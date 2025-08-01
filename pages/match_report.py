"""Match report page functionality"""
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from core.data_loader import load_data, load_event_data
from core.constants import METRICS
from core.theme import ThemeConfig
from components.metrics import create_metric_card, create_performance_summary
from components.charts import create_plotly_radar, create_performance_bar_chart, create_trend_line_chart
from components.ai_assistant import display_ai_assistant
from utils.calculations import calculate_percentile_values

def render_match_report(api_key: str, team_config: dict):
    """Render the match report section"""
    # Get team-specific files
    MATCH_FILES = team_config.get("match_files", {})
    EVENT_FILES = team_config.get("event_files", {})
    EVENT_IMAGES = team_config.get("event_images", {})
    
    if not MATCH_FILES:
        st.warning("No match files configured for this team.")
        return
        
    # Match selection
    match_options = ["All Matches (Average)"] + list(MATCH_FILES.keys())
    selected_match = st.sidebar.selectbox("Select Match", match_options)
    
    # Load data
    if selected_match == "All Matches (Average)":
        df = pd.concat([load_data(path) for path in MATCH_FILES.values()], ignore_index=True)
    else:
        df = load_data(MATCH_FILES[selected_match])
    
    if df.empty:
        st.error("No data available for the selected match.")
        return
    
    # Half selection
    half_option = st.sidebar.selectbox("Select Half", ["Total", "First Half", "Second Half"])
    
    # Player selection
    players = df["Player Name"].unique().tolist()
    selected_player = st.sidebar.selectbox("Select Player", ["All"] + players)
    
    # Filter data
    match_df = df.copy()
    if selected_player != "All":
        match_df = match_df[match_df["Player Name"] == selected_player]
    if half_option != "Total":
        match_df = match_df[match_df["Session Type"] == half_option]
    
    # Display match title
    st.markdown(f"<h2 style='color: {ThemeConfig.PRIMARY_COLOR};'>🏆 {selected_match}</h2>", unsafe_allow_html=True)
    
    # Key Metrics Dashboard
    st.markdown("### Key Performance Indicators")
    
    # Calculate and display metrics
    display_match_metrics(match_df, api_key)
    
    # Tabbed content
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚡ Event Analysis", "📊 Performance Charts", 
                                           "📈 Trends", "🎯 Radar Analysis", "📋 Data Table"])
    
    with tab1:
        render_event_analysis(selected_match, api_key, EVENT_FILES, EVENT_IMAGES, match_df)
    
    with tab2:
        render_performance_charts(match_df, api_key)
    
    with tab3:
        render_trend_analysis(selected_match, match_df, api_key, MATCH_FILES)
    
    with tab4:
        render_radar_analysis(match_df, df, half_option, selected_player, api_key)
    
    with tab5:
        render_data_table(match_df)

def display_match_metrics(match_df: pd.DataFrame, api_key: str):
    """Display key match metrics"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calculate metrics
    metrics_data = {
        "Distance": match_df["Total Distance"].mean() if "Total Distance" in match_df.columns else 0,
        "Max Speed": match_df["Max Speed"].mean() if "Max Speed" in match_df.columns else 0,
        "Sprints": match_df["No of Sprints"].mean() if "No of Sprints" in match_df.columns else 0,
        "HSR": match_df["High Speed Running"].mean() if "High Speed Running" in match_df.columns else 0,
        "Work Rate": (match_df["Accelerations"].mean() + match_df["Decelerations"].mean()) 
                     if all(col in match_df.columns for col in ["Accelerations", "Decelerations"]) else 0
    }
    
    # Display metrics
    with col1:
        st.markdown(create_metric_card("Distance", f"{metrics_data['Distance']:.2f} km"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Max Speed", f"{metrics_data['Max Speed']:.1f} km/h"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Sprints", f"{metrics_data['Sprints']:.0f}"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("HSR", f"{metrics_data['HSR']:.0f} m"), unsafe_allow_html=True)
    with col5:
        st.markdown(create_metric_card("Work Rate", f"{metrics_data['Work Rate']:.0f}"), unsafe_allow_html=True)
    
    # AI Assistant
    match_summary = f"""
    Team Averages:
    - Distance: {metrics_data['Distance']:.2f} km
    - Max Speed: {metrics_data['Max Speed']:.1f} km/h
    - Sprints: {metrics_data['Sprints']:.0f}
    - High Speed Running: {metrics_data['HSR']:.0f} m
    - Work Rate: {metrics_data['Work Rate']:.0f} actions/game
    """
    
    display_ai_assistant("Match Overview Analysis", match_summary, api_key)

def render_event_analysis(selected_match: str, api_key: str, EVENT_FILES: dict, 
                         EVENT_IMAGES: dict, match_df: pd.DataFrame):
    """Render event analysis section"""
    st.markdown("### Match Event Analysis")
    
    if selected_match == "All Matches (Average)":
        # Load all event data
        all_events = []
        for match, file_path in EVENT_FILES.items():
            try:
                df_temp = load_event_data(file_path)
                if not df_temp.empty:
                    df_temp["Match"] = match
                    all_events.append(df_temp)
            except Exception as e:
                st.warning(f"Could not load event data for {match}: {e}")
        
        if not all_events:
            st.error("No event data available across matches.")
            return
        
        df_events = pd.concat(all_events, ignore_index=True)
    else:
        # Load single match event data
        xls_path = EVENT_FILES.get(selected_match)
        if not xls_path:
            st.warning("Event data not available for this match.")
            return
        
        df_events = load_event_data(xls_path)
        if df_events.empty:
            st.warning("No event data available.")
            return
    
    # Display event summary
    display_event_summary(df_events, selected_match)
    
    # Shot map
    render_shot_map(df_events, selected_match)

def render_performance_charts(match_df: pd.DataFrame, api_key: str):
    """Render performance charts"""
    st.markdown("### Performance Metrics by Player")
    
    if match_df.empty:
        st.warning("No data available for performance charts.")
        return
    
    # Metric selection
    available_metrics = [m for m in METRICS if m in match_df.columns]
    selected_metrics = st.multiselect(
        "Select metrics to display:",
        available_metrics,
        default=available_metrics[:4] if len(available_metrics) >= 4 else available_metrics
    )
    
    if not selected_metrics:
        st.warning("Please select at least one metric to display.")
        return
    
    # Create charts for each metric
    for metric in selected_metrics:
        if metric in match_df.columns:
            fig = create_performance_bar_chart(match_df, metric, f"{metric} by Player")
            st.plotly_chart(fig, use_container_width=True)
            
            # Top performers
            top_performers = match_df.groupby("Player Name")[metric].mean().nlargest(3)
            with st.expander(f"🏆 Top 3 Performers - {metric}"):
                for idx, (player, value) in enumerate(top_performers.items(), 1):
                    medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉"
                    st.markdown(f"{medal} **{player}**: {value:.2f}")

def render_trend_analysis(selected_match: str, match_df: pd.DataFrame, 
                         api_key: str, MATCH_FILES: dict):
    """Render trend analysis"""
    if selected_match == "All Matches (Average)":
        st.markdown("### Team Performance Trends")
        
        # Load all match data with proper ordering
        all_matches_data = []
        match_order = list(MATCH_FILES.keys())
        
        for idx, (match_name, file_path) in enumerate(MATCH_FILES.items()):
            df_temp = load_data(file_path)
            if not df_temp.empty:
                df_temp["Match"] = match_name
                df_temp["Match_Order"] = idx
                all_matches_data.append(df_temp)
        
        if not all_matches_data:
            st.warning("No match data available for trend analysis.")
            return
            
        full_df = pd.concat(all_matches_data, ignore_index=True)
        
        # Team trends
        render_team_trends(full_df, api_key)
        
        # Player trends
        render_player_trends_comparison(full_df, api_key)
    else:
        st.info("Trend analysis is only available when 'All Matches (Average)' is selected.")

def render_radar_analysis(match_df: pd.DataFrame, full_df: pd.DataFrame, 
                         half_option: str, selected_player: str, api_key: str):
    """Render radar analysis"""
    st.markdown("### Player Radar Analysis")
    
    if match_df.empty:
        st.warning("No data available for radar analysis.")
        return
    
    available_metrics = [m for m in METRICS if m in match_df.columns and m in full_df.columns]
    
    if selected_player == "All":
        # Multi-player comparison
        render_multi_player_radar(match_df, full_df, available_metrics, half_option)
    else:
        # Single player analysis
        render_single_player_radar(match_df, full_df, selected_player, 
                                  available_metrics, half_option, api_key)

def render_data_table(match_df: pd.DataFrame):
    """Render data table with export options"""
    st.markdown("### Raw Data View")
    
    if match_df.empty:
        st.warning("No data available to display.")
        return
    
    # Data filtering options
    col1, col2 = st.columns(2)
    
    with col1:
        available_columns = match_df.columns.tolist()
        default_columns = ["Player Name", "Session Type"] + [col for col in METRICS if col in available_columns]
        
        show_cols = st.multiselect(
            "Select columns to display:",
            available_columns,
            default=default_columns
        )
    
    with col2:
        if show_cols:
            sort_by = st.selectbox("Sort by:", show_cols, index=0)
        else:
            sort_by = None
    
    if show_cols:
        display_df = match_df[show_cols]
        
        if sort_by and sort_by in display_df.columns:
            display_df = display_df.sort_values(by=sort_by)
        
        # Display statistics
        st.markdown("#### Summary Statistics")
        numeric_cols = [col for col in show_cols if col in METRICS]
        if numeric_cols:
            stats_df = display_df[numeric_cols].describe().round(2)
            st.dataframe(stats_df, use_container_width=True)
        
        # Display full data
        st.markdown("#### Full Dataset")
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Export option
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"match_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Helper functions for match report

def display_event_summary(df_events: pd.DataFrame, selected_match: str):
    """Display event summary statistics"""
    # Implementation of event summary display
    pass

def render_shot_map(df_events: pd.DataFrame, selected_match: str):
    """Render shot map visualization"""
    # Implementation of shot map
    pass

def render_team_trends(full_df: pd.DataFrame, api_key: str):
    """Render team-level trend analysis"""
    # Implementation of team trends
    pass

def render_player_trends_comparison(full_df: pd.DataFrame, api_key: str):
    """Render player trend comparisons"""
    # Implementation of player trends
    pass

def render_multi_player_radar(match_df: pd.DataFrame, full_df: pd.DataFrame, 
                             metrics: list, half_option: str):
    """Render multi-player radar comparison"""
    # Implementation of multi-player radar
    pass

def render_single_player_radar(match_df: pd.DataFrame, full_df: pd.DataFrame, 
                              player: str, metrics: list, half_option: str, api_key: str):
    """Render single player radar analysis"""
    # Implementation of single player radar
    pass
