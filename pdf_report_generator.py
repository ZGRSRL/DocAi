"""
SAP ME/MII Professional PDF Report Generator
- Combines analysis outputs into professional PDF reports
- Supports multiple data sources (SUMMARY.md, ADVANCED_SUMMARY.md, JSON data)
- Generates executive summaries and technical documentation
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import re

# PDF generation libraries
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class SAPMEIIPDFGenerator:
    """Professional PDF report generator for SAP ME/MII analysis"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.styles = getSampleStyleSheet() if REPORTLAB_AVAILABLE else None
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        if not REPORTLAB_AVAILABLE:
            return
            
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f77b4')
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#2c3e50')
        )
        
        # Subsection style
        self.subsection_style = ParagraphStyle(
            'CustomSubsection',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.HexColor('#34495e')
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14
        )
        
        # Code style
        self.code_style = ParagraphStyle(
            'CustomCode',
            parent=self.styles['Code'],
            fontSize=9,
            fontName='Courier',
            backColor=colors.HexColor('#f8f9fa'),
            borderColor=colors.HexColor('#dee2e6'),
            borderWidth=1,
            leftIndent=10,
            rightIndent=10,
            spaceAfter=6
        )

    def load_analysis_data(self, analysis_dir: Path) -> Dict[str, Any]:
        """Load all analysis data from directory"""
        data = {
            'summary': {},
            'advanced_summary': {},
            'sapui5_deep': {},
            'metadata': {
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'project_name': analysis_dir.name,
                'analysis_dir': str(analysis_dir)
            }
        }
        
        # Load SUMMARY.md
        summary_path = analysis_dir / 'SUMMARY.md'
        if summary_path.exists():
            data['summary'] = self.parse_markdown_file(summary_path)
        
        # Load ADVANCED_SUMMARY.md
        advanced_path = analysis_dir / 'ADVANCED_SUMMARY.md'
        if advanced_path.exists():
            data['advanced_summary'] = self.parse_markdown_file(advanced_path)
        
        # Load sapui5_deep_analysis.json
        json_path = analysis_dir / 'sapui5_deep_analysis.json'
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data['sapui5_deep'] = json.load(f)
            except Exception as e:
                print(f"Error loading JSON data: {e}")
        
        return data

    def parse_markdown_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse markdown file into structured data"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Split into sections
            sections = {}
            current_section = None
            current_content = []
            
            for line in content.split('\n'):
                if line.startswith('#'):
                    # Save previous section
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = line.strip('# ').strip()
                    current_content = []
                else:
                    current_content.append(line)
            
            # Save last section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            
            return sections
        except Exception as e:
            print(f"Error parsing markdown file {file_path}: {e}")
            return {}

    def extract_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from analysis data"""
        metrics = {
            'controllers': 0,
            'views': 0,
            'functions': 0,
            'event_handlers': 0,
            'api_calls': 0,
            'odata_services': 0,
            'rest_apis': 0,
            'i18n_keys': 0,
            'ui_components': {},
            'sap_me_apis': 0,
            'sfc_operations': 0,
            'me_mii_patterns': 0
        }
        
        # Extract from sapui5_deep_analysis.json
        if data:
            sapui5_data = data
            
            metrics['controllers'] = len(sapui5_data.get('controllers', []))
            metrics['views'] = len(sapui5_data.get('views', []))
            metrics['functions'] = sum(len(ctrl.get('functions', [])) for ctrl in sapui5_data.get('controllers', []))
            metrics['event_handlers'] = sum(len(ctrl.get('event_handlers', [])) for ctrl in sapui5_data.get('controllers', []))
            metrics['api_calls'] = sum(len(ctrl.get('api_calls', [])) for ctrl in sapui5_data.get('controllers', []))
            metrics['odata_services'] = len(sapui5_data.get('services', {}).get('odata', []))
            metrics['rest_apis'] = len(sapui5_data.get('services', {}).get('rest', []))
            metrics['i18n_keys'] = len(sapui5_data.get('i18n', {}))
            metrics['ui_components'] = sapui5_data.get('ui_components', {})
            metrics['sap_me_apis'] = len(sapui5_data.get('sap_me_apis', []))
            metrics['sfc_operations'] = len(sapui5_data.get('sfc_operations', []))
            metrics['me_mii_patterns'] = len(sapui5_data.get('me_mii_patterns', []))
        
        return metrics

    def generate_executive_summary(self, data: Dict[str, Any], metrics: Dict[str, Any]) -> List:
        """Generate executive summary section"""
        if not REPORTLAB_AVAILABLE:
            return []
            
        elements = []
        
        # Title
        elements.append(Paragraph("SAP ME/MII Analysis Report", self.title_style))
        elements.append(Spacer(1, 20))
        
        # Project info
        project_name = data['metadata']['project_name']
        generated_at = data['metadata']['generated_at']
        
        elements.append(Paragraph(f"<b>Project:</b> {project_name}", self.body_style))
        elements.append(Paragraph(f"<b>Analysis Date:</b> {generated_at}", self.body_style))
        elements.append(Spacer(1, 20))
        
        # Executive summary
        elements.append(Paragraph("Executive Summary", self.section_style))
        
        summary_text = f"""
        This report presents a comprehensive analysis of the {project_name} SAP ME/MII project. 
        The analysis reveals a sophisticated SAPUI5/Fiori application with {metrics['controllers']} controllers, 
        {metrics['views']} views, and {metrics['functions']} total functions. The application demonstrates 
        strong integration with SAP ME/MII systems through {metrics['sap_me_apis']} ME API calls and 
        {metrics['sfc_operations']} SFC operations.
        """
        
        elements.append(Paragraph(summary_text, self.body_style))
        elements.append(Spacer(1, 20))
        
        # Key metrics table
        metrics_data = [
            ['Metric', 'Value'],
            ['Controllers', str(metrics['controllers'])],
            ['Views', str(metrics['views'])],
            ['Functions', str(metrics['functions'])],
            ['Event Handlers', str(metrics['event_handlers'])],
            ['SAP ME API Calls', str(metrics['sap_me_apis'])],
            ['SFC Operations', str(metrics['sfc_operations'])],
            ['i18n Translation Keys', str(metrics['i18n_keys'])],
            ['ME/MII Patterns', str(metrics['me_mii_patterns'])]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(metrics_table)
        elements.append(PageBreak())
        
        return elements

    def generate_architecture_section(self, data: Dict[str, Any]) -> List:
        """Generate application architecture section"""
        if not REPORTLAB_AVAILABLE:
            return []
            
        elements = []
        
        elements.append(Paragraph("Application Architecture & Navigation", self.section_style))
        
        # Navigation flow
        if 'sapui5_deep' in data and 'navigation_flow' in data['sapui5_deep']:
            nav_flow = data['sapui5_deep']['navigation_flow']
            if nav_flow:
                elements.append(Paragraph("Navigation Flow", self.subsection_style))
                nav_text = "The application implements the following navigation patterns:<br/><br/>"
                for nav in nav_flow[:10]:  # Limit to first 10
                    nav_text += f"• {nav}<br/>"
                elements.append(Paragraph(nav_text, self.body_style))
                elements.append(Spacer(1, 12))
        
        # Controllers analysis
        if 'sapui5_deep' in data and 'controllers' in data['sapui5_deep']:
            controllers = data['sapui5_deep']['controllers']
            if controllers:
                elements.append(Paragraph("Controller Architecture", self.subsection_style))
                
                # Find BaseController
                base_controller = None
                for ctrl in controllers:
                    if 'BaseController' in ctrl.get('file', ''):
                        base_controller = ctrl
                        break
                
                if base_controller:
                    elements.append(Paragraph(
                        f"<b>BaseController.js</b> serves as the foundation with {len(base_controller.get('functions', []))} functions. "
                        f"All other controllers extend from this base class, ensuring consistent architecture patterns.",
                        self.body_style
                    ))
                    elements.append(Spacer(1, 12))
                
                # Controller summary table
                ctrl_data = [['Controller', 'Functions', 'Event Handlers']]
                for ctrl in controllers[:8]:  # Limit to first 8
                    filename = Path(ctrl.get('file', '')).name
                    functions = len(ctrl.get('functions', []))
                    events = len(ctrl.get('event_handlers', []))
                    ctrl_data.append([filename, str(functions), str(events)])
                
                ctrl_table = Table(ctrl_data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
                ctrl_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(ctrl_table)
                elements.append(PageBreak())
        
        return elements

    def generate_me_mii_analysis(self, data: Dict[str, Any]) -> List:
        """Generate ME/MII specific analysis section"""
        if not REPORTLAB_AVAILABLE:
            return []
            
        elements = []
        
        elements.append(Paragraph("SAP ME/MII Integration Analysis", self.section_style))
        
        if data:
            sapui5_data = data
            
            # SAP ME API Usage
            if 'sap_me_apis' in sapui5_data and sapui5_data['sap_me_apis']:
                elements.append(Paragraph("SAP ME API Usage", self.subsection_style))
                
                # Count API usage
                api_counts = {}
                for api in sapui5_data['sap_me_apis']:
                    class_name = api.get('class', 'Unknown')
                    api_counts[class_name] = api_counts.get(class_name, 0) + 1
                
                # Create API usage table
                api_data = [['API Class', 'Usage Count']]
                for api_class, count in sorted(api_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    api_data.append([api_class, str(count)])
                
                api_table = Table(api_data, colWidths=[2.5*inch, 1.5*inch])
                api_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fadbd8')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(api_table)
                elements.append(Spacer(1, 12))
            
            # SFC Operations
            if 'sfc_operations' in sapui5_data and sapui5_data['sfc_operations']:
                elements.append(Paragraph("SFC/Order/Resource Operations", self.subsection_style))
                
                # Count SFC operations
                sfc_counts = {}
                for sfc in sapui5_data['sfc_operations']:
                    operation = sfc.get('operation', 'Unknown')
                    op_type = operation.split('=')[0].strip() if '=' in operation else operation
                    sfc_counts[op_type] = sfc_counts.get(op_type, 0) + 1
                
                # Create SFC operations table
                sfc_data = [['Operation Type', 'Count']]
                for op_type, count in sorted(sfc_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    sfc_data.append([op_type, str(count)])
                
                sfc_table = Table(sfc_data, colWidths=[2.5*inch, 1.5*inch])
                sfc_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#d5f4e6')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(sfc_table)
                elements.append(Spacer(1, 12))
            
            # ME/MII Patterns
            if 'me_mii_patterns' in sapui5_data and sapui5_data['me_mii_patterns']:
                elements.append(Paragraph("ME/MII Domain Patterns", self.subsection_style))
                patterns_text = "The application implements the following ME/MII domain patterns:<br/><br/>"
                for pattern in sapui5_data['me_mii_patterns']:
                    patterns_text += f"• {pattern}<br/>"
                elements.append(Paragraph(patterns_text, self.body_style))
                elements.append(PageBreak())
        
        return elements

    def generate_ui_analysis(self, data: Dict[str, Any]) -> List:
        """Generate UI components analysis section"""
        if not REPORTLAB_AVAILABLE:
            return []
            
        elements = []
        
        elements.append(Paragraph("UI Components & User Experience", self.section_style))
        
        if data and 'ui_components' in data:
            ui_components = data['ui_components']
            
            # Manual count if data is incorrect
            if sum(ui_components.values()) == 0:
                # Count buttons manually
                button_count = 0
                table_count = 0
                input_count = 0
                
                # Count from controllers
                for ctrl in data.get('controllers', []):
                    functions = ctrl.get('functions', [])
                    for func in functions:
                        if 'Button' in func:
                            button_count += 1
                
                # Count from views
                for view in data.get('views', []):
                    controls = view.get('controls', [])
                    for control in controls:
                        if control.get('type') == 'Button':
                            button_count += 1
                        elif control.get('type') == 'Table':
                            table_count += 1
                        elif control.get('type') in ['Input', 'TextField']:
                            input_count += 1
                
                # Update UI components
                ui_components = {
                    'buttons': button_count,
                    'tables': table_count,
                    'inputs': input_count,
                    'forms': 0,
                    'dialogs': 0
                }
            
            # UI components summary
            elements.append(Paragraph("UI Components Summary", self.subsection_style))
            
            ui_data = [['Component Type', 'Count']]
            for comp_type, count in ui_components.items():
                ui_data.append([comp_type.title(), str(count)])
            
            ui_table = Table(ui_data, colWidths=[2.5*inch, 1.5*inch])
            ui_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e8daef')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(ui_table)
            elements.append(Spacer(1, 12))
        
        # i18n Analysis
        if 'sapui5_deep' in data and 'i18n' in data['sapui5_deep']:
            i18n_data = data['sapui5_deep']['i18n']
            if i18n_data:
                elements.append(Paragraph("Internationalization (i18n)", self.subsection_style))
                
                elements.append(Paragraph(
                    f"The application supports internationalization with {len(i18n_data)} translation keys. "
                    "This indicates comprehensive multi-language support and proper localization practices.",
                    self.body_style
                ))
                
                # Sample i18n keys
                elements.append(Paragraph("Sample Translation Keys:", self.subsection_style))
                sample_keys = list(i18n_data.items())[:10]
                keys_text = ""
                for key, value in sample_keys:
                    keys_text += f"• <b>{key}</b>: {value}<br/>"
                elements.append(Paragraph(keys_text, self.body_style))
                elements.append(PageBreak())
        
        return elements

    def extract_specific_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract specific insights from analysis data for targeted recommendations"""
        insights = {
            'basecontroller_functions': 0,
            'error_codes': [],
            'critical_error_codes': [],
            'me_api_usage': {},
            'websocket_usage': False,
            'nc_login_controllers': [],
            'sfc_operations': []
        }
        
        if data:
            sapui5_data = data
            
            # BaseController analysis
            for ctrl in sapui5_data.get('controllers', []):
                if 'BaseController' in ctrl.get('file', ''):
                    insights['basecontroller_functions'] = len(ctrl.get('functions', []))
                    break
            
            # Error codes analysis
            i18n_data = sapui5_data.get('i18n', {})
            for key, value in i18n_data.items():
                if 'error.label' in key:
                    insights['error_codes'].append({'code': key, 'message': value})
                    # Critical error codes (13xxx series)
                    if any(key.startswith(f'13{i:03d}.error.label') for i in range(10)):
                        insights['critical_error_codes'].append({'code': key, 'message': value})
            
            # ME API usage analysis
            for api in sapui5_data.get('sap_me_apis', []):
                class_name = api.get('class', 'Unknown')
                insights['me_api_usage'][class_name] = insights['me_api_usage'].get(class_name, 0) + 1
            
            # WebSocket usage
            for ctrl in sapui5_data.get('controllers', []):
                functions = ctrl.get('functions', [])
                if any('WebSocket' in func for func in functions):
                    insights['websocket_usage'] = True
                
                # NC Login controllers
                if any('NCDialog' in func or 'Login' in func for func in functions):
                    filename = Path(ctrl.get('file', '')).name
                    insights['nc_login_controllers'].append(filename)
            
            # SFC operations
            insights['sfc_operations'] = sapui5_data.get('sfc_operations', [])
        
        return insights

    def generate_specific_recommendations(self, data: Dict[str, Any], insights: Dict[str, Any]) -> List:
        """Generate specific, actionable recommendations based on deep analysis"""
        if not REPORTLAB_AVAILABLE:
            return []
            
        elements = []
        
        elements.append(Paragraph("Specific Technical Recommendations", self.section_style))
        
        # 1. BaseController Optimization
        if insights['basecontroller_functions'] > 50:
            elements.append(Paragraph("1. BaseController Architecture Optimization", self.subsection_style))
            
            basecontroller_text = f"""
            <b>Current State:</b> BaseController contains {insights['basecontroller_functions']} functions, 
            making it the central hub of the application.
            
            <b>Risk Assessment:</b> High complexity and potential single point of failure.
            
            <b>Specific Recommendations:</b>
            • <b>1.1 Risk Mitigation:</b> Extract critical business logic functions (getActiveSFCInformation, 
              disassembleComponent) to dedicated Helper classes or SAPUI5 Service/Manager modules
            • <b>1.2 SFC Flow Management:</b> Centralize all SFC-related operations (completeSfc, onSubmitStartSfc) 
              from packageLabel.controller.js and qualityChain.controller.js into a unified "SfcOperationService" module
            • <b>1.3 Separation of Concerns:</b> Keep BaseController focused only on UI/Routing/General state management
            """
            
            elements.append(Paragraph(basecontroller_text, self.body_style))
            elements.append(Spacer(1, 12))
        
        # 2. Critical Error Management
        if insights['critical_error_codes']:
            elements.append(Paragraph("2. Critical Error Management Enhancement", self.subsection_style))
            
            error_text = f"""
            <b>Current State:</b> {len(insights['error_codes'])} error codes detected, including 
            {len(insights['critical_error_codes'])} critical SAP ME business errors (13xxx series).
            
            <b>Critical Error Examples:</b>
            """
            
            for error in insights['critical_error_codes'][:5]:  # Show first 5
                error_text += f"• {error['code']}: {error['message']}<br/>"
            
            error_text += """
            
            <b>Specific Recommendations:</b>
            • <b>2.1 Enhanced Error Feedback:</b> Implement specialized error handler (_showMeErrorMessage(errorCode)) 
              in BaseController that interprets error codes and provides relevant SAP ME documentation links
            • <b>2.2 SFC State Validation:</b> Add strict state checking (SFCStatusCheck Helper) before all 
              SFC operations to prevent common issues like "SFC is not in queue at operation"
            • <b>2.3 Error Context:</b> Enhance error messages with actionable steps and resolution guidance
            """
            
            elements.append(Paragraph(error_text, self.body_style))
            elements.append(Spacer(1, 12))
        
        # 3. ME API Security and Versioning
        if insights['me_api_usage']:
            elements.append(Paragraph("3. ME API Security and Versioning", self.subsection_style))
            
            api_text = f"""
            <b>Current State:</b> {sum(insights['me_api_usage'].values())} ME API calls detected across multiple controllers.
            Most frequently used APIs: {', '.join(list(insights['me_api_usage'].keys())[:5])}
            
            <b>Specific Recommendations:</b>
            • <b>3.1 API Versioning:</b> Audit all ME API calls for version compatibility and update deprecated versions
            • <b>3.2 Security Enhancement:</b> Replace hardcoded credential validation in NC Login Dialog 
              ({', '.join(insights['nc_login_controllers'])}) with secure HTTPS/SAML/OAuth2 flows
            • <b>3.3 Input Validation:</b> Implement comprehensive input sanitization for all ME API parameters
            """
            
            elements.append(Paragraph(api_text, self.body_style))
            elements.append(Spacer(1, 12))
        
        # 4. WebSocket Reliability
        if insights['websocket_usage']:
            elements.append(Paragraph("4. WebSocket Reliability Enhancement", self.subsection_style))
            
            websocket_text = """
            <b>Current State:</b> WebSocket connection detected in BaseController for real-time updates.
            
            <b>Risk Assessment:</b> Potential data loss and connection instability in production environments.
            
            <b>Specific Recommendations:</b>
            • <b>4.1 Auto-Reconnection:</b> Implement automatic reconnection logic with exponential backoff
            • <b>4.2 Message Queuing:</b> Add message queuing system to handle connection interruptions
            • <b>4.3 Health Monitoring:</b> Implement WebSocket health checks and connection status indicators
            • <b>4.4 Fallback Mechanism:</b> Provide polling-based fallback when WebSocket is unavailable
            """
            
            elements.append(Paragraph(websocket_text, self.body_style))
            elements.append(Spacer(1, 12))
        
        # 5. Performance Optimization
        elements.append(Paragraph("5. Performance and Scalability", self.subsection_style))
        
        performance_text = f"""
        <b>Current State:</b> {data['metadata']['project_name']} handles {insights['basecontroller_functions']} functions 
        and {len(insights['error_codes'])} error scenarios.
        
        <b>Specific Recommendations:</b>
        • <b>5.1 Lazy Loading:</b> Implement lazy loading for non-critical controller functions
        • <b>5.2 Caching Strategy:</b> Add intelligent caching for frequently accessed ME API responses
        • <b>5.3 Memory Management:</b> Implement proper cleanup for event listeners and WebSocket connections
        • <b>5.4 Bundle Optimization:</b> Split large controller files into smaller, focused modules
        """
        
        elements.append(Paragraph(performance_text, self.body_style))
        elements.append(Spacer(1, 12))
        
        return elements

    def generate_recommendations(self, data: Dict[str, Any], metrics: Dict[str, Any]) -> List:
        """Generate recommendations and conclusions section"""
        if not REPORTLAB_AVAILABLE:
            return []
            
        elements = []
        
        elements.append(Paragraph("Findings & Recommendations", self.section_style))
        
        # Extract specific insights
        insights = self.extract_specific_insights(data)
        
        # Code Quality Assessment
        elements.append(Paragraph("Code Quality Assessment", self.subsection_style))
        
        quality_text = f"""
        The analysis reveals a well-structured SAPUI5/Fiori application with strong architectural patterns:
        
        <b>Strengths:</b>
        • Comprehensive controller architecture with {metrics['controllers']} controllers
        • Extensive function library with {metrics['functions']} total functions
        • Strong SAP ME/MII integration with {metrics['sap_me_apis']} API calls
        • Robust SFC operations with {metrics['sfc_operations']} operations
        • Complete internationalization support with {metrics['i18n_keys']} translation keys
        • Sophisticated error handling with {len(insights['error_codes'])} error scenarios
        
        <b>Critical Areas for Improvement:</b>
        • BaseController complexity ({insights['basecontroller_functions']} functions) requires refactoring
        • {len(insights['critical_error_codes'])} critical SAP ME error codes need enhanced handling
        • ME API security and versioning requires immediate attention
        • WebSocket reliability needs strengthening for production stability
        """
        
        elements.append(Paragraph(quality_text, self.body_style))
        elements.append(Spacer(1, 12))
        
        # Add specific technical recommendations
        elements.extend(self.generate_specific_recommendations(data, insights))
        
        # Implementation Priority
        elements.append(Paragraph("Implementation Priority Matrix", self.subsection_style))
        
        priority_text = """
        <b>High Priority (Immediate Action Required):</b>
        1. BaseController refactoring and SFC operation centralization
        2. Critical error code handling enhancement (13xxx series)
        3. ME API security improvements and credential management
        
        <b>Medium Priority (Next Sprint):</b>
        4. WebSocket reliability and auto-reconnection
        5. Performance optimization and caching implementation
        
        <b>Low Priority (Future Enhancement):</b>
        6. Advanced monitoring and analytics
        7. Additional unit testing coverage
        """
        
        elements.append(Paragraph(priority_text, self.body_style))
        elements.append(Spacer(1, 20))
        
        # Conclusion
        elements.append(Paragraph("Conclusion", self.subsection_style))
        
        conclusion_text = f"""
        The {data['metadata']['project_name']} project demonstrates a sophisticated implementation of SAP ME/MII 
        integration within a modern SAPUI5/Fiori application. While the analysis reveals strong architectural 
        patterns and comprehensive ME/MII integration, the identified specific recommendations address critical 
        production risks and provide clear, actionable steps for improvement.
        
        <b>Key Success Factors:</b>
        • Immediate attention to BaseController complexity and error handling
        • Implementation of security best practices for ME API interactions
        • Enhancement of real-time communication reliability
        
        These targeted improvements will significantly enhance the application's maintainability, security, 
        and production stability while preserving its strong architectural foundation.
        """
        
        elements.append(Paragraph(conclusion_text, self.body_style))
        
        return elements

    def generate_pdf_report(self, analysis_dir: Path, output_filename: str = None) -> Path:
        """Generate complete PDF report"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")
        
        if output_filename is None:
            output_filename = f"{analysis_dir.name}_Analysis_Report.pdf"
        
        output_path = self.output_dir / output_filename
        
        # Load analysis data
        data = self.load_analysis_data(analysis_dir)
        metrics = self.extract_metrics(data)
        
        # Create PDF document
        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        elements = []
        
        # Generate all sections
        elements.extend(self.generate_executive_summary(data, metrics))
        elements.extend(self.generate_architecture_section(data))
        elements.extend(self.generate_me_mii_analysis(data))
        elements.extend(self.generate_ui_analysis(data))
        elements.extend(self.generate_recommendations(data, metrics))
        
        # Build PDF
        doc.build(elements)
        
        return output_path
    
    def generate_documentation_pdf(self, analysis_dir: Path, output_filename: str = None) -> Path:
        """Generate Documentation Agent PDF report"""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")
        
        # Determine output filename
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"Documentation_Report_{timestamp}.pdf"
        
        output_path = self.output_dir / output_filename
        
        # Load documentation data
        doc_dir = analysis_dir / 'documentation'
        if not doc_dir.exists():
            raise ValueError(f"No documentation found in {doc_dir}")
        
        # Create PDF document
        doc = SimpleDocTemplate(str(output_path), pagesize=A4)
        elements = []
        
        # Generate documentation sections
        elements.extend(self.generate_documentation_header())
        elements.extend(self.generate_training_material_section(doc_dir))
        elements.extend(self.generate_qa_scenarios_section(doc_dir))
        elements.extend(self.generate_documentation_summary(doc_dir))
        
        # Build PDF
        doc.build(elements)
        
        print(f"Documentation PDF report generated successfully: {output_path}")
        return output_path
    
    def generate_documentation_header(self) -> List:
        """Generate documentation header section"""
        if not REPORTLAB_AVAILABLE:
            return []
            
        elements = []
        
        # Title
        elements.append(Paragraph("📚 Documentation Agent Report", self.title_style))
        elements.append(Spacer(1, 20))
        
        # Subtitle
        elements.append(Paragraph("Technical Training Material & QA Test Scenarios", self.section_style))
        elements.append(Spacer(1, 20))
        
        # Generation info
        generation_info = f"""
        <b>Generated on:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Report Type:</b> Documentation Package<br/>
        <b>Content:</b> Training Material, QA Scenarios, Implementation Guidelines
        """
        
        elements.append(Paragraph(generation_info, self.body_style))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def generate_training_material_section(self, doc_dir: Path) -> List:
        """Generate training material section"""
        if not REPORTLAB_AVAILABLE:
            return []
            
        elements = []
        
        elements.append(Paragraph("🎓 Technical Training Material", self.section_style))
        elements.append(Spacer(1, 12))
        
        # Load training material
        training_path = doc_dir / 'TRAINING_MATERIAL.md'
        if training_path.exists():
            training_content = training_path.read_text(encoding='utf-8')
            
            # Split content into sections
            sections = training_content.split('#')
            
            for section in sections[1:]:  # Skip empty first section
                lines = section.strip().split('\n')
                if not lines:
                    continue
                    
                # Section title
                title = lines[0].strip()
                elements.append(Paragraph(f"<b>{title}</b>", self.subsection_style))
                elements.append(Spacer(1, 8))
                
                # Section content
                content = '\n'.join(lines[1:]).strip()
                if content:
                    # Clean up markdown formatting
                    content = content.replace('**', '<b>').replace('**', '</b>')
                    content = content.replace('*', '<i>').replace('*', '</i>')
                    content = content.replace('`', '<font name="Courier">').replace('`', '</font>')
                    
                    elements.append(Paragraph(content, self.body_style))
                    elements.append(Spacer(1, 12))
        else:
            elements.append(Paragraph("Training material not found.", self.body_style))
        
        elements.append(PageBreak())
        return elements
    
    def generate_qa_scenarios_section(self, doc_dir: Path) -> List:
        """Generate QA scenarios section"""
        if not REPORTLAB_AVAILABLE:
            return []
            
        elements = []
        
        elements.append(Paragraph("🧪 QA Test Scenarios", self.section_style))
        elements.append(Spacer(1, 12))
        
        # Load QA scenarios
        qa_path = doc_dir / 'QA_TEST_SCENARIOS.md'
        if qa_path.exists():
            qa_content = qa_path.read_text(encoding='utf-8')
            
            # Extract test scenarios table
            lines = qa_content.split('\n')
            in_table = False
            test_scenarios = []
            
            for line in lines:
                if '| Test ID |' in line:
                    in_table = True
                    continue
                elif in_table and line.startswith('|'):
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 6 and parts[1]:  # Valid test row
                        test_scenarios.append({
                            'id': parts[1],
                            'scenario': parts[2],
                            'focus': parts[3],
                            'controller': parts[4],
                            'priority': parts[5],
                            'result': parts[6] if len(parts) > 6 else ''
                        })
                elif in_table and not line.startswith('|'):
                    break
            
            # Create test scenarios table
            if test_scenarios:
                elements.append(Paragraph("Test Scenarios Overview", self.subsection_style))
                elements.append(Spacer(1, 8))
                
                # Table data
                table_data = [['Test ID', 'Scenario', 'Priority', 'Focus Area']]
                for test in test_scenarios[:10]:  # Show first 10
                    table_data.append([
                        test['id'],
                        test['scenario'][:50] + '...' if len(test['scenario']) > 50 else test['scenario'],
                        test['priority'],
                        test['focus'][:30] + '...' if len(test['focus']) > 30 else test['focus']
                    ])
                
                # Create table
                table = Table(table_data, colWidths=[1*inch, 3*inch, 1*inch, 2*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 20))
                
                # Priority summary
                priority_counts = {}
                for test in test_scenarios:
                    priority = test['priority']
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                priority_text = f"""
                <b>Priority Distribution:</b><br/>
                • High Priority: {priority_counts.get('Yüksek', 0)} tests<br/>
                • Medium Priority: {priority_counts.get('Orta', 0)} tests<br/>
                • Low Priority: {priority_counts.get('Düşük', 0)} tests<br/>
                • Total Tests: {len(test_scenarios)}
                """
                
                elements.append(Paragraph(priority_text, self.body_style))
                elements.append(Spacer(1, 12))
        else:
            elements.append(Paragraph("QA scenarios not found.", self.body_style))
        
        elements.append(PageBreak())
        return elements
    
    def generate_documentation_summary(self, doc_dir: Path) -> List:
        """Generate documentation summary section"""
        if not REPORTLAB_AVAILABLE:
            return []
            
        elements = []
        
        elements.append(Paragraph("📋 Documentation Summary", self.section_style))
        elements.append(Spacer(1, 12))
        
        # Load summary
        summary_path = doc_dir / 'DOCUMENTATION_SUMMARY.md'
        if summary_path.exists():
            summary_content = summary_path.read_text(encoding='utf-8')
            
            # Simple text processing - remove markdown formatting
            summary_content = summary_content.replace('#', '').replace('*', '').replace('**', '')
            summary_content = summary_content.replace('`', '').replace('##', '').replace('###', '')
            
            elements.append(Paragraph(summary_content, self.body_style))
        else:
            elements.append(Paragraph("Documentation summary not found.", self.body_style))
        
        elements.append(Spacer(1, 20))
        
        # Usage guidelines
        usage_text = """
        <b>Usage Guidelines:</b><br/>
        • Use Training Material for developer onboarding and knowledge transfer<br/>
        • Use QA Scenarios for testing and validation of changes<br/>
        • Review Implementation Guidelines for best practices<br/>
        • Update documentation as the system evolves
        """
        
        elements.append(Paragraph(usage_text, self.body_style))
        
        return elements

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate professional PDF reports for SAP ME/MII analysis')
    parser.add_argument('--analysis-dir', required=True, help='Directory containing analysis outputs')
    parser.add_argument('--output-dir', default='./pdf_reports', help='Output directory for PDF reports')
    parser.add_argument('--output-name', help='Custom output filename for PDF')
    parser.add_argument('--type', choices=['analysis', 'documentation'], default='analysis', 
                       help='Type of PDF report to generate')
    
    args = parser.parse_args()
    
    analysis_dir = Path(args.analysis_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    if not analysis_dir.exists():
        print(f"Analysis directory not found: {analysis_dir}")
        return
    
    try:
        generator = SAPMEIIPDFGenerator(output_dir)
        
        if args.type == 'documentation':
            pdf_path = generator.generate_documentation_pdf(analysis_dir, args.output_name)
        else:
            pdf_path = generator.generate_pdf_report(analysis_dir, args.output_name)
            
        print(f"PDF report generated successfully: {pdf_path}")
    except Exception as e:
        print(f"Error generating PDF report: {e}")

if __name__ == "__main__":
    main()
