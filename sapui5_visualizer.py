"""
SAPUI5 Advanced Visualizer
- Database/API Relationship Visualization
- UI Screen Preview Generator
- API Endpoint Map
- Data Flow Diagram
"""
from pathlib import Path
import json
import re
from typing import Dict, List, Any, Set, Tuple
import xml.etree.ElementTree as ET

class SAPUI5Visualizer:
    """Advanced visualization for SAPUI5 projects"""
    
    def __init__(self, project_root: Path):
        self.root = project_root
        self.api_endpoints = []
        self.database_tables = set()
        self.ui_screens = []
        self.data_flows = []
        
    def analyze_all(self) -> Dict[str, Any]:
        """Run all analyses"""
        return {
            "api_map": self.extract_api_endpoints(),
            "database_schema": self.extract_database_info(),
            "ui_screens": self.extract_ui_screens(),
            "data_flows": self.extract_data_flows()
        }
    
    def extract_api_endpoints(self) -> Dict[str, Any]:
        """Extract all API endpoints and their relationships"""
        endpoints = {
            "rest_apis": [],
            "odata_services": [],
            "websocket_connections": [],
            "mqtt_topics": []
        }
        
        for js_file in self.root.rglob("*.js"):
            if 'controller' in str(js_file).lower():
                content = js_file.read_text(encoding='utf-8', errors='ignore')
                
                # REST API endpoints
                rest_patterns = [
                    r'["\']/([\w/]+Controller/[\w]+)["\']',
                    r'endPoint\s*=\s*["\']([^"\']+)["\']',
                    r'url:\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in rest_patterns:
                    for match in re.finditer(pattern, content):
                        endpoint = match.group(1)
                        if endpoint not in [e['path'] for e in endpoints['rest_apis']]:
                            # Determine method
                            method = 'GET'
                            if 'asyncPOST' in content[max(0, match.start()-100):match.start()]:
                                method = 'POST'
                            elif 'asyncGET' in content[max(0, match.start()-100):match.start()]:
                                method = 'GET'
                            
                            endpoints['rest_apis'].append({
                                'path': endpoint,
                                'method': method,
                                'file': str(js_file.name),
                                'line': content[:match.start()].count('\n') + 1
                            })
                
                # WebSocket/MQTT
                if 'WebSocket' in content or 'MQTT' in content:
                    mqtt_pattern = r'subscribe\(["\']([^"\']+)["\']'
                    for match in re.finditer(mqtt_pattern, content):
                        topic = match.group(1)
                        endpoints['mqtt_topics'].append({
                            'topic': topic,
                            'file': str(js_file.name)
                        })
        
        return endpoints
    
    def extract_database_info(self) -> Dict[str, Any]:
        """Extract database tables and relationships from code"""
        db_info = {
            "tables": [],
            "relationships": [],
            "queries": []
        }
        
        # Common SAP ME table patterns
        table_patterns = [
            r'["\'](\w+_T)["\']',  # SAP tables ending with _T
            r'FROM\s+(\w+)',  # SQL FROM
            r'JOIN\s+(\w+)',  # SQL JOIN
            r'TABLE\s*=\s*["\'](\w+)["\']',
            r'tableName:\s*["\'](\w+)["\']'
        ]
        
        for js_file in self.root.rglob("*.js"):
            content = js_file.read_text(encoding='utf-8', errors='ignore')
            
            for pattern in table_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    table_name = match.group(1)
                    if len(table_name) > 3 and table_name.upper() == table_name:
                        if table_name not in [t['name'] for t in db_info['tables']]:
                            db_info['tables'].append({
                                'name': table_name,
                                'source_file': str(js_file.name)
                            })
        
        # Extract relationships from foreign keys or JOIN patterns
        for js_file in self.root.rglob("*.js"):
            content = js_file.read_text(encoding='utf-8', errors='ignore')
            
            # Look for JOIN patterns
            join_pattern = r'(\w+)\s+(?:INNER\s+)?JOIN\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)'
            for match in re.finditer(join_pattern, content, re.IGNORECASE):
                db_info['relationships'].append({
                    'from_table': match.group(1),
                    'to_table': match.group(2),
                    'from_column': match.group(4),
                    'to_column': match.group(6),
                    'type': 'JOIN'
                })
        
        return db_info
    
    def extract_ui_screens(self) -> List[Dict[str, Any]]:
        """Extract UI screen structure from View XML files"""
        screens = []
        
        for xml_file in self.root.rglob("*.xml"):
            if 'view' in str(xml_file).lower() and 'fragment' not in str(xml_file).lower():
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    
                    screen = {
                        'name': xml_file.stem,
                        'file': str(xml_file.name),
                        'layout': self._extract_layout(root),
                        'controls': self._extract_controls(root),
                        'fragments': self._extract_fragments(root)
                    }
                    
                    screens.append(screen)
                except Exception as e:
                    pass
        
        return screens
    
    def _extract_layout(self, root) -> Dict[str, Any]:
        """Extract layout information from XML"""
        layout = {
            'type': 'Unknown',
            'sections': []
        }
        
        # Detect layout type
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag in ['Page', 'Panel', 'VBox', 'HBox', 'Grid', 'Form']:
                layout['type'] = tag
                break
        
        return layout
    
    def _extract_controls(self, root) -> List[Dict[str, Any]]:
        """Extract UI controls from XML"""
        controls = []
        
        control_types = ['Button', 'Input', 'Table', 'List', 'Select', 'ComboBox', 
                        'DatePicker', 'CheckBox', 'RadioButton', 'Text', 'Label',
                        'IconTabBar', 'Dialog', 'Popover']
        
        for elem in root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if tag in control_types:
                control = {
                    'type': tag,
                    'id': elem.get('id', ''),
                    'text': elem.get('text', elem.get('title', '')),
                    'press': elem.get('press', ''),
                    'visible': elem.get('visible', 'true')
                }
                
                # Tablo için özel bilgiler
                if tag == 'Table':
                    control['items'] = elem.get('items', '')
                    control['model'] = elem.get('items', '').split('/')[0] if '/' in elem.get('items', '') else ''
                    
                    # Tablo sütunlarını say
                    columns = list(elem.iter())
                    column_count = len([col for col in columns if col.tag.split('}')[-1] == 'Column'])
                    control['column_count'] = column_count
                
                controls.append(control)
        
        return controls
    
    def _extract_fragments(self, root) -> List[str]:
        """Extract fragment references"""
        fragments = []
        
        for elem in root.iter():
            if 'Fragment' in elem.tag:
                frag_name = elem.get('fragmentName', '')
                if frag_name:
                    fragments.append(frag_name)
        
        return fragments
    
    def extract_data_flows(self) -> List[Dict[str, Any]]:
        """Extract data flow between components"""
        flows = []
        
        # Map controllers to their API calls
        controller_apis = {}
        
        for js_file in self.root.rglob("*.js"):
            if 'controller' in str(js_file).lower():
                content = js_file.read_text(encoding='utf-8', errors='ignore')
                controller_name = js_file.stem
                
                # Find API calls in this controller
                api_calls = []
                endpoint_pattern = r'endPoint\s*=\s*["\']([^"\']+)["\']'
                for match in re.finditer(endpoint_pattern, content):
                    api_calls.append(match.group(1))
                
                if api_calls:
                    controller_apis[controller_name] = api_calls
        
        # Create flow diagram
        for controller, apis in controller_apis.items():
            for api in apis:
                flows.append({
                    'from': controller,
                    'to': api,
                    'type': 'API_CALL',
                    'method': 'POST' if 'POST' in api else 'GET'
                })
        
        return flows
    
    def generate_mermaid_api_map(self, api_data: Dict[str, Any]) -> str:
        """Generate Mermaid diagram for API endpoints"""
        lines = ["```mermaid", "graph LR"]
        
        # REST APIs
        if api_data['rest_apis']:
            lines.append("    subgraph REST_APIs")
            for i, api in enumerate(api_data['rest_apis'][:20]):  # Limit to 20
                api_id = f"API{i}"
                method_color = "fill:#90EE90" if api['method'] == 'GET' else "fill:#FFB6C1"
                lines.append(f"        {api_id}[\"{api['method']}: {api['path']}\"]")
                lines.append(f"        style {api_id} {method_color}")
            lines.append("    end")
        
        # MQTT Topics
        if api_data['mqtt_topics']:
            lines.append("    subgraph MQTT_Topics")
            for i, mqtt in enumerate(api_data['mqtt_topics'][:10]):
                mqtt_id = f"MQTT{i}"
                lines.append(f"        {mqtt_id}[\"{mqtt['topic']}\"]")
                lines.append(f"        style {mqtt_id} fill:#FFE4B5")
            lines.append("    end")
        
        lines.append("```")
        return "\n".join(lines)
    
    def generate_mermaid_database_erd(self, db_data: Dict[str, Any]) -> str:
        """Generate Mermaid ERD for database tables"""
        lines = ["```mermaid", "erDiagram"]
        
        # Add tables
        for table in db_data['tables'][:15]:  # Limit to 15 tables
            lines.append(f"    {table['name']} {{")
            lines.append(f"        string id PK")
            lines.append(f"        string data")
            lines.append(f"    }}")
        
        # Add relationships
        for rel in db_data['relationships'][:20]:
            lines.append(f"    {rel['from_table']} ||--o{{ {rel['to_table']} : {rel['type']}")
        
        lines.append("```")
        return "\n".join(lines)
    
    def generate_mermaid_data_flow(self, flow_data: List[Dict[str, Any]]) -> str:
        """Generate Mermaid diagram for data flow"""
        lines = ["```mermaid", "graph TD"]
        
        # Group by controller
        controllers = set([f['from'] for f in flow_data])
        
        for controller in list(controllers)[:10]:  # Limit to 10 controllers
            ctrl_id = controller.replace('.', '_')
            lines.append(f"    {ctrl_id}[{controller}]")
            lines.append(f"    style {ctrl_id} fill:#87CEEB")
            
            # Add API calls from this controller
            apis = [f for f in flow_data if f['from'] == controller]
            for i, api in enumerate(apis[:5]):  # Max 5 APIs per controller
                api_id = f"{ctrl_id}_API{i}"
                api_path = api['to'].split('/')[-1][:20]  # Shorten path
                lines.append(f"    {api_id}[{api_path}]")
                lines.append(f"    {ctrl_id} -->|{api['method']}| {api_id}")
                lines.append(f"    style {api_id} fill:#98FB98")
        
        lines.append("```")
        return "\n".join(lines)
    
    def generate_ui_preview_html(self, screen_data: Dict[str, Any]) -> str:
        """Generate HTML preview of UI screen"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{screen_data['name']} - UI Preview</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
        .screen {{ background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; max-width: 800px; margin: 0 auto; }}
        .header {{ background: #0070f3; color: white; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
        .control {{ margin: 10px 0; padding: 10px; border: 1px solid #e0e0e0; border-radius: 4px; }}
        .button {{ background: #0070f3; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }}
        .input {{ padding: 8px; border: 1px solid #ddd; border-radius: 4px; width: 100%; }}
        .table {{ width: 100%; border-collapse: collapse; }}
        .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .table th {{ background: #f0f0f0; }}
        .fragment {{ background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="screen">
        <div class="header">
            <h1>{screen_data['name']}</h1>
            <p>Layout: {screen_data['layout']['type']}</p>
        </div>
        
        <h2>UI Controls ({len(screen_data['controls'])})</h2>
"""
        
        # Add controls
        for control in screen_data['controls'][:20]:  # Limit to 20
            if control['type'] == 'Button':
                html += f"""
        <div class="control">
            <button class="button" onclick="alert('Event: {control['press']}')">{control['text'] or 'Button'}</button>
            <small>ID: {control['id']}</small>
        </div>
"""
            elif control['type'] == 'Input':
                html += f"""
        <div class="control">
            <label>{control['text'] or 'Input Field'}</label>
            <input type="text" class="input" placeholder="{control['id']}" />
        </div>
"""
            elif control['type'] == 'Table':
                # Tablo ismini ve ID'sini göster
                table_name = control.get('id', 'Unknown Table')
                table_text = control.get('text', '')
                display_name = f"{table_name}" if table_text else f"{table_name}"
                
                # Tablo detayları
                model_info = f"Model: {control.get('model', 'No Model')}" if control.get('model') else ""
                column_info = f"Columns: {control.get('column_count', 0)}" if control.get('column_count') else ""
                
                html += f"""
        <div class="control">
            <h3>📊 {display_name}</h3>
            <p><strong>ID:</strong> {control.get('id', 'No ID')}</p>
            {f'<p><strong>{model_info}</strong></p>' if model_info else ''}
            {f'<p><strong>{column_info}</strong></p>' if column_info else ''}
            <table class="table">
                <thead><tr><th>Column 1</th><th>Column 2</th><th>Column 3</th></tr></thead>
                <tbody>
                    <tr><td>Data</td><td>Data</td><td>Data</td></tr>
                    <tr><td>Data</td><td>Data</td><td>Data</td></tr>
                </tbody>
            </table>
        </div>
"""
        
        # Add fragments
        if screen_data['fragments']:
            html += "<h2>Fragments</h2>"
            for fragment in screen_data['fragments']:
                html += f'<div class="fragment">📦 {fragment}</div>'
        
        html += """
    </div>
</body>
</html>
"""
        return html


def main():
    """Test the visualizer"""
    import sys
    if len(sys.argv) < 2:
        print("Usage: python sapui5_visualizer.py <project_path>")
        return
    
    project_path = Path(sys.argv[1])
    visualizer = SAPUI5Visualizer(project_path)
    
    print("Analyzing SAPUI5 project...")
    results = visualizer.analyze_all()
    
    # Save results
    output_dir = Path("./visualization_output")
    output_dir.mkdir(exist_ok=True)
    
    # API Map
    api_mermaid = visualizer.generate_mermaid_api_map(results['api_map'])
    (output_dir / "api_map.mmd").write_text(api_mermaid, encoding='utf-8')
    
    # Database ERD
    db_mermaid = visualizer.generate_mermaid_database_erd(results['database_schema'])
    (output_dir / "database_erd.mmd").write_text(db_mermaid, encoding='utf-8')
    
    # Data Flow
    flow_mermaid = visualizer.generate_mermaid_data_flow(results['data_flows'])
    (output_dir / "data_flow.mmd").write_text(flow_mermaid, encoding='utf-8')
    
    # UI Previews
    for screen in results['ui_screens'][:5]:  # First 5 screens
        html = visualizer.generate_ui_preview_html(screen)
        (output_dir / f"{screen['name']}_preview.html").write_text(html, encoding='utf-8')
    
    # JSON output
    (output_dir / "visualization_data.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    
    print(f"Visualization complete! Output: {output_dir.resolve()}")
    print(f"   - API Map: {len(results['api_map']['rest_apis'])} endpoints")
    print(f"   - Database: {len(results['database_schema']['tables'])} tables")
    print(f"   - UI Screens: {len(results['ui_screens'])} screens")
    print(f"   - Data Flows: {len(results['data_flows'])} flows")


if __name__ == '__main__':
    main()
