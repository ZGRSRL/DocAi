"""
Network Visualization Module for SAPDOCAI
Creates interactive network visualizations using Pyvis and NetworkX
"""

import networkx as nx
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from pyvis.network import Network
import streamlit as st
import streamlit.components.v1 as components


class NetworkVisualizer:
    """Creates interactive network visualizations from NetworkX graphs"""
    
    def __init__(self, width: str = "100%", height: str = "600px"):
        self.width = width
        self.height = height
        self.net = None
        
    def create_interactive_network(self, graph_data: Dict[str, Any], 
                                 output_path: Path) -> str:
        """
        Create interactive network visualization from graph.json data
        
        Args:
            graph_data: JSON data from graph.json file
            output_path: Path to save the HTML file
            
        Returns:
            Path to the generated HTML file
        """
        # Initialize Pyvis network
        self.net = Network(
            height=self.height,
            width=self.width,
            bgcolor="#ffffff",
            font_color="#333333",
            directed=True
        )
        
        # Configure physics
        self.net.set_options("""
        {
            "physics": {
                "enabled": true,
                "stabilization": {"iterations": 100},
                "barnesHut": {
                    "gravitationalConstant": -2000,
                    "centralGravity": 0.1,
                    "springLength": 95,
                    "springConstant": 0.04,
                    "damping": 0.09
                }
            },
            "interaction": {
                "hover": true,
                "tooltipDelay": 200,
                "hideEdgesOnDrag": false
            },
            "nodes": {
                "font": {"size": 14, "color": "#333333"},
                "borderWidth": 2,
                "shadow": true
            },
            "edges": {
                "font": {"size": 12, "color": "#666666"},
                "shadow": true,
                "smooth": {"type": "continuous"}
            }
        }
        """)
        
        # Add nodes and edges
        self._add_nodes_and_edges(graph_data)
        
        # Save HTML file
        html_file = output_path / "interactive_network.html"
        self.net.save_graph(str(html_file))
        
        return str(html_file)
    
    def _add_nodes_and_edges(self, graph_data: Dict[str, Any]):
        """Add nodes and edges to the network"""
        nodes_added = set()
        
        # Handle different JSON structures
        if isinstance(graph_data, list):
            # If graph_data is a list, treat it as edges directly
            edges = graph_data
        elif isinstance(graph_data, dict):
            # If graph_data is a dict, look for edges key
            edges = graph_data.get('edges', [])
        else:
            st.error(f"Unexpected graph_data type: {type(graph_data)}")
            return
        
        # Ensure edges is a list
        if not isinstance(edges, list):
            st.error(f"Edges should be a list, got: {type(edges)}")
            return
        
        for edge in edges:
            # Handle different edge formats
            if isinstance(edge, dict):
                # Check for different field names
                source = edge.get('source', edge.get('src', ''))
                target = edge.get('target', edge.get('dst', ''))
                relation_type = edge.get('relation', edge.get('type', ''))
            elif isinstance(edge, list) and len(edge) >= 2:
                # Handle tuple-like format [source, target, relation]
                source = str(edge[0]) if len(edge) > 0 else ''
                target = str(edge[1]) if len(edge) > 1 else ''
                relation_type = str(edge[2]) if len(edge) > 2 else ''
            else:
                continue
            
            if not source or not target:
                continue
                
            # Add source node
            if source not in nodes_added:
                self._add_node(source, self._get_node_type(source))
                nodes_added.add(source)
            
            # Add target node
            if target not in nodes_added:
                self._add_node(target, self._get_node_type(target))
                nodes_added.add(target)
            
            # Add edge
            self._add_edge(source, target, relation_type)
    
    def _add_node(self, node_id: str, node_type: str):
        """Add a node to the network"""
        # Determine node properties based on type
        color, shape, size = self._get_node_properties(node_type)
        
        # Create tooltip with node information
        tooltip = f"""
        <div style="font-family: Arial; font-size: 12px;">
            <b>{node_id}</b><br>
            <i>Type: {node_type}</i>
        </div>
        """
        
        self.net.add_node(
            node_id,
            label=node_id,
            color=color,
            shape=shape,
            size=size,
            title=tooltip
        )
    
    def _add_edge(self, source: str, target: str, relation_type: str):
        """Add an edge to the network"""
        # Determine edge properties based on relation type
        color, width, dashes = self._get_edge_properties(relation_type)
        
        # Create tooltip
        tooltip = f"<b>{relation_type}</b><br>From: {source}<br>To: {target}"
        
        self.net.add_edge(
            source,
            target,
            label=relation_type,
            color=color,
            width=width,
            dashes=dashes,
            title=tooltip
        )
    
    def _get_node_type(self, node_id: str) -> str:
        """Determine node type based on node ID"""
        node_lower = node_id.lower()
        
        if '.java' in node_lower or 'service' in node_lower:
            return 'java_class'
        elif '.xml' in node_lower or 'bls' in node_lower:
            return 'xml_component'
        elif 'http' in node_lower or 'api' in node_lower:
            return 'endpoint'
        elif 'sql' in node_lower or 'jdbc' in node_lower:
            return 'database'
        elif '.properties' in node_lower or 'config' in node_lower:
            return 'config'
        else:
            return 'generic'
    
    def _get_node_properties(self, node_type: str) -> tuple:
        """Get node properties based on type"""
        properties = {
            'java_class': ('#4CAF50', 'box', 25),      # Green box
            'xml_component': ('#2196F3', 'diamond', 20), # Blue diamond
            'endpoint': ('#FF9800', 'triangle', 22),    # Orange triangle
            'database': ('#9C27B0', 'circle', 24),      # Purple circle
            'config': ('#607D8B', 'square', 18),         # Blue-grey square
            'generic': ('#795548', 'ellipse', 20)        # Brown ellipse
        }
        return properties.get(node_type, properties['generic'])
    
    def _get_edge_properties(self, relation_type: str) -> tuple:
        """Get edge properties based on relation type"""
        properties = {
            'SERVICE_EXPOSES_ENDPOINT': ('#4CAF50', 3, False),  # Green solid
            'METHOD_TOUCHES_SQL': ('#9C27B0', 2, False),        # Purple solid
            'SERVICE_CALLS_HTTP': ('#FF9800', 2, False),       # Orange solid
            'BLS_CALLS_TARGET': ('#2196F3', 2, True),           # Blue dashed
            'CFG_URL': ('#607D8B', 1, True),                   # Grey dashed
            'CFG_DSN': ('#795548', 1, True),                    # Brown dashed
            'SOAP_DEF': ('#E91E63', 2, False),                  # Pink solid
            'BLS_PARAM': ('#00BCD4', 1, True)                   # Cyan dashed
        }
        return properties.get(relation_type, ('#666666', 1, False))


def create_network_visualization(graph_json_path: Path, output_path: Path) -> str:
    """
    Create interactive network visualization from graph.json
    
    Args:
        graph_json_path: Path to graph.json file
        output_path: Path to save HTML output
        
    Returns:
        Path to generated HTML file
    """
    try:
        # Load graph data
        with open(graph_json_path, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        
        # Create visualizer
        visualizer = NetworkVisualizer()
        
        # Generate interactive network
        html_file = visualizer.create_interactive_network(graph_data, output_path)
        
        return html_file
        
    except Exception as e:
        st.error(f"Network visualization error: {str(e)}")
        return None


def display_interactive_network(html_file_path: str):
    """
    Display interactive network in Streamlit
    
    Args:
        html_file_path: Path to HTML file
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Display in Streamlit
        components.html(html_content, height=600, scrolling=True)
        
    except Exception as e:
        st.error(f"Error displaying network: {str(e)}")


def create_summary_statistics(graph_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create summary statistics from graph data
    
    Args:
        graph_data: JSON data from graph.json
        
    Returns:
        Dictionary with statistics
    """
    # Handle different JSON structures
    if isinstance(graph_data, list):
        edges = graph_data
    elif isinstance(graph_data, dict):
        edges = graph_data.get('edges', [])
    else:
        return {
            'total_edges': 0,
            'node_types': {},
            'relation_types': {},
            'unique_nodes': 0
        }
    
    # Count nodes by type
    node_types = {}
    relation_types = {}
    
    for edge in edges:
        # Handle different edge formats
        if isinstance(edge, dict):
            # Check for different field names
            source = edge.get('source', edge.get('src', ''))
            target = edge.get('target', edge.get('dst', ''))
            relation = edge.get('relation', edge.get('type', ''))
        elif isinstance(edge, list) and len(edge) >= 2:
            source = str(edge[0]) if len(edge) > 0 else ''
            target = str(edge[1]) if len(edge) > 1 else ''
            relation = str(edge[2]) if len(edge) > 2 else ''
        else:
            continue
        
        # Count relation types
        if relation:
            relation_types[relation] = relation_types.get(relation, 0) + 1
        
        # Determine node types
        if source:
            source_type = _get_node_type_from_id(source)
            node_types[source_type] = node_types.get(source_type, 0) + 1
        
        if target:
            target_type = _get_node_type_from_id(target)
            node_types[target_type] = node_types.get(target_type, 0) + 1
    
    return {
        'total_edges': len(edges),
        'node_types': node_types,
        'relation_types': relation_types,
        'unique_nodes': len(set([str(edge[0]) if isinstance(edge, list) and len(edge) > 0 else edge.get('source', '') for edge in edges] + 
                              [str(edge[1]) if isinstance(edge, list) and len(edge) > 1 else edge.get('target', '') for edge in edges]))
    }


def _get_node_type_from_id(node_id: str) -> str:
    """Helper function to determine node type"""
    node_lower = node_id.lower()
    
    if '.java' in node_lower or 'service' in node_lower:
        return 'Java Classes'
    elif '.xml' in node_lower or 'bls' in node_lower:
        return 'XML Components'
    elif 'http' in node_lower or 'api' in node_lower:
        return 'Endpoints'
    elif 'sql' in node_lower or 'jdbc' in node_lower:
        return 'Database'
    elif '.properties' in node_lower or 'config' in node_lower:
        return 'Config Files'
    else:
        return 'Other Components'
