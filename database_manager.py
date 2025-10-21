"""
SAPDOCAI Database Manager
Handles database connections and operations for analysis results
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import mysql.connector
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.mysql_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER', 'sapdocai_user'),
            'password': os.getenv('MYSQL_PASSWORD', 'sapdocai_pass'),
            'database': os.getenv('MYSQL_DATABASE', 'sapdocai_db')
        }
        
        self.postgres_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'user': os.getenv('POSTGRES_USER', 'sapdocai_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'sapdocai_pass'),
            'database': os.getenv('POSTGRES_DATABASE', 'sapdocai_pg')
        }
        
        self.redis_config = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', 6379)),
            'db': int(os.getenv('REDIS_DB', 0))
        }
    
    @contextmanager
    def get_mysql_connection(self):
        """Get MySQL database connection"""
        conn = None
        try:
            conn = mysql.connector.connect(**self.mysql_config)
            yield conn
        except Exception as e:
            logger.error(f"MySQL connection error: {e}")
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    @contextmanager
    def get_postgres_connection(self):
        """Get PostgreSQL database connection"""
        conn = None
        try:
            conn = psycopg2.connect(**self.postgres_config)
            yield conn
        except Exception as e:
            logger.error(f"PostgreSQL connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def save_analysis_results(self, analysis_data: Dict[str, Any], db_type: str = 'mysql') -> int:
        """Save analysis results to database"""
        try:
            if db_type == 'mysql':
                return self._save_to_mysql(analysis_data)
            elif db_type == 'postgres':
                return self._save_to_postgres(analysis_data)
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")
            raise
    
    def _save_to_mysql(self, analysis_data: Dict[str, Any]) -> int:
        """Save analysis results to MySQL"""
        with self.get_mysql_connection() as conn:
            cursor = conn.cursor()
            
            # Insert analysis result
            cursor.execute("""
                INSERT INTO analysis_results 
                (project_name, total_files, java_classes, sapui5_views, database_accesses, rest_endpoints, bls_steps, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                analysis_data.get('project_name', 'Unknown'),
                analysis_data.get('total_files', 0),
                analysis_data.get('java_classes', 0),
                analysis_data.get('sapui5_views', 0),
                analysis_data.get('database_accesses', 0),
                analysis_data.get('rest_endpoints', 0),
                analysis_data.get('bls_steps', 0),
                'completed'
            ))
            
            analysis_id = cursor.lastrowid
            
            # Save detailed data
            self._save_java_classes_mysql(cursor, analysis_id, analysis_data.get('java_classes_data', []))
            self._save_sapui5_components_mysql(cursor, analysis_id, analysis_data.get('sapui5_components', []))
            self._save_database_accesses_mysql(cursor, analysis_id, analysis_data.get('database_accesses_data', []))
            self._save_rest_endpoints_mysql(cursor, analysis_id, analysis_data.get('rest_endpoints_data', []))
            self._save_bls_steps_mysql(cursor, analysis_id, analysis_data.get('bls_steps_data', []))
            self._save_relationships_mysql(cursor, analysis_id, analysis_data.get('relationships', []))
            
            conn.commit()
            return analysis_id
    
    def _save_to_postgres(self, analysis_data: Dict[str, Any]) -> int:
        """Save analysis results to PostgreSQL"""
        with self.get_postgres_connection() as conn:
            cursor = conn.cursor()
            
            # Insert analysis result
            cursor.execute("""
                INSERT INTO analysis_results 
                (project_name, total_files, java_classes, sapui5_views, database_accesses, rest_endpoints, bls_steps, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                analysis_data.get('project_name', 'Unknown'),
                analysis_data.get('total_files', 0),
                analysis_data.get('java_classes', 0),
                analysis_data.get('sapui5_views', 0),
                analysis_data.get('database_accesses', 0),
                analysis_data.get('rest_endpoints', 0),
                analysis_data.get('bls_steps', 0),
                'completed'
            ))
            
            analysis_id = cursor.fetchone()[0]
            
            # Save detailed data
            self._save_java_classes_postgres(cursor, analysis_id, analysis_data.get('java_classes_data', []))
            self._save_sapui5_components_postgres(cursor, analysis_id, analysis_data.get('sapui5_components', []))
            self._save_database_accesses_postgres(cursor, analysis_id, analysis_data.get('database_accesses_data', []))
            self._save_rest_endpoints_postgres(cursor, analysis_id, analysis_data.get('rest_endpoints_data', []))
            self._save_bls_steps_postgres(cursor, analysis_id, analysis_data.get('bls_steps_data', []))
            self._save_relationships_postgres(cursor, analysis_id, analysis_data.get('relationships', []))
            
            conn.commit()
            return analysis_id
    
    def _save_java_classes_mysql(self, cursor, analysis_id: int, java_classes: List[Dict]):
        """Save Java classes to MySQL"""
        for class_data in java_classes:
            cursor.execute("""
                INSERT INTO java_classes 
                (analysis_id, class_name, file_path, package_name, methods_count, complexity_score)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                analysis_id,
                class_data.get('name', ''),
                class_data.get('file_path', ''),
                class_data.get('package', ''),
                class_data.get('methods_count', 0),
                class_data.get('complexity_score', 0)
            ))
    
    def _save_java_classes_postgres(self, cursor, analysis_id: int, java_classes: List[Dict]):
        """Save Java classes to PostgreSQL"""
        for class_data in java_classes:
            cursor.execute("""
                INSERT INTO java_classes 
                (analysis_id, class_name, file_path, package_name, methods_count, complexity_score)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                analysis_id,
                class_data.get('name', ''),
                class_data.get('file_path', ''),
                class_data.get('package', ''),
                class_data.get('methods_count', 0),
                class_data.get('complexity_score', 0)
            ))
    
    def _save_sapui5_components_mysql(self, cursor, analysis_id: int, components: List[Dict]):
        """Save SAPUI5 components to MySQL"""
        for component in components:
            cursor.execute("""
                INSERT INTO sapui5_components 
                (analysis_id, component_type, component_name, file_path, functions_count, event_handlers_count, api_calls_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                analysis_id,
                component.get('type', ''),
                component.get('name', ''),
                component.get('file_path', ''),
                component.get('functions_count', 0),
                component.get('event_handlers_count', 0),
                component.get('api_calls_count', 0)
            ))
    
    def _save_sapui5_components_postgres(self, cursor, analysis_id: int, components: List[Dict]):
        """Save SAPUI5 components to PostgreSQL"""
        for component in components:
            cursor.execute("""
                INSERT INTO sapui5_components 
                (analysis_id, component_type, component_name, file_path, functions_count, event_handlers_count, api_calls_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                analysis_id,
                component.get('type', ''),
                component.get('name', ''),
                component.get('file_path', ''),
                component.get('functions_count', 0),
                component.get('event_handlers_count', 0),
                component.get('api_calls_count', 0)
            ))
    
    def _save_database_accesses_mysql(self, cursor, analysis_id: int, accesses: List[Dict]):
        """Save database accesses to MySQL"""
        for access in accesses:
            cursor.execute("""
                INSERT INTO database_accesses 
                (analysis_id, access_type, pattern_matched, file_path, line_number, context)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                analysis_id,
                access.get('type', ''),
                access.get('match', ''),
                access.get('file_path', ''),
                access.get('line', 0),
                access.get('context', '')
            ))
    
    def _save_database_accesses_postgres(self, cursor, analysis_id: int, accesses: List[Dict]):
        """Save database accesses to PostgreSQL"""
        for access in accesses:
            cursor.execute("""
                INSERT INTO database_accesses 
                (analysis_id, access_type, pattern_matched, file_path, line_number, context)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                analysis_id,
                access.get('type', ''),
                access.get('match', ''),
                access.get('file_path', ''),
                access.get('line', 0),
                access.get('context', '')
            ))
    
    def _save_rest_endpoints_mysql(self, cursor, analysis_id: int, endpoints: List[Dict]):
        """Save REST endpoints to MySQL"""
        for endpoint in endpoints:
            cursor.execute("""
                INSERT INTO rest_endpoints 
                (analysis_id, endpoint_path, http_method, file_path, line_number, context)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                analysis_id,
                endpoint.get('path', ''),
                endpoint.get('method', 'GET'),
                endpoint.get('file_path', ''),
                endpoint.get('line', 0),
                endpoint.get('context', '')
            ))
    
    def _save_rest_endpoints_postgres(self, cursor, analysis_id: int, endpoints: List[Dict]):
        """Save REST endpoints to PostgreSQL"""
        for endpoint in endpoints:
            cursor.execute("""
                INSERT INTO rest_endpoints 
                (analysis_id, endpoint_path, http_method, file_path, line_number, context)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                analysis_id,
                endpoint.get('path', ''),
                endpoint.get('method', 'GET'),
                endpoint.get('file_path', ''),
                endpoint.get('line', 0),
                endpoint.get('context', '')
            ))
    
    def _save_bls_steps_mysql(self, cursor, analysis_id: int, steps: List[Dict]):
        """Save BLS steps to MySQL"""
        for step in steps:
            cursor.execute("""
                INSERT INTO bls_steps 
                (analysis_id, step_name, step_type, file_path, line_number, context)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                analysis_id,
                step.get('step', ''),
                step.get('type', ''),
                step.get('file_path', ''),
                step.get('line', 0),
                step.get('context', '')
            ))
    
    def _save_bls_steps_postgres(self, cursor, analysis_id: int, steps: List[Dict]):
        """Save BLS steps to PostgreSQL"""
        for step in steps:
            cursor.execute("""
                INSERT INTO bls_steps 
                (analysis_id, step_name, step_type, file_path, line_number, context)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                analysis_id,
                step.get('step', ''),
                step.get('type', ''),
                step.get('file_path', ''),
                step.get('line', 0),
                step.get('context', '')
            ))
    
    def _save_relationships_mysql(self, cursor, analysis_id: int, relationships: List[Dict]):
        """Save relationships to MySQL"""
        for rel in relationships:
            cursor.execute("""
                INSERT INTO analysis_relationships 
                (analysis_id, source_component, target_component, relationship_type)
                VALUES (%s, %s, %s, %s)
            """, (
                analysis_id,
                rel.get('source', ''),
                rel.get('target', ''),
                rel.get('type', '')
            ))
    
    def _save_relationships_postgres(self, cursor, analysis_id: int, relationships: List[Dict]):
        """Save relationships to PostgreSQL"""
        for rel in relationships:
            cursor.execute("""
                INSERT INTO analysis_relationships 
                (analysis_id, source_component, target_component, relationship_type)
                VALUES (%s, %s, %s, %s)
            """, (
                analysis_id,
                rel.get('source', ''),
                rel.get('target', ''),
                rel.get('type', '')
            ))
    
    def get_analysis_results(self, project_name: str = None, db_type: str = 'mysql') -> List[Dict]:
        """Get analysis results from database"""
        try:
            if db_type == 'mysql':
                return self._get_from_mysql(project_name)
            elif db_type == 'postgres':
                return self._get_from_postgres(project_name)
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
        except Exception as e:
            logger.error(f"Error getting analysis results: {e}")
            raise
    
    def _get_from_mysql(self, project_name: str = None) -> List[Dict]:
        """Get analysis results from MySQL"""
        with self.get_mysql_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            if project_name:
                cursor.execute("SELECT * FROM analysis_results WHERE project_name = %s ORDER BY analysis_date DESC", (project_name,))
            else:
                cursor.execute("SELECT * FROM analysis_results ORDER BY analysis_date DESC")
            
            return cursor.fetchall()
    
    def _get_from_postgres(self, project_name: str = None) -> List[Dict]:
        """Get analysis results from PostgreSQL"""
        with self.get_postgres_connection() as conn:
            cursor = conn.cursor()
            
            if project_name:
                cursor.execute("SELECT * FROM analysis_results WHERE project_name = %s ORDER BY analysis_date DESC", (project_name,))
            else:
                cursor.execute("SELECT * FROM analysis_results ORDER BY analysis_date DESC")
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results

# Global database manager instance
db_manager = DatabaseManager()
