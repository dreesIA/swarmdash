"""Weekly training report functionality"""
import streamlit as st
import pandas as pd
import plotly.express as px
from core.data_loader import load_data
from core.constants import METRICS
from core.theme import ThemeConfig
from components.metrics import create_metric_card, calculate_load_score
from components.charts import create_heatmap, create_performance_bar_chart
from components.ai_assistant import display_ai_assistant

def render_weekly_training_report(api_key: str, team_config: dict):
    """Render weekly training report"""
    st.markdown(f"<h2 style='color: {ThemeConfig.PRIMARY_COLOR};'>📅 Weekly Training Report</h2>", 
                unsafe_allow_html=True)
    
    # Get training files from team_config
    TRAINING_FILES = team_config.get("training_files", {})
    
    if not TRAINING_FILES:
        st.warning("No training files configured for this team.")
        return
    
    # Session selection
    available_sessions = list(TRAINING_FILES.keys())
    selected_sessions = st.sidebar.multiselect(
        "Select Training Sessions",
        available_sessions,
        default=available_sessions,
        key="weekly_sessions_selector"
    )
    
    if not selected_sessions:
        st.info("Please select at least one training session.")
        return
    
    # Load data with proper ordering
    training_data = []
    session_order = {session: idx for idx, session in enumerate(available_sessions)}
    
    for session in selected_sessions:
        df_temp = load_data(TRAINING_FILES[session])
        if not df_temp.empty:
            df_temp["Session"] = session
            df_temp["Session_Order"] = session_order[session]
            training_data.append(df_temp)
    
    if not training_data:
        st.warning("No data available for selected sessions.")
        return
        
    weekly_df = pd.concat(training_data, ignore_index=True)
    
    # View mode selection
    view_mode = st.sidebar.radio(
        "View Mode",
        ["Team Overview", "Individual Analysis", "Session Comparison", "Load Management"],
        key="weekly_view"
    )
    
    if view_mode == "Team Overview":
        render_team_overview(weekly_df, api_key)
    elif view_mode == "Individual Analysis":
        render_individual_analysis(weekly_df, api_key)
    elif view_mode == "Session Comparison":
        render_session_comparison(weekly_df, api_key)
    elif view_mode == "Load Management":
        render_load_management(weekly_df, api_key)

def render_team_overview(weekly_df: pd.DataFrame, api_key: str):
    """Render team overview for weekly training"""
    st.markdown("### Team Training Overview")
    
    if weekly_df.empty:
        st.warning("No data available for team overview.")
        return
    
    # Calculate weekly totals and averages
    col1, col2, col3, col4 = st.columns(4)
    
    metrics_data = calculate_team_metrics(weekly_df)
    
    with col1:
        st.markdown(create_metric_card("Total Team Distance", f"{metrics_data['total_distance']:.0f} km"), 
                   unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Avg Intensity", f"{metrics_data['avg_intensity']:.1f} km/h"), 
                   unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Total Sprints", f"{metrics_data['total_sprints']:.0f}"), 
                   unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("Avg Load", f"{metrics_data['avg_load']:.0f}"), 
                   unsafe_allow_html=True)
    
    # AI Assistant
    team_summary = create_team_summary(weekly_df, metrics_data)
    display_ai_assistant("Weekly Team Training Analysis", team_summary, api_key)
    
    # Training load distribution
    display_load_distribution(weekly_df)
    
    # Player rankings
    display_player_rankings(weekly_df)

def render_individual_analysis(weekly_df: pd.DataFrame, api_key: str):
    """Render individual player analysis"""
    st.markdown("### Individual Player Analysis")
    
    if weekly_df.empty:
        st.warning("No data available for individual analysis.")
        return
    
    # Player selection
    available_players = sorted(weekly_df["Player Name"].unique())
    selected_player = st.sidebar.selectbox(
        "Select Player",
        available_players,
        key="individual_player_selector"
    )
    
    player_data = weekly_df[weekly_df["Player Name"] == selected_player]
    
    if player_data.empty:
        st.warning(f"No data available for {selected_player}.")
        return
    
    # Display player metrics
    display_player_metrics(player_data, selected_player)
    
    # Performance trends
    display_player_trends(player_data, weekly_df, selected_player, api_key)
    
    # Percentile rankings
    display_player_rankings_individual(player_data, weekly_df, selected_player)

def render_session_comparison(weekly_df: pd.DataFrame, api_key: str):
    """Render session comparison analysis"""
    st.markdown("### Session Comparison")
    
    if weekly_df.empty or "Session" not in weekly_df.columns:
        st.warning("No session data available for comparison.")
        return
    
    # Session metrics overview
    display_session_overview(weekly_df)
    
    # Metric comparison across sessions
    display_session_metric_comparison(weekly_df)
    
    # Player participation
    display_player_participation(weekly_df)
    
    # AI Assistant
    session_summary = create_session_comparison_summary(weekly_df)
    display_ai_assistant("Training Session Comparison", session_summary, api_key)

def render_load_management(weekly_df: pd.DataFrame, api_key: str):
    """Render load management analysis"""
    st.markdown("### Load Management & Recovery")
    
    if weekly_df.empty:
        st.warning("No data available for load management analysis.")
        return
    
    # Calculate load metrics
    weekly_df["Load Score"] = calculate_load_score(weekly_df)
    
    # Player load status
    display_load_status(weekly_df)
    
    # AI Assistant
    load_summary = create_load_management_summary(weekly_df)
    display_ai_assistant("Load Management Analysis", load_summary, api_key)
    
    # Detailed player load table
    display_detailed_load_analysis(weekly_df)
    
    # Load progression chart
    display_load_progression(weekly_df)

# Helper functions for weekly training

def calculate_team_metrics(df: pd.DataFrame) -> dict:
    """Calculate team-level metrics"""
    metrics = {
        "total_distance": df["Total Distance"].sum() if "Total Distance" in df.columns else 0,
        "avg_intensity": df["Max Speed"].mean() if "Max Speed" in df.columns else 0,
        "total_sprints": df["No of Sprints"].sum() if "No of Sprints" in df.columns else 0,
        "avg_load": 0
    }
    
    if "Accelerations" in df.columns and "Decelerations" in df.columns:
        metrics["avg_load"] = df["Accelerations"].mean() + df["Decelerations"].mean()
    
    return metrics

def create_team_summary(df: pd.DataFrame, metrics: dict) -> str:
    """Create team summary for AI assistant"""
    return f"""
    Weekly Training Overview:
    Sessions completed: {df['Session'].nunique() if 'Session' in df.columns else 0}
    Total players: {df['Player Name'].nunique()}
    
    Team Statistics:
    - Total Distance: {metrics['total_distance']:.0f} km
    - Average Intensity: {metrics['avg_intensity']:.1f} km/h
    - Total Sprints: {metrics['total_sprints']:.0f}
    - Average Load: {metrics['avg_load']:.0f}
    
    Consider: Is the training load appropriate for match schedule? Are all players getting adequate volume?
    """

def display_load_distribution(df: pd.DataFrame):
    """Display training load distribution heatmap"""
    st.markdown("#### Training Load Distribution")
    
    if "Session" in df.columns and "Total Distance" in df.columns:
        pivot_df = df.pivot_table(
            values="Total Distance",
            index="Player Name",
            columns="Session",
            aggfunc="mean"
        ).fillna(0)
        
        if not pivot_df.empty:
            fig = create_heatmap(pivot_df, "Player Load Heatmap")
            st.plotly_chart(fig, use_container_width=True)

def display_player_rankings(df: pd.DataFrame):
    """Display weekly player rankings"""
    st.markdown("#### Weekly Player Rankings")
    
    available_metrics = [m for m in METRICS if m in df.columns]
    ranking_metric = st.selectbox(
        "Select ranking metric:",
        available_metrics,
        key="weekly_ranking_metric"
    )
    
    if ranking_metric in df.columns:
        fig = create_performance_bar_chart(df, ranking_metric, f"Top 10 Players - {ranking_metric}")
        st.plotly_chart(fig, use_container_width=True)

# Additional helper functions would continue here...
