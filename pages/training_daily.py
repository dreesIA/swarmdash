"""Daily training report functionality"""
import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from core.data_loader import load_data
from core.constants import METRICS
from core.theme import ThemeConfig
from components.metrics import create_metric_card
from components.charts import create_distribution_plot, create_plotly_radar
from components.ai_assistant import display_ai_assistant

def render_daily_training_report(api_key: str, team_config: dict):
    """Render daily training report"""
    st.markdown(f"<h2 style='color: {ThemeConfig.PRIMARY_COLOR};'>📊 Daily Training Report</h2>", 
                unsafe_allow_html=True)
    
    # Get training files from team_config
    TRAINING_FILES = team_config.get("training_files", {})
    
    if not TRAINING_FILES:
        st.warning("No training files configured for this team.")
        return
    
    # Session selection
    selected_session = st.sidebar.selectbox(
        "Select Training Session",
        list(TRAINING_FILES.keys()),
        key="daily_session_selector"
    )
    
    # Load data
    df_daily = load_data(TRAINING_FILES[selected_session])
    
    if df_daily.empty:
        st.error("No data available for this session.")
        return
    
    st.markdown(f"### {selected_session}")
    
    # Display session overview metrics
    display_session_metrics(df_daily, selected_session, api_key)
    
    # View mode
    view_mode = st.radio(
        "Select View",
        ["Session Overview", "Individual Performance", "Comparative Analysis"],
        horizontal=True
    )
    
    if view_mode == "Session Overview":
        render_session_overview(df_daily, api_key)
    elif view_mode == "Individual Performance":
        render_individual_performance(df_daily, api_key)
    elif view_mode == "Comparative Analysis":
        render_comparative_analysis(df_daily, api_key)

def display_session_metrics(df: pd.DataFrame, session_name: str, api_key: str):
    """Display session overview metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = calculate_session_metrics(df)
    
    with col1:
        st.markdown(create_metric_card("Participants", f"{metrics['participants']}"), 
                   unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card("Avg Distance", f"{metrics['avg_distance']:.2f} km"), 
                   unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("Session Peak Speed", f"{metrics['max_speed']:.1f} km/h"), 
                   unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card("Total Sprints", f"{metrics['total_sprints']}"), 
                   unsafe_allow_html=True)
    
    # AI Assistant
    daily_summary = f"""
    Daily Training Session: {session_name}
    
    Session Statistics:
    - Participants: {metrics['participants']}
    - Average Distance: {metrics['avg_distance']:.2f} km
    - Peak Speed: {metrics['max_speed']:.1f} km/h
    - Total Sprints: {metrics['total_sprints']}
    
    Consider: Was the session intensity appropriate? Any players showing fatigue? Recovery needs?
    """
    
    display_ai_assistant("Daily Training Overview", daily_summary, api_key)
