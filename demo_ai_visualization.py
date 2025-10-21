"""
Demo script for AI Visualization
- Quick demonstration of AI visualization features
- Sample data generation
- Interactive charts showcase
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="AI Visualization Demo",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .demo-header {
        font-size: 2.5rem;
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
</style>
""", unsafe_allow_html=True)

def create_demo_metrics():
    """Create demo metric cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🎮 Controllers</h3>
            <h1>12</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📱 Views</h3>
            <h1>9</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>⚙️ Functions</h3>
            <h1>91</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🏭 ME APIs</h3>
            <h1>47</h1>
        </div>
        """, unsafe_allow_html=True)

def create_demo_ui_chart():
    """Create demo UI components chart"""
    ui_data = {
        'Component': ['Buttons', 'Tables/Lists', 'Input Fields', 'Forms', 'Dialogs'],
        'Count': [48, 32, 14, 0, 0]  # Gerçek TVMES verilerine göre güncellendi
    }
    
    df = pd.DataFrame(ui_data)
    
    fig = px.bar(
        df,
        x='Count',
        y='Component',
        orientation='h',
        title="🎨 UI Components Distribution",
        color='Count',
        color_continuous_scale='viridis',
        text='Count'
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Count",
        yaxis_title="Component Type"
    )
    
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    
    return fig

def create_demo_controller_analysis():
    """Create demo controller analysis"""
    controller_data = {
        'Controller': ['BaseController.js', 'App.controller.js', 'Home.controller.js', 
                      'confirmation.controller.js', 'NotFound.controller.js'],
        'Functions': [91, 7, 9, 5, 2],
        'Event Handlers': [15, 4, 5, 5, 2],
        'API Calls': [23, 0, 3, 2, 0]
    }
    
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
    return fig

def create_demo_me_mii_analysis():
    """Create demo ME/MII analysis"""
    # SAP ME API Usage
    api_data = {
        'API Class': ['split', 'response', 'getSelectedKey', 'attachChange', 'null', 'detachChange'],
        'Usage Count': [63, 47, 28, 16, 10, 4]
    }
    
    api_df = pd.DataFrame(api_data)
    
    fig1 = px.pie(
        api_df, 
        values='Usage Count', 
        names='API Class',
        title="🏭 SAP ME API Usage Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # SFC Operations
    sfc_data = {
        'Operation Type': ['resource', 'Resource', 'Sfc', 'WorkCenter', 'sfc', 'SFC'],
        'Count': [35, 22, 18, 11, 9, 9]
    }
    
    sfc_df = pd.DataFrame(sfc_data)
    
    fig2 = px.bar(
        sfc_df,
        x='Count',
        y='Operation Type',
        orientation='h',
        title="⚙️ SFC Operations Distribution",
        color='Count',
        color_continuous_scale='blues'
    )
    
    return fig1, fig2

def create_demo_navigation():
    """Create demo navigation flow"""
    mermaid_code = """
    graph TD
        Home(Home.controller.js) --> PNL(panelView)
        Home --> TRC(traceabilityView)
        Home --> PCL(packageLabelView)
        Home --> QLC(qualityChainView)
        Home --> RFU(repairView)
        Home --> CFV(confirmationView)
        Home --> TRF(transferView)
        Home --> TPL(typeLabelView)

        style Home fill:#ADD8E6,stroke:#333,stroke-width:2px
        style PNL fill:#90EE90,stroke:#333
        style TRC fill:#90EE90,stroke:#333
        style PCL fill:#90EE90,stroke:#333
        style QLC fill:#90EE90,stroke:#333
        style RFU fill:#90EE90,stroke:#333
        style CFV fill:#90EE90,stroke:#333
        style TRF fill:#90EE90,stroke:#333
        style TPL fill:#90EE90,stroke:#333
    """
    
    return mermaid_code

def main():
    """Main demo function"""
    st.markdown('<h1 class="demo-header">🧠 AI Agent Visualization Demo</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎛️ Demo Controls")
        
        demo_options = ["Overview", "Controllers", "UI Components", "ME/MII Analysis", "Navigation"]
        selected_demo = st.selectbox("Select Demo View", demo_options)
        
        st.markdown("## 📊 Sample Data")
        st.info("This demo uses sample data from TVMES project analysis")
    
    # Main content
    if selected_demo == "Overview":
        st.header("📊 Project Overview")
        create_demo_metrics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_demo_ui_chart(), use_container_width=True)
        with col2:
            st.subheader("🔄 Data Flow")
            st.code(create_demo_navigation(), language='mermaid')
    
    elif selected_demo == "Controllers":
        st.header("🎮 Controller Analysis")
        st.plotly_chart(create_demo_controller_analysis(), use_container_width=True)
    
    elif selected_demo == "UI Components":
        st.header("🎨 UI Components Analysis")
        st.plotly_chart(create_demo_ui_chart(), use_container_width=True)
    
    elif selected_demo == "ME/MII Analysis":
        st.header("🏭 ME/MII Integration Analysis")
        fig1, fig2 = create_demo_me_mii_analysis()
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.plotly_chart(fig2, use_container_width=True)
    
    elif selected_demo == "Navigation":
        st.header("🗺️ Navigation Analysis")
        st.subheader("Application Navigation Flow")
        st.code(create_demo_navigation(), language='mermaid')
        
        st.subheader("📋 Navigation Routes")
        routes = [
            "appHome", "panelView", "traceabilityView", "typeLabelView", 
            "repairView", "qualityChainView", "confirmationView", 
            "transferView", "packageLabelView"
        ]
        
        for i, route in enumerate(routes, 1):
            st.write(f"{i}. {route}")
    
    # Footer
    st.markdown("---")
    st.markdown("**🧠 AI Agent Visualization Demo** - Powered by Streamlit & Plotly")
    st.info("🚀 Full AI Dashboard: py -m streamlit run ai_visualization_app.py --server.port 8502")

if __name__ == "__main__":
    main()
