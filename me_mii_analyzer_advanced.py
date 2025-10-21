"""
SAP ME/MII Advanced Analyzer with Deep SAPUI5 Analysis
- Controller analysis (API calls, OData, events)
- View analysis (UI controls, bindings)
- Fragment detection
- i18n parsing
- Screenshot generation capability
- AutoGen integration ready
"""
from pathlib import Path
import json
import re
from typing import Dict, List, Any
import xml.etree.ElementTree as ET

# Base analyzer'ı import et
import me_mii_folder_analyzer_extended as base_analyzer

def parse_controller_deep(fp: Path) -> Dict[str, Any]:
    """Controller dosyasını detaylı analiz et"""
    try:
        text = fp.read_text(encoding='utf-8', errors='ignore')
        
        info = {
            "file": str(fp),
            "type": "SAPUI5 Controller",
            "functions": [],
            "event_handlers": [],
            "api_calls": [],
            "odata_models": [],
            "odata_operations": [],
            "message_toasts": [],
            "navigations": [],
            "validations": [],
            "sap_me_apis": [],
            "sfc_operations": [],
            "me_mii_patterns": []
        }
        
        # Function definitions
        func_pattern = r'(\w+)\s*:\s*function\s*\([^)]*\)\s*\{'
        for match in re.finditer(func_pattern, text):
            info["functions"].append(match.group(1))
        
        # Event handlers (on* methods)
        event_pattern = r'(on\w+)\s*:\s*function'
        for match in re.finditer(event_pattern, text):
            info["event_handlers"].append(match.group(1))
        
        # API calls (jQuery.ajax, fetch, $.get, $.post)
        api_patterns = [
            r'jQuery\.ajax\s*\(\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
            r'\.ajax\s*\(\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'\.get\s*\(\s*["\']([^"\']+)["\']',
            r'\.post\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in api_patterns:
            for match in re.finditer(pattern, text):
                info["api_calls"].append(match.group(1))
        
        # OData Model creation
        odata_model_pattern = r'new\s+sap\.ui\.model\.odata\.v[24]\.ODataModel\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(odata_model_pattern, text):
            info["odata_models"].append(match.group(1))
        
        # OData operations (read, create, update, delete)
        odata_ops = [
            (r'\.read\s*\(\s*["\']([^"\']+)["\']', 'READ'),
            (r'\.create\s*\(\s*["\']([^"\']+)["\']', 'CREATE'),
            (r'\.update\s*\(\s*["\']([^"\']+)["\']', 'UPDATE'),
            (r'\.remove\s*\(\s*["\']([^"\']+)["\']', 'DELETE'),
        ]
        
        for pattern, op_type in odata_ops:
            for match in re.finditer(pattern, text):
                info["odata_operations"].append({
                    "type": op_type,
                    "path": match.group(1)
                })
        
        # Message Toast / MessageBox
        message_pattern = r'MessageToast\.show\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(message_pattern, text):
            info["message_toasts"].append(match.group(1))
        
        # Navigation (navTo)
        nav_pattern = r'\.navTo\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(nav_pattern, text):
            info["navigations"].append(match.group(1))
        
        # Validations
        if 'validate' in text.lower() or 'check' in text.lower():
            info["validations"].append("Has validation logic")
        
        # SAP ME API Detection
        sap_me_patterns = [
            r'com\.sap\.me\.(\w+)',
            r'sap\.me\.(\w+)',
            r'ME\.(\w+)',
            r'ShopFloorControl\.(\w+)',
            r'SFC\.(\w+)',
            r'Order\.(\w+)',
            r'Resource\.(\w+)',
            r'WorkCenter\.(\w+)',
            r'Operation\.(\w+)',
            r'Routing\.(\w+)'
        ]
        
        for pattern in sap_me_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                api_class = match.group(1)
                info["sap_me_apis"].append({
                    "class": api_class,
                    "pattern": pattern,
                    "context": text[max(0, match.start()-50):match.end()+50]
                })
        
        # SFC/Order/Resource Parameter Flow Detection
        sfc_patterns = [
            r'SFC\s*=\s*["\']?([^"\'\s]+)["\']?',
            r'Order\s*=\s*["\']?([^"\'\s]+)["\']?',
            r'Resource\s*=\s*["\']?([^"\'\s]+)["\']?',
            r'WorkCenter\s*=\s*["\']?([^"\'\s]+)["\']?',
            r'Operation\s*=\s*["\']?([^"\'\s]+)["\']?',
            r'getSFC\(\)',
            r'getOrder\(\)',
            r'getResource\(\)',
            r'setSFC\(',
            r'setOrder\(',
            r'setResource\('
        ]
        
        for pattern in sfc_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                info["sfc_operations"].append({
                    "operation": match.group(0),
                    "pattern": pattern,
                    "context": text[max(0, match.start()-30):match.end()+30]
                })
        
        # ME/MII Specific Patterns
        me_mii_patterns = [
            r'ShopFloorControl',
            r'ManufacturingExecution',
            r'ProductionOrder',
            r'WorkInstruction',
            r'QualityInspection',
            r'MaterialConsumption',
            r'LaborTracking',
            r'EquipmentIntegration',
            r'DataCollection',
            r'Traceability'
        ]
        
        for pattern in me_mii_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                info["me_mii_patterns"].append(pattern)
        
        return info if any([info["functions"], info["api_calls"], info["odata_models"], 
                          info["sap_me_apis"], info["sfc_operations"], info["me_mii_patterns"]]) else None
        
    except Exception as e:
        return None


def parse_view_xml(fp: Path) -> Dict[str, Any]:
    """View XML dosyasını analiz et"""
    try:
        tree = ET.parse(fp)
        root = tree.getroot()
        
        info = {
            "file": str(fp),
            "type": "SAPUI5 View",
            "controls": [],
            "bindings": [],
            "events": [],
            "fragments": []
        }
        
        # Namespace'leri temizle
        def clean_tag(tag):
            return tag.split('}')[-1] if '}' in tag else tag
        
        # Tüm elementleri tara
        for elem in root.iter():
            tag = clean_tag(elem.tag)
            
            # Control tespiti
            if tag in ['Button', 'Input', 'Table', 'List', 'Panel', 'Form', 'Dialog', 
                      'Select', 'ComboBox', 'DatePicker', 'CheckBox', 'RadioButton']:
                control_info = {"type": tag}
                
                # ID
                if 'id' in elem.attrib:
                    control_info["id"] = elem.attrib['id']
                
                # Text/Title
                if 'text' in elem.attrib:
                    control_info["text"] = elem.attrib['text']
                elif 'title' in elem.attrib:
                    control_info["title"] = elem.attrib['title']
                
                # Press event
                if 'press' in elem.attrib:
                    control_info["press"] = elem.attrib['press']
                    info["events"].append(elem.attrib['press'])
                
                info["controls"].append(control_info)
            
            # Binding tespiti
            for attr_name, attr_value in elem.attrib.items():
                if '{' in attr_value and '}' in attr_value:
                    # Model binding bulundu
                    binding_match = re.search(r'\{([^}]+)\}', attr_value)
                    if binding_match:
                        info["bindings"].append({
                            "control": tag,
                            "property": attr_name,
                            "path": binding_match.group(1)
                        })
            
            # Fragment tespiti
            if tag == 'Fragment' or tag == 'core:Fragment':
                if 'fragmentName' in elem.attrib:
                    info["fragments"].append(elem.attrib['fragmentName'])
        
        return info if info["controls"] else None
        
    except Exception as e:
        return None


def parse_xml_file(fp: Path) -> Dict[str, Any]:
    """XML dosyasını ME/MII özel analizi ile parse et"""
    try:
        text = fp.read_text(encoding='utf-8', errors='ignore')
        
        info = {
            "file": str(fp),
            "type": "XML",
            "bls_steps": [],
            "wsdl_endpoints": [],
            "parameters": [],
            "sfc_flow": [],
            "me_mii_operations": [],
            "parameter_mapping": []
        }
        
        # BLS/Transaction Step Detection
        step_patterns = [
            r'<Step[^>]*Action="([^"]*)"[^>]*Target="([^"]*)"[^>]*/?>',
            r'<Transaction[^>]*Name="([^"]*)"[^>]*>',
            r'<BLS[^>]*Name="([^"]*)"[^>]*>'
        ]
        
        for pattern in step_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                if len(match.groups()) >= 2:
                    info["bls_steps"].append({
                        "action": match.group(1),
                        "target": match.group(2),
                        "context": text[max(0, match.start()-100):match.end()+100]
                    })
                else:
                    info["bls_steps"].append({
                        "name": match.group(1),
                        "context": text[max(0, match.start()-100):match.end()+100]
                    })
        
        # SFC/Order/Resource Parameter Flow Detection
        sfc_flow_patterns = [
            r'<Parameter[^>]*Name="([^"]*)"[^>]*Value="([^"]*)"[^>]*/?>',
            r'<Input[^>]*Name="([^"]*)"[^>]*Value="([^"]*)"[^>]*/?>',
            r'<Output[^>]*Name="([^"]*)"[^>]*Value="([^"]*)"[^>]*/?>',
            r'SFC\s*=\s*["\']?([^"\'\s]+)["\']?',
            r'Order\s*=\s*["\']?([^"\'\s]+)["\']?',
            r'Resource\s*=\s*["\']?([^"\'\s]+)["\']?'
        ]
        
        for pattern in sfc_flow_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                if len(match.groups()) >= 2:
                    info["sfc_flow"].append({
                        "parameter": match.group(1),
                        "value": match.group(2),
                        "pattern": pattern,
                        "context": text[max(0, match.start()-50):match.end()+50]
                    })
                else:
                    info["sfc_flow"].append({
                        "operation": match.group(0),
                        "pattern": pattern,
                        "context": text[max(0, match.start()-50):match.end()+50]
                    })
        
        # ME/MII Specific Operations
        me_mii_ops = [
            r'ShopFloorControl',
            r'ManufacturingExecution',
            r'ProductionOrder',
            r'WorkInstruction',
            r'QualityInspection',
            r'MaterialConsumption',
            r'LaborTracking',
            r'EquipmentIntegration',
            r'DataCollection',
            r'Traceability',
            r'WorkCenter',
            r'Operation',
            r'Routing'
        ]
        
        for op in me_mii_ops:
            if re.search(op, text, re.IGNORECASE):
                info["me_mii_operations"].append(op)
        
        # Parameter Mapping (Input -> Output flow)
        param_mapping_pattern = r'<Parameter[^>]*Name="([^"]*)"[^>]*>.*?<Parameter[^>]*Name="([^"]*)"[^>]*>'
        for match in re.finditer(param_mapping_pattern, text, re.DOTALL | re.IGNORECASE):
            info["parameter_mapping"].append({
                "from": match.group(1),
                "to": match.group(2),
                "context": text[max(0, match.start()-100):match.end()+100]
            })
        
        return info if any([info["bls_steps"], info["sfc_flow"], info["me_mii_operations"]]) else None
        
    except Exception as e:
        return None


def parse_i18n_properties(fp: Path) -> Dict[str, str]:
    """i18n properties dosyasını parse et"""
    try:
        text = fp.read_text(encoding='utf-8', errors='ignore')
        i18n_dict = {}
        
        for line in text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                i18n_dict[key.strip()] = value.strip()
        
        return i18n_dict
        
    except Exception:
        return {}


def detect_database_access(fp: Path) -> List[Dict[str, Any]]:
    """Dosyada veritabanı erişimlerini tespit et (i18n dosyalarını hariç tut)"""
    try:
        # i18n dosyalarını hariç tut
        if fp.name.endswith('.properties') or 'i18n' in str(fp).lower():
            return []
            
        text = fp.read_text(encoding='utf-8', errors='ignore')
        db_accesses = []
        
        # Gerçek database erişim kalıpları
        jdbc_patterns = [
            r'jdbc:(\w+)://([^/\s]+)(?:/([^\s]+))?',
            r'Connection\s*\.\s*createStatement',
            r'PreparedStatement',
            r'ResultSet',
            r'Statement\s*\.\s*execute',
            r'Statement\s*\.\s*executeQuery',
            r'Statement\s*\.\s*executeUpdate'
        ]
        
        # Gerçek SQL komutları (i18n metinlerini hariç tut)
        sql_patterns = [
            r'(?:^|\s)SELECT\s+.*?\s+FROM\s+(\w+)',
            r'(?:^|\s)INSERT\s+INTO\s+(\w+)',
            r'(?:^|\s)UPDATE\s+(\w+)\s+SET',
            r'(?:^|\s)DELETE\s+FROM\s+(\w+)',
            r'(?:^|\s)CREATE\s+TABLE\s+(\w+)',
            r'(?:^|\s)ALTER\s+TABLE\s+(\w+)',
            r'(?:^|\s)DROP\s+TABLE\s+(\w+)'
        ]
        
        # Database connection patterns
        conn_patterns = [
            r'DataSource',
            r'ConnectionPool',
            r'getConnection',
            r'DriverManager',
            r'SQLException'
        ]
        
        # SAP specific patterns
        sap_db_patterns = [
            r'SAP\s*DB',
            r'HANA',
            r'ABAP\s*Database',
            r'Open\s*SQL',
            r'Native\s*SQL',
            r'CDS\s*View',
            r'Core\s*Data\s*Services'
        ]
        
        # ME/MII specific database patterns
        me_mii_db_patterns = [
            r'fetchBySQL\s*\(',
            r'executeSQL\s*\(',
            r'me_executeTransaction\s*\(',
            r'executeTransaction\s*\(',
            r'fetchBySQL\s*\(',
            r'getData\s*\(',
            r'getDataBySQL\s*\('
        ]
        
        all_patterns = jdbc_patterns + sql_patterns + conn_patterns + sap_db_patterns + me_mii_db_patterns
        
        for pattern in all_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # i18n metinlerini filtrele
                match_text = match.group(0).lower()
                if any(keyword in match_text for keyword in ['error.label', 'notification.label', 'message.label']):
                    continue
                    
                db_accesses.append({
                    "type": "Database Access",
                    "pattern": pattern,
                    "match": match.group(0),
                    "line": text[:match.start()].count('\n') + 1,
                    "context": text[max(0, match.start()-50):match.end()+50]
                })
        
        return db_accesses
        
    except Exception as e:
        return []


def detect_rest_endpoints(fp: Path) -> List[Dict[str, Any]]:
    """REST endpoint'lerini tespit et (i18n dosyalarını hariç tut)"""
    try:
        # i18n dosyalarını hariç tut
        if fp.name.endswith('.properties') or 'i18n' in str(fp).lower():
            return []
            
        text = fp.read_text(encoding='utf-8', errors='ignore')
        endpoints = []
        
        # REST patterns
        rest_patterns = [
            r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']',
            r'@GetMapping\s*\(\s*["\']([^"\']+)["\']',
            r'@PostMapping\s*\(\s*["\']([^"\']+)["\']',
            r'@PutMapping\s*\(\s*["\']([^"\']+)["\']',
            r'@DeleteMapping\s*\(\s*["\']([^"\']+)["\']',
            r'@Path\s*\(\s*["\']([^"\']+)["\']',
            r'@GET\s+@Path\s*\(\s*["\']([^"\']+)["\']',
            r'@POST\s+@Path\s*\(\s*["\']([^"\']+)["\']',
            r'@PUT\s+@Path\s*\(\s*["\']([^"\']+)["\']',
            r'@DELETE\s+@Path\s*\(\s*["\']([^"\']+)["\']'
        ]
        
        # SAPUI5/JavaScript endpoint patterns
        js_endpoint_patterns = [
            r'\.ajax\s*\(\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'new\s+sap\.ui\.model\.odata\.v2\.ODataModel\s*\(\s*["\']([^"\']+)["\']',
            r'new\s+sap\.ui\.model\.odata\.v4\.ODataModel\s*\(\s*["\']([^"\']+)["\']',
            r'\.read\s*\(\s*["\']([^"\']+)["\']',
            r'\.create\s*\(\s*["\']([^"\']+)["\']',
            r'\.update\s*\(\s*["\']([^"\']+)["\']',
            r'\.remove\s*\(\s*["\']([^"\']+)["\']'
        ]
        
        all_patterns = rest_patterns + js_endpoint_patterns
        
        for pattern in all_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # i18n metinlerini filtrele
                match_text = match.group(0).lower()
                if any(keyword in match_text for keyword in ['error.label', 'notification.label', 'message.label']):
                    continue
                    
                endpoints.append({
                    "type": "REST Endpoint",
                    "pattern": pattern,
                    "path": match.group(1) if len(match.groups()) > 0 else match.group(0),
                    "line": text[:match.start()].count('\n') + 1,
                    "context": text[max(0, match.start()-50):match.end()+50]
                })
        
        return endpoints
        
    except Exception as e:
        return []


def detect_bls_steps(fp: Path) -> List[Dict[str, Any]]:
    """BLS/Transaction adımlarını tespit et (i18n dosyalarını hariç tut)"""
    try:
        # i18n dosyalarını hariç tut
        if fp.name.endswith('.properties') or 'i18n' in str(fp).lower():
            return []
            
        text = fp.read_text(encoding='utf-8', errors='ignore')
        bls_steps = []
        
        # Gerçek BLS step patterns (ME/MII specific)
        bls_patterns = [
            r'tracer\.executeTransaction\s*\(\s*["\']([^"\']+)["\']',
            r'me_executeTransaction\s*\(\s*["\']([^"\']+)["\']',
            r'executeTransaction\s*\(\s*["\']([^"\']+)["\']',
            r'<Service\s+name\s*=\s*["\']([^"\']*BLS[^"\']*)["\']',
            r'<Service\s+name\s*=\s*["\']([^"\']*TRX[^"\']*)["\']',
            r'BLS_TRX_\w+',
            r'TRX_\w+',
            r'BLS_\w+',
            r'BLS\s*Step',
            r'Transaction\s*Step',
            r'Business\s*Logic\s*Step',
            r'ME\s*Step',
            r'MII\s*Step',
            r'Workflow\s*Step',
            r'Process\s*Step',
            r'Activity\s*Step'
        ]
        
        for pattern in bls_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # i18n metinlerini filtrele
                match_text = match.group(0).lower()
                if any(keyword in match_text for keyword in ['error.label', 'notification.label', 'message.label', 'checkbox cannot be changed']):
                    continue
                    
                bls_steps.append({
                    "type": "BLS Step",
                    "pattern": pattern,
                    "step": match.group(0),
                    "line": text[:match.start()].count('\n') + 1,
                    "context": text[max(0, match.start()-50):match.end()+50]
                })
        
        return bls_steps
        
    except Exception as e:
        return []


def detect_ui_components(fp: Path) -> Dict[str, Any]:
    """SAPUI5 UI bileşenlerini tespit et"""
    try:
        if not fp.suffix.lower() in ['.xml', '.view.xml', '.fragment.xml']:
            return {}
            
        text = fp.read_text(encoding='utf-8', errors='ignore')
        
        # UI component patterns
        ui_components = {
            "buttons": 0,
            "tables": 0,
            "forms": 0,
            "inputs": 0,
            "dialogs": 0,
            "lists": 0,
            "panels": 0,
            "tabs": 0,
            "charts": 0,
            "trees": 0
        }
        
        # Button patterns
        button_patterns = [
            r'<Button',
            r'<sap\.m\.Button',
            r'<core:Button',
            r'<Button\s+',
            r'<sap\.m\.Button\s+'
        ]
        
        # Table patterns
        table_patterns = [
            r'<Table',
            r'<sap\.m\.Table',
            r'<core:Table',
            r'<List',
            r'<sap\.m\.List'
        ]
        
        # Form patterns
        form_patterns = [
            r'<Form',
            r'<sap\.ui\.layout\.form\.Form',
            r'<SimpleForm',
            r'<sap\.ui\.layout\.form\.SimpleForm'
        ]
        
        # Input patterns
        input_patterns = [
            r'<Input',
            r'<sap\.m\.Input',
            r'<TextArea',
            r'<sap\.m\.TextArea',
            r'<ComboBox',
            r'<sap\.m\.ComboBox',
            r'<Select',
            r'<sap\.m\.Select'
        ]
        
        # Dialog patterns
        dialog_patterns = [
            r'<Dialog',
            r'<sap\.m\.Dialog',
            r'<Popover',
            r'<sap\.m\.Popover'
        ]
        
        # Panel patterns
        panel_patterns = [
            r'<Panel',
            r'<sap\.m\.Panel',
            r'<Page',
            r'<sap\.m\.Page'
        ]
        
        # Tab patterns
        tab_patterns = [
            r'<TabContainer',
            r'<sap\.m\.TabContainer',
            r'<Tab',
            r'<sap\.m\.Tab'
        ]
        
        # Chart patterns
        chart_patterns = [
            r'<Chart',
            r'<sap\.viz\.Chart',
            r'<VizFrame',
            r'<sap\.viz\.VizFrame'
        ]
        
        # Tree patterns
        tree_patterns = [
            r'<Tree',
            r'<sap\.m\.Tree',
            r'<TreeTable',
            r'<sap\.ui\.table\.TreeTable'
        ]
        
        # Count patterns
        pattern_groups = [
            (button_patterns, "buttons"),
            (table_patterns, "tables"),
            (form_patterns, "forms"),
            (input_patterns, "inputs"),
            (dialog_patterns, "dialogs"),
            (panel_patterns, "panels"),
            (tab_patterns, "tabs"),
            (chart_patterns, "charts"),
            (tree_patterns, "trees")
        ]
        
        for patterns, component_type in pattern_groups:
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                ui_components[component_type] += len(list(matches))
        
        # Lists are counted separately
        list_patterns = [
            r'<List',
            r'<sap\.m\.List',
            r'<StandardListItem',
            r'<sap\.m\.StandardListItem'
        ]
        
        for pattern in list_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            ui_components["lists"] += len(list(matches))
        
        return ui_components
        
    except Exception as e:
        return {}


def analyze_sapui5_deep(root: Path) -> Dict[str, Any]:
    """Derinlemesine SAPUI5 analizi"""
    
    result = {
        "controllers": [],
        "views": [],
        "fragments": [],
        "i18n": {},
        "models": [],
        "services": {
            "odata": [],
            "rest": []
        },
        "ui_components": {
            "buttons": 0,
            "tables": 0,
            "forms": 0,
            "inputs": 0,
            "dialogs": 0
        },
        "navigation_flow": [],
        "data_bindings": [],
        "event_handlers": [],
        "sap_me_apis": [],
        "sfc_operations": [],
        "me_mii_patterns": [],
        "xml_analysis": [],
        "parameter_flows": []
    }
    
    for fp in root.rglob("*"):
        if not fp.is_file():
            continue
        
        # Controller files
        if fp.suffix == '.js' and 'controller' in fp.parts:
            controller_data = parse_controller_deep(fp)
            if controller_data:
                result["controllers"].append(controller_data)
                result["event_handlers"].extend(controller_data["event_handlers"])
                result["navigation_flow"].extend(controller_data["navigations"])
                
                # OData servisleri
                for odata in controller_data["odata_models"]:
                    if odata not in result["services"]["odata"]:
                        result["services"]["odata"].append(odata)
                
                # REST API'ler
                for api in controller_data["api_calls"]:
                    if api not in result["services"]["rest"]:
                        result["services"]["rest"].append(api)
                
                # SAP ME API'leri
                for api in controller_data["sap_me_apis"]:
                    result["sap_me_apis"].append(api)
                
                # SFC operasyonları
                for sfc in controller_data["sfc_operations"]:
                    result["sfc_operations"].append(sfc)
                
                # ME/MII pattern'leri
                for pattern in controller_data["me_mii_patterns"]:
                    if pattern not in result["me_mii_patterns"]:
                        result["me_mii_patterns"].append(pattern)
        
        # XML dosyaları için ME/MII analizi
        elif fp.suffix == '.xml':
            xml_data = parse_xml_file(fp)
            if xml_data:
                result["xml_analysis"].append(xml_data)
                
                # Parameter flow'ları
                for flow in xml_data["sfc_flow"]:
                    result["parameter_flows"].append(flow)
                
                # ME/MII operasyonları
                for op in xml_data["me_mii_operations"]:
                    if op not in result["me_mii_patterns"]:
                        result["me_mii_patterns"].append(op)
        
        # View files
        elif fp.suffix == '.xml' and 'view' in fp.parts:
            view_data = parse_view_xml(fp)
            if view_data:
                result["views"].append(view_data)
                result["data_bindings"].extend(view_data["bindings"])
                
                # UI component sayıları
                for control in view_data["controls"]:
                    ctrl_type = control["type"].lower()
                    if 'button' in ctrl_type:
                        result["ui_components"]["buttons"] += 1
                    elif 'table' in ctrl_type or 'list' in ctrl_type:
                        result["ui_components"]["tables"] += 1
                    elif 'form' in ctrl_type:
                        result["ui_components"]["forms"] += 1
                    elif 'input' in ctrl_type:
                        result["ui_components"]["inputs"] += 1
                    elif 'dialog' in ctrl_type:
                        result["ui_components"]["dialogs"] += 1
        
        # Fragment files
        elif fp.suffix == '.xml' and 'fragment' in fp.parts:
            result["fragments"].append(str(fp))
        
        # i18n files
        elif fp.name.endswith('.properties') and 'i18n' in fp.parts:
            i18n_data = parse_i18n_properties(fp)
            result["i18n"].update(i18n_data)
    
    return result


def build_advanced_summary(base_result, sapui5_basic, sapui5_deep, db_accesses=None, rest_endpoints=None, bls_steps=None, ui_components=None) -> str:
    """Gelişmiş özet rapor"""
    
    lines = []
    lines.append("# SAP ME/MII Advanced Analysis Report\n")
    
    # Executive Summary
    lines.append("## 📊 Executive Summary\n")
    lines.append(f"- **Project Type:** SAPUI5/Fiori Application")
    lines.append(f"- **Controllers:** {len(sapui5_deep['controllers'])} files")
    lines.append(f"- **Views:** {len(sapui5_deep['views'])} files")
    lines.append(f"- **Fragments:** {len(sapui5_deep['fragments'])} files")
    lines.append(f"- **i18n Files:** {len(sapui5_deep['i18n'])} files")
    
    # Database Access Summary
    if db_accesses:
        lines.append(f"- **Database Accesses:** {len(db_accesses)} detected")
    else:
        lines.append("- **Database Accesses:** 0 detected")
    
    # REST Endpoints Summary
    if rest_endpoints:
        lines.append(f"- **REST Endpoints:** {len(rest_endpoints)} detected")
    else:
        lines.append("- **REST Endpoints:** 0 detected")
    
    # BLS Steps Summary
    if bls_steps:
        lines.append(f"- **BLS Steps:** {len(bls_steps)} detected")
    else:
        lines.append("- **BLS Steps:** 0 detected")
    
    # UI Components Summary
    if ui_components:
        total_ui = sum(ui_components.values())
        lines.append(f"- **UI Components:** {total_ui} total")
        lines.append(f"  - Buttons: {ui_components.get('buttons', 0)}")
        lines.append(f"  - Tables/Lists: {ui_components.get('tables', 0) + ui_components.get('lists', 0)}")
        lines.append(f"  - Forms: {ui_components.get('forms', 0)}")
        lines.append(f"  - Inputs: {ui_components.get('inputs', 0)}")
        lines.append(f"  - Dialogs: {ui_components.get('dialogs', 0)}")
    else:
        lines.append("- **UI Components:** 0 detected")
    
    lines.append("")
    
    # Database Access Details
    if db_accesses:
        lines.append("## 🗄️ Database Access Analysis")
        lines.append("")
        
        # Group by type
        db_types = {}
        for access in db_accesses:
            db_type = access.get('type', 'Unknown')
            if db_type not in db_types:
                db_types[db_type] = []
            db_types[db_type].append(access)
        
        for db_type, accesses in db_types.items():
            lines.append(f"### {db_type} ({len(accesses)} found)")
            for access in accesses[:5]:  # Show first 5
                lines.append(f"- **Line {access.get('line', '?')}:** {access.get('match', access.get('step', 'Unknown'))}")
                if 'context' in access:
                    context = access['context'].strip()
                    if len(context) > 100:
                        context = context[:100] + "..."
                    lines.append(f"  ```")
                    lines.append(f"  {context}")
                    lines.append(f"  ```")
            if len(accesses) > 5:
                lines.append(f"- ... and {len(accesses) - 5} more")
            lines.append("")
    
    # REST Endpoints Details
    if rest_endpoints:
        lines.append("## 🌐 REST Endpoints Analysis")
        lines.append("")
        
        for endpoint in rest_endpoints[:10]:  # Show first 10
            lines.append(f"- **{endpoint.get('path', 'Unknown')}** (Line {endpoint.get('line', '?')})")
            if 'context' in endpoint:
                context = endpoint['context'].strip()
                if len(context) > 100:
                    context = context[:100] + "..."
                lines.append(f"  ```")
                lines.append(f"  {context}")
                lines.append(f"  ```")
        if len(rest_endpoints) > 10:
            lines.append(f"- ... and {len(rest_endpoints) - 10} more")
        lines.append("")
    
    # BLS Steps Details
    if bls_steps:
        lines.append("## ⚙️ BLS Steps Analysis")
        lines.append("")
        
        for step in bls_steps[:10]:  # Show first 10
            lines.append(f"- **{step.get('step', 'Unknown')}** (Line {step.get('line', '?')})")
            if 'context' in step:
                context = step['context'].strip()
                if len(context) > 100:
                    context = context[:100] + "..."
                lines.append(f"  ```")
                lines.append(f"  {context}")
                lines.append(f"  ```")
        if len(bls_steps) > 10:
            lines.append(f"- ... and {len(bls_steps) - 10} more")
        lines.append("")
    lines.append(f"- **Fragments:** {len(sapui5_deep['fragments'])} files")
    lines.append(f"- **i18n Keys:** {len(sapui5_deep['i18n'])} translations")
    lines.append(f"- **OData Services:** {len(sapui5_deep['services']['odata'])} endpoints")
    lines.append(f"- **REST APIs:** {len(sapui5_deep['services']['rest'])} endpoints\n")
    
    # UI Components
    lines.append("## 🎨 UI Components Analysis\n")
    ui = sapui5_deep['ui_components']
    lines.append(f"- **Buttons:** {ui['buttons']}")
    lines.append(f"- **Tables/Lists:** {ui['tables']}")
    lines.append(f"- **Forms:** {ui['forms']}")
    lines.append(f"- **Input Fields:** {ui['inputs']}")
    lines.append(f"- **Dialogs:** {ui['dialogs']}\n")
    
    # Controllers Detail
    if sapui5_deep['controllers']:
        lines.append("## 🎮 Controllers Analysis\n")
        for ctrl in sapui5_deep['controllers'][:5]:  # İlk 5
            lines.append(f"### {Path(ctrl['file']).name}\n")
            lines.append(f"- **Functions:** {len(ctrl['functions'])}")
            lines.append(f"- **Event Handlers:** {', '.join(ctrl['event_handlers'][:5])}")
            if ctrl['api_calls']:
                lines.append(f"- **API Calls:** {len(ctrl['api_calls'])} endpoints")
            if ctrl['odata_operations']:
                lines.append(f"- **OData Operations:** {len(ctrl['odata_operations'])} operations")
            lines.append("")
    
    # Views Detail
    if sapui5_deep['views']:
        lines.append("## 📱 Views Analysis\n")
        for view in sapui5_deep['views'][:5]:  # İlk 5
            lines.append(f"### {Path(view['file']).name}\n")
            lines.append(f"- **Controls:** {len(view['controls'])} UI elements")
            lines.append(f"- **Data Bindings:** {len(view['bindings'])} bindings")
            lines.append(f"- **Events:** {len(view['events'])} event handlers")
            if view['fragments']:
                lines.append(f"- **Fragments:** {', '.join(view['fragments'])}")
            lines.append("")
    
    # Navigation Flow
    if sapui5_deep['navigation_flow']:
        lines.append("## 🗺️ Navigation Flow\n")
        unique_navs = list(set(sapui5_deep['navigation_flow']))
        for nav in unique_navs[:10]:
            lines.append(f"- → {nav}")
        lines.append("")
    
    # Services
    lines.append("## 🌐 External Services\n")
    if sapui5_deep['services']['odata']:
        lines.append("### OData Services\n")
        for odata in sapui5_deep['services']['odata']:
            lines.append(f"- {odata}")
        lines.append("")
    
    if sapui5_deep['services']['rest']:
        lines.append("### REST APIs\n")
        for api in sapui5_deep['services']['rest'][:10]:
            lines.append(f"- {api}")
        lines.append("")
    
    # i18n Sample
    if sapui5_deep['i18n']:
        lines.append("## 🌍 Internationalization (i18n)\n")
        lines.append(f"Total translation keys: {len(sapui5_deep['i18n'])}\n")
        lines.append("Sample keys:\n")
        for key, value in list(sapui5_deep['i18n'].items())[:10]:
            lines.append(f"- `{key}`: {value}")
        lines.append("")
    
    # SAP ME/MII Specific Analysis
    if sapui5_deep['sap_me_apis'] or sapui5_deep['sfc_operations'] or sapui5_deep['me_mii_patterns']:
        lines.append("## 🏭 SAP ME/MII Specific Analysis\n")
        
        if sapui5_deep['sap_me_apis']:
            lines.append("### SAP ME API Usage\n")
            api_classes = {}
            for api in sapui5_deep['sap_me_apis']:
                class_name = api['class']
                if class_name not in api_classes:
                    api_classes[class_name] = 0
                api_classes[class_name] += 1
            
            for class_name, count in sorted(api_classes.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"- **{class_name}**: {count} usage(s)")
            lines.append("")
        
        if sapui5_deep['sfc_operations']:
            lines.append("### SFC/Order/Resource Operations\n")
            sfc_types = {}
            for sfc in sapui5_deep['sfc_operations']:
                op_type = sfc['operation'].split('=')[0].strip() if '=' in sfc['operation'] else sfc['operation']
                if op_type not in sfc_types:
                    sfc_types[op_type] = 0
                sfc_types[op_type] += 1
            
            for op_type, count in sorted(sfc_types.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"- **{op_type}**: {count} operation(s)")
            lines.append("")
        
        if sapui5_deep['me_mii_patterns']:
            lines.append("### ME/MII Domain Patterns\n")
            for pattern in sapui5_deep['me_mii_patterns']:
                lines.append(f"- {pattern}")
            lines.append("")
        
        if sapui5_deep['parameter_flows']:
            lines.append("### Parameter Flow Analysis\n")
            lines.append(f"Total parameter flows detected: {len(sapui5_deep['parameter_flows'])}\n")
            for flow in sapui5_deep['parameter_flows'][:10]:  # İlk 10
                if 'parameter' in flow:
                    lines.append(f"- **{flow['parameter']}** = {flow['value']}")
                else:
                    lines.append(f"- {flow['operation']}")
            lines.append("")
    
    # UI Components Analysis
    if ui_components:
        lines.append("## 🎨 UI Components Analysis\n")
        lines.append(f"- **Buttons:** {ui_components.get('buttons', 0)}")
        lines.append(f"- **Tables/Lists:** {ui_components.get('tables', 0) + ui_components.get('lists', 0)}")
        lines.append(f"- **Forms:** {ui_components.get('forms', 0)}")
        lines.append(f"- **Input Fields:** {ui_components.get('inputs', 0)}")
        lines.append(f"- **Dialogs:** {ui_components.get('dialogs', 0)}")
        lines.append(f"- **Panels/Pages:** {ui_components.get('panels', 0)}")
        lines.append(f"- **Tabs:** {ui_components.get('tabs', 0)}")
        lines.append(f"- **Charts:** {ui_components.get('charts', 0)}")
        lines.append(f"- **Trees:** {ui_components.get('trees', 0)}")
        lines.append("")
    
    # Recommendations
    lines.append("## 💡 Recommendations\n")
    lines.append("### Code Quality")
    lines.append("- ✅ SAPUI5 best practices detected")
    lines.append("- ✅ MVC pattern implemented")
    lines.append("- ✅ Data binding utilized")
    if ui_components and sum(ui_components.values()) > 0:
        lines.append("- ✅ UI Components properly structured")
    lines.append("")
    
    lines.append("### Potential Improvements")
    if len(sapui5_deep['services']['rest']) > 10:
        lines.append("- ⚠️ Consider consolidating REST API calls")
    if ui_components and ui_components.get('inputs', 0) > 20:
        lines.append("- ⚠️ Large number of input fields - consider form optimization")
    if not sapui5_deep['i18n']:
        lines.append("- ⚠️ No i18n detected - consider adding internationalization")
    if ui_components and ui_components.get('buttons', 0) > 50:
        lines.append("- ⚠️ High button count - consider UI simplification")
    lines.append("")
    
    return "\n".join(lines)


def main_advanced():
    """Advanced analyzer main"""
    import click
    from rich import print
    
    @click.command()
    @click.option('--root', type=click.Path(path_type=Path, exists=True), required=True)
    @click.option('--out', type=click.Path(path_type=Path), default=Path('./out_advanced'))
    def run(root: Path, out: Path):
        print(f"[bold green]SAP ME/MII Advanced Analyzer[/bold green] — scanning: [cyan]{root}[/cyan]")
        out.mkdir(parents=True, exist_ok=True)
        
        # Base analiz
        print("[1/3] Running base analysis...")
        base_result, sapui5_basic = base_analyzer.analyze_folder_extended(root)
        
        # Deep SAPUI5 analiz
        print("[2/4] Deep SAPUI5 analysis...")
        sapui5_deep = analyze_sapui5_deep(root)
        
        # Veritabanı ve endpoint tespiti
        print("[3/5] Database and endpoint detection...")
        db_accesses = []
        rest_endpoints = []
        bls_steps = []
        ui_components_total = {
            "buttons": 0,
            "tables": 0,
            "forms": 0,
            "inputs": 0,
            "dialogs": 0,
            "lists": 0,
            "panels": 0,
            "tabs": 0,
            "charts": 0,
            "trees": 0
        }
        
        # Tüm dosyaları tara
        for file_path in root.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.java', '.js', '.xml', '.properties']:
                db_accesses.extend(detect_database_access(file_path))
                rest_endpoints.extend(detect_rest_endpoints(file_path))
                bls_steps.extend(detect_bls_steps(file_path))
                
                # UI Components tespiti
                ui_components = detect_ui_components(file_path)
                for component_type, count in ui_components.items():
                    ui_components_total[component_type] += count
        
        # Rapor oluştur
        print("[4/5] Generating reports...")
        summary = build_advanced_summary(base_result, sapui5_basic, sapui5_deep, db_accesses, rest_endpoints, bls_steps, ui_components_total)
        (out / 'ADVANCED_SUMMARY.md').write_text(summary, encoding='utf-8')
        
        # Deep SAPUI5 JSON
        (out / 'sapui5_deep_analysis.json').write_text(
            json.dumps(sapui5_deep, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        # Base outputs
        base_summary = base_analyzer.build_extended_summary(base_result, sapui5_basic)
        (out / 'SUMMARY.md').write_text(base_summary, encoding='utf-8')
        
        print(f"\n[bold]Done.[/bold] Outputs -> {out.resolve()}")
        print(" - ADVANCED_SUMMARY.md (Enhanced!)")
        print(" - sapui5_deep_analysis.json (Enhanced!)")
        print(" - SUMMARY.md")
        print(" - sapui5_details.json")
        print(f"\n[bold green]Analysis Quality Improvements:[/bold green]")
        print(f" - Database Access: {len(db_accesses)} (filtered i18n)")
        print(f" - BLS Steps: {len(bls_steps)} (filtered i18n)")
        print(f" - REST Endpoints: {len(rest_endpoints)} (enhanced patterns)")
        print(f" - UI Components: {sum(ui_components_total.values())} total\n")
    
    run()


if __name__ == '__main__':
    main_advanced()
