"""
AI Agent Visualization App for SAP ME/MII Analysis
- Interactive visualization of analysis results
- RAG Agent integration with visual outputs
- Real-time chat interface
- Advanced charts and graphs
"""

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any
import re
from datetime import datetime

# Import our existing modules
from pdf_report_generator import SAPMEIIPDFGenerator
from rag_consultant import ask as rag_ask

# Page configuration
st.set_page_config(
    page_title="AI Agent Visualization - SAP ME/MII",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .ai-response {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class AIVisualizationApp:
    """AI-powered visualization application for SAP ME/MII analysis"""
    
    def __init__(self):
        self.analysis_data = {}
        self.rag_responses = []
        
    def load_analysis_data(self, analysis_dir: Path):
        """Load analysis data from directory"""
        try:
            # Load JSON data
            json_path = analysis_dir / 'sapui5_deep_analysis.json'
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.analysis_data = json.load(f)
            
            # Load summary data
            summary_path = analysis_dir / 'ADVANCED_SUMMARY.md'
            if summary_path.exists():
                self.summary_text = summary_path.read_text(encoding='utf-8')
            else:
                self.summary_text = "Summary not available"
                
            return True
        except Exception as e:
            st.error(f"Error loading analysis data: {e}")
            return False
    
    def create_metrics_cards(self):
        """Create metric cards for key statistics"""
        if not self.analysis_data:
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            controllers = len(self.analysis_data.get('controllers', []))
            st.markdown(f"""
            <div class="metric-card">
                <h3>🎮 Controllers</h3>
                <h1>{controllers}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            views = len(self.analysis_data.get('views', []))
            st.markdown(f"""
            <div class="metric-card">
                <h3>📱 Views</h3>
                <h1>{views}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            functions = sum(len(ctrl.get('functions', [])) for ctrl in self.analysis_data.get('controllers', []))
            st.markdown(f"""
            <div class="metric-card">
                <h3>⚙️ Functions</h3>
                <h1>{functions}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            me_apis = len(self.analysis_data.get('sap_me_apis', []))
            st.markdown(f"""
            <div class="metric-card">
                <h3>🏭 ME APIs</h3>
                <h1>{me_apis}</h1>
            </div>
            """, unsafe_allow_html=True)
    
    def create_ui_components_chart(self):
        """Create UI components visualization"""
        if not self.analysis_data:
            st.warning("No analysis data available")
            return
        
        sapui5_data = self.analysis_data
        if 'ui_components' not in sapui5_data:
            st.warning("No UI components data available")
            return
        
        ui_data = sapui5_data['ui_components']
        
        # Manual count if data is incorrect
        if sum(ui_data.values()) == 0:
            st.warning("⚠️ UI components data appears to be incorrect. Calculating manually...")
            
            # Count buttons manually
            button_count = 0
            table_count = 0
            input_count = 0
            
            # Count from controllers
            for ctrl in sapui5_data.get('controllers', []):
                functions = ctrl.get('functions', [])
                for func in functions:
                    if 'Button' in func:
                        button_count += 1
            
            # Count from views
            for view in sapui5_data.get('views', []):
                controls = view.get('controls', [])
                for control in controls:
                    if control.get('type') == 'Button':
                        button_count += 1
                    elif control.get('type') == 'Table':
                        table_count += 1
                    elif control.get('type') in ['Input', 'TextField']:
                        input_count += 1
            
            # Update UI data
            ui_data = {
                'buttons': button_count,
                'tables': table_count,
                'inputs': input_count,
                'forms': 0,
                'dialogs': 0
            }
            
            st.info(f"✅ Manual count: {button_count} buttons, {table_count} tables, {input_count} inputs")
        
        # Prepare data for plotting
        components = list(ui_data.keys())
        values = list(ui_data.values())
        
        # Create horizontal bar chart
        fig = px.bar(
            x=values,
            y=components,
            orientation='h',
            title="🎨 UI Components Distribution",
            color=values,
            color_continuous_scale='viridis',
            text=values
        )
        
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Count",
            yaxis_title="Component Type"
        )
        
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_controller_analysis(self):
        """Create controller analysis visualization"""
        if 'controllers' not in self.analysis_data:
            return
        
        controllers = self.analysis_data['controllers']
        
        # Prepare data
        controller_data = []
        for ctrl in controllers:
            filename = Path(ctrl.get('file', '')).name
            functions = len(ctrl.get('functions', []))
            events = len(ctrl.get('event_handlers', []))
            api_calls = len(ctrl.get('api_calls', []))
            
            controller_data.append({
                'Controller': filename,
                'Functions': functions,
                'Event Handlers': events,
                'API Calls': api_calls
            })
        
        df = pd.DataFrame(controller_data)
        
        # Create subplot
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Functions per Controller', 'Event Handlers per Controller', 
                          'API Calls per Controller', 'Controller Complexity'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Functions chart
        fig.add_trace(
            go.Bar(x=df['Controller'], y=df['Functions'], name='Functions', marker_color='lightblue'),
            row=1, col=1
        )
        
        # Event handlers chart
        fig.add_trace(
            go.Bar(x=df['Controller'], y=df['Event Handlers'], name='Event Handlers', marker_color='lightgreen'),
            row=1, col=2
        )
        
        # API calls chart
        fig.add_trace(
            go.Bar(x=df['Controller'], y=df['API Calls'], name='API Calls', marker_color='lightcoral'),
            row=2, col=1
        )
        
        # Complexity scatter plot
        fig.add_trace(
            go.Scatter(
                x=df['Functions'], 
                y=df['Event Handlers'],
                mode='markers+text',
                text=df['Controller'],
                textposition='top center',
                name='Complexity',
                marker=dict(size=df['API Calls']*2+10, color=df['API Calls'], colorscale='viridis')
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False, title_text="🎮 Controller Analysis Dashboard")
        st.plotly_chart(fig, use_container_width=True)
    
    def create_navigation_flow(self):
        """Create navigation flow visualization"""
        if 'navigation_flow' not in self.analysis_data:
            return
        
        nav_flow = self.analysis_data['navigation_flow']
        
        # Create Mermaid diagram
        mermaid_code = """
        graph TD
        """
        
        # Add navigation nodes
        for nav in nav_flow[:10]:  # Limit to first 10
            if 'View' in nav:
                mermaid_code += f"\n    {nav.replace('View', '')}({nav})"
        
        # Add connections (simplified)
        mermaid_code += "\n    Home --> Panel"
        mermaid_code += "\n    Home --> Traceability"
        mermaid_code += "\n    Home --> PackageLabel"
        mermaid_code += "\n    Home --> QualityChain"
        mermaid_code += "\n    Home --> Repair"
        mermaid_code += "\n    Home --> Confirmation"
        mermaid_code += "\n    Home --> Transfer"
        mermaid_code += "\n    Home --> TypeLabel"
        
        mermaid_code += """
        
        style Home fill:#ADD8E6,stroke:#333,stroke-width:2px
        style Panel fill:#90EE90,stroke:#333
        style Traceability fill:#90EE90,stroke:#333
        style PackageLabel fill:#90EE90,stroke:#333
        style QualityChain fill:#90EE90,stroke:#333
        style Repair fill:#90EE90,stroke:#333
        style Confirmation fill:#90EE90,stroke:#333
        style Transfer fill:#90EE90,stroke:#333
        style TypeLabel fill:#90EE90,stroke:#333
        """
        
        st.subheader("🗺️ Application Navigation Flow")
        st.code(mermaid_code, language='mermaid')
        
        # Also show as a simple list
        st.subheader("📋 Navigation Routes")
        for i, nav in enumerate(nav_flow, 1):
            st.write(f"{i}. {nav}")
    
    def create_me_mii_analysis(self):
        """Create ME/MII specific analysis visualization"""
        if not self.analysis_data:
            return
        
        # SAP ME API Usage
        if 'sap_me_apis' in self.analysis_data and self.analysis_data['sap_me_apis']:
            st.subheader("🏭 SAP ME API Usage Analysis")
            
            # Count API usage
            api_counts = {}
            for api in self.analysis_data['sap_me_apis']:
                class_name = api.get('class', 'Unknown')
                api_counts[class_name] = api_counts.get(class_name, 0) + 1
            
            # Create pie chart
            api_df = pd.DataFrame(list(api_counts.items()), columns=['API Class', 'Usage Count'])
            api_df = api_df.sort_values('Usage Count', ascending=False).head(10)
            
            fig = px.pie(
                api_df, 
                values='Usage Count', 
                names='API Class',
                title="SAP ME API Usage Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed table
            st.subheader("📊 API Usage Details")
            st.dataframe(api_df, use_container_width=True)
        
        # SFC Operations
        if 'sfc_operations' in self.analysis_data and self.analysis_data['sfc_operations']:
            st.subheader("⚙️ SFC/Order/Resource Operations")
            
            # Count SFC operations
            sfc_counts = {}
            for sfc in self.analysis_data['sfc_operations']:
                operation = sfc.get('operation', 'Unknown')
                op_type = operation.split('=')[0].strip() if '=' in operation else operation
                sfc_counts[op_type] = sfc_counts.get(op_type, 0) + 1
            
            # Create bar chart
            sfc_df = pd.DataFrame(list(sfc_counts.items()), columns=['Operation Type', 'Count'])
            sfc_df = sfc_df.sort_values('Count', ascending=False).head(10)
            
            fig = px.bar(
                sfc_df,
                x='Count',
                y='Operation Type',
                orientation='h',
                title="SFC Operations Distribution",
                color='Count',
                color_continuous_scale='blues'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def create_rag_chat_interface(self, analysis_dir: Path):
        """Create RAG chat interface"""
        st.subheader("🤖 AI Agent Chat Interface")
        
        # Chat input
        user_question = st.chat_input("Ask the AI agent about the analysis...")
        
        if user_question:
            # Add user message to chat
            st.chat_message("user").write(user_question)
            
            # Get AI response
            with st.spinner("AI agent is thinking..."):
                try:
                    ai_response = rag_ask(user_question, output_dir=str(analysis_dir))
                    
                    # Add AI response to chat
                    with st.chat_message("assistant"):
                        st.markdown(f"""
                        <div class="ai-response">
                            <h4>🧠 AI Agent Response:</h4>
                            <p>{ai_response}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Store in session state
                    if 'chat_history' not in st.session_state:
                        st.session_state.chat_history = []
                    
                    st.session_state.chat_history.append({
                        'user': user_question,
                        'ai': ai_response,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    
                except Exception as e:
                    st.error(f"Error getting AI response: {e}")
        
        # Show chat history
        if 'chat_history' in st.session_state and st.session_state.chat_history:
            st.subheader("💬 Chat History")
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5
                with st.expander(f"Chat {len(st.session_state.chat_history)-i} - {chat['timestamp']}"):
                    st.write(f"**User:** {chat['user']}")
                    st.write(f"**AI:** {chat['ai']}")
    
    def create_data_flow_diagram(self):
        """Create data flow diagram"""
        st.subheader("🔄 Data Flow Diagram")
        
        # Create a simple data flow using Mermaid
        data_flow_code = """
        graph LR
            A[User Interface] --> B[Controllers]
            B --> C[BaseController]
            C --> D[SAP ME APIs]
            C --> E[SFC Operations]
            D --> F[Manufacturing Data]
            E --> F
            F --> G[Database]
            C --> H[WebSocket]
            H --> I[Real-time Updates]
            I --> A
            
            style A fill:#e1f5fe
            style B fill:#f3e5f5
            style C fill:#fff3e0
            style D fill:#e8f5e8
            style E fill:#e8f5e8
            style F fill:#fce4ec
            style G fill:#f1f8e9
            style H fill:#e0f2f1
            style I fill:#fff8e1
        """
        
        st.code(data_flow_code, language='mermaid')
    
    def create_technical_recommendations(self):
        """Create technical recommendations section"""
        if not self.analysis_data:
            st.warning("No analysis data available")
            return
        
        # Extract insights
        insights = self.extract_specific_insights()
        
        # 1. BaseController Analysis
        if insights['basecontroller_functions'] > 50:
            st.subheader("🏗️ 1. BaseController Architecture Optimization")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                **Current State:** BaseController contains {insights['basecontroller_functions']} functions, 
                making it the central hub of the application.
                
                **Risk Assessment:** High complexity and potential single point of failure.
                """)
            
            with col2:
                st.metric("Functions", insights['basecontroller_functions'], delta="High Risk")
            
            st.markdown("**Specific Recommendations:**")
            st.markdown("""
            • **1.1 Risk Mitigation:** Extract critical business logic functions (getActiveSFCInformation, 
              disassembleComponent) to dedicated Helper classes or SAPUI5 Service/Manager modules
            • **1.2 SFC Flow Management:** Centralize all SFC-related operations (completeSfc, onSubmitStartSfc) 
              from packageLabel.controller.js and qualityChain.controller.js into a unified "SfcOperationService" module
            • **1.3 Separation of Concerns:** Keep BaseController focused only on UI/Routing/General state management
            """)
            
            st.info("🚨 **Priority:** High - Immediate action required to reduce complexity and improve maintainability")
        
        # 2. Error Management
        if insights['critical_error_codes']:
            st.subheader("⚠️ 2. Critical Error Management Enhancement")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                **Current State:** {len(insights['error_codes'])} error codes detected, including 
                {len(insights['critical_error_codes'])} critical SAP ME business errors (13xxx series).
                """)
            
            with col2:
                st.metric("Critical Errors", len(insights['critical_error_codes']), delta="High Risk")
            
            # Show critical error examples
            st.markdown("**Critical Error Examples:**")
            error_df = pd.DataFrame(insights['critical_error_codes'][:5])
            if not error_df.empty:
                st.dataframe(error_df, use_container_width=True)
            
            st.markdown("**Specific Recommendations:**")
            st.markdown("""
            • **2.1 Enhanced Error Feedback:** Implement specialized error handler (_showMeErrorMessage(errorCode)) 
              in BaseController that interprets error codes and provides relevant SAP ME documentation links
            • **2.2 SFC State Validation:** Add strict state checking (SFCStatusCheck Helper) before all 
              SFC operations to prevent common issues like "SFC is not in queue at operation"
            • **2.3 Error Context:** Enhance error messages with actionable steps and resolution guidance
            """)
            
            st.warning("🚨 **Priority:** High - Critical for production stability and user experience")
        
        # 3. ME API Security
        if insights['me_api_usage']:
            st.subheader("🔐 3. ME API Security and Versioning")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                **Current State:** {sum(insights['me_api_usage'].values())} ME API calls detected across multiple controllers.
                Most frequently used APIs: {', '.join(list(insights['me_api_usage'].keys())[:5])}
                """)
            
            with col2:
                st.metric("API Calls", sum(insights['me_api_usage'].values()))
            
            # Show API usage chart
            api_df = pd.DataFrame(list(insights['me_api_usage'].items()), columns=['API Class', 'Usage Count'])
            api_df = api_df.sort_values('Usage Count', ascending=False).head(10)
            
            fig = px.bar(
                api_df,
                x='Usage Count',
                y='API Class',
                orientation='h',
                title="ME API Usage Distribution",
                color='Usage Count',
                color_continuous_scale='reds'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("**Specific Recommendations:**")
            st.markdown("""
            • **3.1 API Versioning:** Audit all ME API calls for version compatibility and update deprecated versions
            • **3.2 Security Enhancement:** Replace hardcoded credential validation in NC Login Dialog 
              with secure HTTPS/SAML/OAuth2 flows
            • **3.3 Input Validation:** Implement comprehensive input sanitization for all ME API parameters
            """)
            
            st.error("🚨 **Priority:** High - Security vulnerabilities require immediate attention")
        
        # 4. WebSocket Reliability
        if insights['websocket_usage']:
            st.subheader("🌐 4. WebSocket Reliability Enhancement")
            
            st.markdown("""
            **Current State:** WebSocket connection detected in BaseController for real-time updates.
            
            **Risk Assessment:** Potential data loss and connection instability in production environments.
            """)
            
            st.markdown("**Specific Recommendations:**")
            st.markdown("""
            • **4.1 Auto-Reconnection:** Implement automatic reconnection logic with exponential backoff
            • **4.2 Message Queuing:** Add message queuing system to handle connection interruptions
            • **4.3 Health Monitoring:** Implement WebSocket health checks and connection status indicators
            • **4.4 Fallback Mechanism:** Provide polling-based fallback when WebSocket is unavailable
            """)
            
            st.info("⚠️ **Priority:** Medium - Important for production reliability")
        
        # 5. Implementation Priority Matrix
        st.subheader("📋 Implementation Priority Matrix")
        
        priority_data = {
            'Priority': ['High', 'High', 'High', 'Medium', 'Medium', 'Low', 'Low'],
            'Task': [
                'BaseController refactoring',
                'Critical error handling',
                'ME API security',
                'WebSocket reliability',
                'Performance optimization',
                'Advanced monitoring',
                'Unit testing coverage'
            ],
            'Timeline': ['Immediate', 'Immediate', 'Immediate', 'Next Sprint', 'Next Sprint', 'Future', 'Future']
        }
        
        priority_df = pd.DataFrame(priority_data)
        
        # Color code by priority
        def highlight_priority(row):
            if row['Priority'] == 'High':
                return ['background-color: #ffebee'] * len(row)
            elif row['Priority'] == 'Medium':
                return ['background-color: #fff3e0'] * len(row)
            else:
                return ['background-color: #f3e5f5'] * len(row)
        
        st.dataframe(
            priority_df.style.apply(highlight_priority, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        # Summary
        st.subheader("🎯 Summary")
        st.markdown(f"""
        **Key Findings:**
        - BaseController complexity: {insights['basecontroller_functions']} functions
        - Critical error codes: {len(insights['critical_error_codes'])} requiring immediate attention
        - ME API calls: {sum(insights['me_api_usage'].values())} needing security review
        - WebSocket usage: {'Yes' if insights['websocket_usage'] else 'No'}
        
        **Next Steps:**
        1. Focus on high-priority items first
        2. Implement BaseController refactoring
        3. Enhance error handling for critical scenarios
        4. Review and secure ME API interactions
        """)
    
    def extract_specific_insights(self):
        """Extract specific insights from analysis data"""
        insights = {
            'basecontroller_functions': 0,
            'error_codes': [],
            'critical_error_codes': [],
            'me_api_usage': {},
            'websocket_usage': False,
            'nc_login_controllers': [],
            'sfc_operations': []
        }
        
        if self.analysis_data:
            sapui5_data = self.analysis_data
            
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
    
    def run(self, analysis_dir: Path):
        """Run the AI visualization app"""
        # Load data
        if not self.load_analysis_data(analysis_dir):
            st.error("Failed to load analysis data")
            return
        
        # Main header
        st.markdown('<h1 class="main-header">🧠 AI Agent Visualization Dashboard</h1>', unsafe_allow_html=True)
        
        # Sidebar
        with st.sidebar:
            st.markdown("## 🎛️ Dashboard Controls")
            
            # Analysis selection
            analysis_options = ["Overview", "Controllers", "UI Components", "ME/MII Analysis", "Navigation", "Technical Recommendations", "AI Chat"]
            selected_analysis = st.selectbox("Select Analysis View", analysis_options)
            
            # Refresh button
            if st.button("🔄 Refresh Data"):
                st.rerun()
            
            # Export options
            st.markdown("## 📤 Export Options")
            if st.button("📄 Generate PDF Report"):
                try:
                    pdf_dir = Path("./pdf_reports")
                    pdf_dir.mkdir(exist_ok=True)
                    
                    generator = SAPMEIIPDFGenerator(pdf_dir)
                    pdf_path = generator.generate_pdf_report(analysis_dir, f"{analysis_dir.name}_AI_Report.pdf")
                    
                    st.success("PDF report generated!")
                    
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_file.read(),
                            file_name=pdf_path.name,
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"Error generating PDF: {e}")
        
        # Main content based on selection
        if selected_analysis == "Overview":
            st.header("📊 Project Overview")
            self.create_metrics_cards()
            
            col1, col2 = st.columns(2)
            with col1:
                self.create_ui_components_chart()
            with col2:
                self.create_data_flow_diagram()
        
        elif selected_analysis == "Controllers":
            st.header("🎮 Controller Analysis")
            self.create_controller_analysis()
        
        elif selected_analysis == "UI Components":
            st.header("🎨 UI Components Analysis")
            self.create_ui_components_chart()
        
        elif selected_analysis == "ME/MII Analysis":
            st.header("🏭 ME/MII Integration Analysis")
            self.create_me_mii_analysis()
        
        elif selected_analysis == "Navigation":
            st.header("🗺️ Navigation Analysis")
            self.create_navigation_flow()
        
        elif selected_analysis == "Technical Recommendations":
            st.header("💡 Technical Recommendations")
            self.create_technical_recommendations()
        
        elif selected_analysis == "AI Chat":
            st.header("🤖 AI Agent Chat")
            self.create_rag_chat_interface(analysis_dir)
        
        # Footer
        st.markdown("---")
        st.markdown("**🧠 AI Agent Visualization Dashboard** - Powered by Streamlit & Plotly")

def main():
    """Main function"""
    app = AIVisualizationApp()
    
    # Get analysis directory
    analysis_dir = Path("./tvmes_enhanced_analysis")
    
    if not analysis_dir.exists():
        st.error(f"Analysis directory not found: {analysis_dir}")
        st.info("Please run the analysis first using me_mii_analyzer_advanced.py")
        return
    
    app.run(analysis_dir)

if __name__ == "__main__":
    main()
