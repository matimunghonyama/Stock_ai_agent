"""
Financial AI Agent - Main Streamlit Application
"""
import streamlit as st
import groq
import os
from datetime import datetime
from typing import Optional
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

from agents.orchestrator import AgentOrchestrator
from tools.pdf_processor import extract_json_from_response, extract_recommendation

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Financial AI Agent | Investment Analysis",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, #1e88e5, #00acc1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .recommendation-buy {
        background: #22c55e;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 600;
        display: inline-block;
    }
    .recommendation-hold {
        background: #eab308;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 600;
        display: inline-block;
    }
    .recommendation-sell {
        background: #ef4444;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 600;
        display: inline-block;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(120deg, #1e88e5, #00acc1);
        color: white;
        border: none;
        padding: 0.75rem;
        font-weight: 600;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


def create_revenue_chart(data: list) -> go.Figure:
    """Create interactive revenue trend chart"""
    df = pd.DataFrame(data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['quarter'],
        y=df['value'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color='#1e88e5', width=3),
        marker=dict(size=10)
    ))
    fig.update_layout(
        title='Quarterly Revenue Trend',
        xaxis_title='Quarter',
        yaxis_title='Revenue ($M)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    return fig


def create_metrics_chart(metrics: dict) -> go.Figure:
    """Create metrics comparison bar chart"""
    fig = go.Figure(data=[
        go.Bar(
            x=list(metrics.keys()),
            y=list(metrics.values()),
            marker=dict(
                color=['#22c55e', '#3b82f6', '#eab308', '#8b5cf6'],
                line=dict(color='white', width=2)
            )
        )
    ])
    fig.update_layout(
        title='Key Financial Metrics',
        template='plotly_white',
        showlegend=False,
        height=400
    )
    return fig


def init_session_state():
    """Initialize session state variables with agent-aware state management"""
    if 'orchestrator' not in st.session_state:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            st.error(" Please set GROQ_API_KEY in your .env file")
            st.stop()

        client = groq.Groq(api_key=api_key)
        st.session_state.orchestrator = AgentOrchestrator(client)

    if 'history' not in st.session_state:
        st.session_state.history = []

    # Agent-aware state tracking
    if 'agent_state' not in st.session_state:
        st.session_state.agent_state = {
            "current_mode": None,
            "constraints_active": False,
            "recovery_mode": False,
            "last_constraint_message": None
        }


def main():
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header"> Financial AI Analysis Agent</h1>', unsafe_allow_html=True)
    st.markdown("*AI-powered investment research and analysis platform*")
    
    # Sidebar
    with st.sidebar:
        st.header(" Control Panel")
        
        mode = st.selectbox(
            "Analysis Mode",
            [" Company Analysis", " PDF Report Analysis", " Research Guide", " General Chat"],
            index=0
        )
        
        st.divider()
        
        pdf_file = st.file_uploader(
            " Upload Earnings PDF",
            type=['pdf'],
            help="Upload quarterly or annual report"
        )
        
        if pdf_file:
            st.success(f" {pdf_file.name} loaded")
        
        st.divider()
        
        st.subheader(" Session Stats")
        st.metric("Total Analyses", len(st.session_state.history))
        st.metric("Current Mode", mode.split()[1])

        # Agent-aware state display
        if hasattr(st.session_state.orchestrator, 'get_session_context'):
            session_ctx = st.session_state.orchestrator.get_session_context()
            with st.expander("🤖 Agent State", expanded=False):
                st.metric("Interaction Count", session_ctx.get("interaction_count", 0))
                if session_ctx.get("constraints"):
                    st.warning(f"Active Constraints: {len(session_ctx['constraints'])}")
                    for constraint in session_ctx["constraints"]:
                        st.caption(f"• {constraint}")

                # Show agent recovery attempts
                if hasattr(st.session_state.orchestrator.company_agent, 'analysis_state'):
                    recovery_attempts = st.session_state.orchestrator.company_agent.analysis_state.get("recovery_attempts", 0)
                    if recovery_attempts > 0:
                        st.info(f"Recovery Attempts: {recovery_attempts} (Agent learning from constraints)")

                # Show current agent mode
                current_mode = session_ctx.get("current_mode")
                if current_mode:
                    st.success(f"Current Mode: {current_mode}")

        if st.button(" Clear History"):
            st.session_state.history = []
            # Reset agent state
            if hasattr(st.session_state.orchestrator, 'reset_session'):
                st.session_state.orchestrator.reset_session()
            st.session_state.agent_state = {
                "current_mode": None,
                "constraints_active": False,
                "recovery_mode": False,
                "last_constraint_message": None
            }
            st.rerun()
    
    # Main Content
    col1, col2 = st.columns([7, 3])
    
    with col1:
        st.subheader(" Your Query")
        
        examples = {
            " Company Analysis": "Analyze Apple's current performance and provide a BUY/HOLD/SELL recommendation",
            " PDF Report Analysis": "Analyze this earnings report and break down the key metrics",
            " Research Guide": "What sources should I review to build conviction on Microsoft stock?",
            " General Chat": "How do I evaluate a company's earnings report?"
        }
        
        st.info(f" Example: *{examples[mode]}*")
        
        query = st.text_area(
            "Enter your question",
            height=120,
            placeholder="Type your analysis request here..."
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 6])
        with col_btn1:
            analyze_btn = st.button(" Analyze", type="primary")
    
    with col2:
        st.subheader(" Quick Actions")
        
        if st.button(" Market Overview"):
            st.info("Feature coming soon! This will show market indices and trends.")
        
        if st.button(" Latest News"):
            st.info("Feature coming soon! This will fetch latest financial news.")
        
        if st.button(" Watchlist"):
            st.info("Feature coming soon! Track your favorite stocks.")
    
    # Process analysis
    if analyze_btn and query:
        with st.spinner(" AI Agent analyzing..."):
            try:
                # Classify intent
                intent = st.session_state.orchestrator.classify_intent(query)
                
                # Show intent detection
                with st.expander("🔍 Intent Detection", expanded=False):
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Intent", intent.get('intent', 'unknown').replace('_', ' ').title())
                    col_b.metric("Confidence", f"{intent.get('confidence', 0):.0%}")
                    col_c.metric("Entities", len(intent.get('entities', [])))
                
                # Get PDF data
                pdf_data = pdf_file.read() if pdf_file else None
                
                # Process
                response = st.session_state.orchestrator.route_and_process(
                    query, 
                    intent, 
                    pdf_data
                )
                
                # Store in history
                st.session_state.history.append({
                    'timestamp': datetime.now(),
                    'query': query,
                    'mode': mode,
                    'intent': intent,
                    'response': response,
                    'recommendation': extract_recommendation(response)
                })
                
            except Exception as e:
                st.error(f" Error during analysis: {str(e)}")
    
    # Display Results
    if st.session_state.history:
        st.divider()
        st.header(" Analysis Results")
        
        latest = st.session_state.history[-1]
        
        # Header info
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("Analysis Type", latest['mode'].split()[1])
        with col_info2:
            recommendation = latest['recommendation']
            if recommendation != 'N/A':
                color = {'BUY': 'buy', 'HOLD': 'hold', 'SELL': 'sell'}[recommendation]
                st.markdown(f'<div class="recommendation-{color}">{recommendation}</div>', 
                           unsafe_allow_html=True)
        with col_info3:
            st.metric("Time", latest['timestamp'].strftime('%H:%M:%S'))
        
        st.markdown(f"**Query:** _{latest['query']}_")
        
        # Response with agent-aware display
        with st.container():
            # Show constraint warning if applicable
            if latest.get('constraints_active', False):
                st.warning(" **Analysis Constraints Active**: This analysis is based on limited information. Consider gathering more data for comprehensive insights.")

            st.markdown(latest['response'])

            # Show recovery suggestions if in constraint mode
            if st.session_state.agent_state.get("recovery_mode", False):
                with st.expander("💡 Recovery Suggestions", expanded=False):
                    st.markdown("""
                    **To improve analysis quality:**

                    1. **Gather Current Data**: Use web search for recent financial statements
                    2. **Check Multiple Sources**: Cross-reference information from Yahoo Finance, Seeking Alpha, Bloomberg
                    3. **Upload Documents**: Provide PDF reports or earnings presentations
                    4. **Specify Requirements**: Be more specific about what aspects you want analyzed

                    **Quick Actions:**
                    - Try web search for the company name + "financials"
                    - Look for recent earnings presentations
                    - Check analyst reports and ratings
                    """)
        
        # Visualizations
        json_data = extract_json_from_response(latest['response'])
        if json_data:
            st.subheader(" Data Visualizations")
            
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                if 'quarterly_revenue' in json_data:
                    fig = create_revenue_chart(json_data['quarterly_revenue'])
                    st.plotly_chart(fig, use_container_width=True)
                elif 'quarterly_trends' in json_data and 'revenue' in json_data['quarterly_trends']:
                    fig = create_revenue_chart(json_data['quarterly_trends']['revenue'])
                    st.plotly_chart(fig, use_container_width=True)
            
            with viz_col2:
                if 'key_metrics' in json_data:
                    metrics = json_data['key_metrics']
                    for key, value in metrics.items():
                        st.metric(
                            key.replace('_', ' ').title(),
                            f"${value:,.2f}M" if value > 100 else f"{value:.2f}"
                        )
                elif 'current_metrics' in json_data:
                    metrics = json_data['current_metrics']
                    for key, value in list(metrics.items())[:4]:
                        st.metric(
                            key.replace('_', ' ').title(),
                            f"${value:,.2f}M" if value > 100 else f"{value:.2f}"
                        )
        
        # History
        if len(st.session_state.history) > 1:
            with st.expander(f" Previous Analyses ({len(st.session_state.history)-1})"):
                for i, item in enumerate(reversed(st.session_state.history[:-1]), 1):
                    st.markdown(f"**{i}. {item['query']}**")
                    st.caption(f"{item['mode']} • {item['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                    st.markdown(item['response'][:300] + "...")
                    st.divider()


if __name__ == "__main__":
    main()