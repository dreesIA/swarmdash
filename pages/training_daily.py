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

def render_session_overview(df_daily: pd.DataFrame, api_key: str):
    """Render session overview"""
    st.markdown("### Session Overview")
    
    # Metric distribution
    available_metrics = [m for m in METRICS if m in df_daily.columns]
    selected_metric = st.selectbox(
        "Select metric to analyze:",
        available_metrics,
        key="session_metric"
    )
    
    if selected_metric in df_daily.columns:
        # Create distribution plot
        fig = create_distribution_plot(df_daily[selected_metric], selected_metric, 
                                     f"{selected_metric} Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Player rankings for the session
    display_session_rankings(df_daily)

def render_individual_performance(df_daily: pd.DataFrame, api_key: str):
    """Render individual performance for daily training"""
    st.markdown("### Individual Performance Analysis")
    
    available_players = sorted(df_daily["Player Name"].unique())
    selected_player = st.selectbox(
        "Select Player:",
        available_players,
        key="daily_individual_player"
    )
    
    player_data = df_daily[df_daily["Player Name"] == selected_player]
    
    if not player_data.empty:
        player_data = player_data.iloc[0]
        
        # Display player metrics
        display_individual_metrics(player_data, df_daily, selected_player)
        
        # Percentile rankings
        display_percentile_rankings(player_data, df_daily, selected_player, api_key)
        
        # Performance insights
        display_performance_insights(player_data, df_daily, selected_player)

def render_comparative_analysis(df_daily: pd.DataFrame, api_key: str):
    """Render comparative analysis for daily training"""
    st.markdown("### Comparative Analysis")
    
    # Player selection
    available_players = sorted(df_daily["Player Name"].unique())
    players = st.multiselect(
        "Select 2-4 players to compare:",
        available_players,
        default=available_players[:3] if len(available_players) >= 3 else available_players,
        max_selections=4,
        key="daily_comparative_players"
    )
    
    if len(players) < 2:
        st.info("Please select at least 2 players for comparison.")
        return
    
    comparison_df = df_daily[df_daily["Player Name"].isin(players)]
    
    # Metric comparison
    display_metric_comparison(comparison_df, players)
    
    # Radar comparison
    display_radar_comparison(comparison_df, df_daily, players)
    
    # AI Assistant for Comparison
    comparison_summary = create_comparison_summary(comparison_df, players)
    display_ai_assistant("Player Comparison Analysis", comparison_summary, api_key)
    
    # Comparison table
    display_comparison_table(comparison_df, df_daily, players)

# Helper functions for daily training

def calculate_session_metrics(df: pd.DataFrame) -> dict:
    """Calculate session-level metrics"""
    metrics = {
        "participants": df["Player Name"].nunique(),
        "avg_distance": df["Total Distance"].mean() if "Total Distance" in df.columns else 0,
        "max_speed": df["Max Speed"].max() if "Max Speed" in df.columns else 0,
        "total_sprints": df["No of Sprints"].sum() if "No of Sprints" in df.columns else 0
    }
    return metrics

def display_session_rankings(df: pd.DataFrame):
    """Display session player rankings"""
    st.markdown("### Session Rankings")
    
    ranking_data = df.copy()
    available_metrics = [m for m in METRICS if m in ranking_data.columns]
    
    if available_metrics:
        ranking_data["Overall Score"] = ranking_data[available_metrics].mean(axis=1)
        ranking_data = ranking_data.sort_values("Overall Score", ascending=False)
        
        # Top performers
        col1, col2, col3 = st.columns(3)
        
        top_3 = ranking_data.head(3)
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (col, (_, player)) in enumerate(zip([col1, col2, col3], top_3.iterrows())):
            with col:
                st.markdown(f"""
                <div style='text-align: center; background-color: {ThemeConfig.CARD_BACKGROUND}; 
                            padding: 20px; border-radius: 10px;'>
                    <h1>{medals[i]}</h1>
                    <h4>{player['Player Name']}</h4>
                    <p>Score: {player['Overall Score']:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Full ranking table
        with st.expander("View Complete Rankings"):
            display_cols = ["Player Name"] + available_metrics + ["Overall Score"]
            st.dataframe(
                ranking_data[display_cols].reset_index(drop=True),
                use_container_width=True
            )

def display_individual_metrics(player_data: pd.Series, df: pd.DataFrame, player_name: str):
    """Display individual player metrics"""
    st.markdown(f"#### {player_name} - Performance Metrics")
    
    # Create metric cards in grid
    cols = st.columns(4)
    available_metrics = [m for m in METRICS if m in player_data.index]
    
    for i, metric in enumerate(available_metrics):
        with cols[i % 4]:
            value = player_data[metric]
            avg_value = df[metric].mean()
            delta = ((value - avg_value) / avg_value * 100) if avg_value > 0 else 0
            
            st.markdown(create_metric_card(
                metric.replace("_", " ").title(),
                f"{value:.2f}",
                delta
            ), unsafe_allow_html=True)

def display_percentile_rankings(player_data: pd.Series, df: pd.DataFrame, 
                               player_name: str, api_key: str):
    """Display percentile rankings for individual player"""
    st.markdown("#### Percentile Rankings")
    
    available_metrics = [m for m in METRICS if m in player_data.index and m in df.columns]
    percentile_data = []
    
    for metric in available_metrics:
        all_values = df[metric]
        player_value = player_data[metric]
        percentile = (all_values < player_value).sum() / len(all_values) * 100
        percentile_data.append(percentile)
    
    if percentile_data:
        # Create radar chart
        fig = create_plotly_radar(
            [percentile_data],
            available_metrics,
            f"{player_name} - Session Performance Percentiles",
            [player_name]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # AI Assistant
    individual_summary = f"""
    Individual Performance Analysis: {player_name}
    
    Session Metrics:
    {chr(10).join([f"- {metric}: {player_data[metric]:.2f} ({percentile_data[i]:.0f}th percentile)" 
                   for i, metric in enumerate(available_metrics)])}
    
    Strengths: {', '.join([available_metrics[i] for i, p in enumerate(percentile_data) if p >= 75])}
    Areas to monitor: {', '.join([available_metrics[i] for i, p in enumerate(percentile_data) if p < 50])}
    """
    
    display_ai_assistant("Individual Session Performance", individual_summary, api_key)

def display_performance_insights(player_data: pd.Series, df: pd.DataFrame, player_name: str):
    """Display performance insights"""
    st.markdown("#### Performance Insights")
    
    available_metrics = [m for m in METRICS if m in player_data.index and m in df.columns]
    
    # Calculate percentiles
    metric_percentiles = {}
    for metric in available_metrics:
        all_values = df[metric]
        player_value = player_data[metric]
        percentile = (all_values < player_value).sum() / len(all_values) * 100
        metric_percentiles[metric] = percentile
    
    # Find strengths and areas for improvement
    strengths = sorted(metric_percentiles.items(), key=lambda x: x[1], reverse=True)[:3]
    improvements = sorted(metric_percentiles.items(), key=lambda x: x[1])[:3]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💪 Top Strengths:**")
        for metric, percentile in strengths:
            st.markdown(f"- {metric}: {percentile:.0f}th percentile")
    
    with col2:
        st.markdown("**📈 Areas for Development:**")
        for metric, percentile in improvements:
            st.markdown(f"- {metric}: {percentile:.0f}th percentile")

def display_metric_comparison(comparison_df: pd.DataFrame, players: list):
    """Display metric comparison between players"""
    st.markdown("#### Metric Comparison")
    
    available_metrics = [m for m in METRICS if m in comparison_df.columns]
    metrics_for_comparison = st.multiselect(
        "Select metrics to compare:",
        available_metrics,
        default=available_metrics[:4] if len(available_metrics) >= 4 else available_metrics,
        key="daily_comparison_metrics"
    )
    
    if metrics_for_comparison:
        # Reshape data for plotting
        plot_data = comparison_df[["Player Name"] + metrics_for_comparison].melt(
            id_vars="Player Name",
            var_name="Metric",
            value_name="Value"
        )
        
        fig = px.bar(
            plot_data,
            x="Metric",
            y="Value",
            color="Player Name",
            barmode="group",
            title="Player Metric Comparison",
            height=500,
            color_discrete_sequence=[ThemeConfig.PRIMARY_COLOR, ThemeConfig.SECONDARY_COLOR, 
                                   ThemeConfig.ACCENT_COLOR, ThemeConfig.SUCCESS_COLOR]
        )
        
        fig.update_layout(
            plot_bgcolor=ThemeConfig.CARD_BACKGROUND,
            paper_bgcolor=ThemeConfig.BACKGROUND_COLOR,
            font=dict(color=ThemeConfig.TEXT_COLOR),
            xaxis=dict(tickangle=-45)
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_radar_comparison(comparison_df: pd.DataFrame, full_df: pd.DataFrame, players: list):
    """Display radar comparison between players"""
    st.markdown("#### Multi-Player Radar Analysis")
    
    available_metrics = [m for m in METRICS if m in comparison_df.columns and m in full_df.columns]
    
    # Calculate percentiles
    percentile_data = []
    for player in players:
        player_row = comparison_df[comparison_df["Player Name"] == player]
        if not player_row.empty:
            player_data = player_row.iloc[0]
            player_percentiles = []
            for metric in available_metrics:
                all_values = full_df[metric]
                player_value = player_data[metric]
                percentile = (all_values < player_value).sum() / len(all_values) * 100
                player_percentiles.append(percentile)
            percentile_data.append(player_percentiles)
    
    if percentile_data:
        fig = create_plotly_radar(
            percentile_data,
            available_metrics,
            "Player Comparison - Percentile Rankings",
            players
        )
        
        st.plotly_chart(fig, use_container_width=True)

def create_comparison_summary(df: pd.DataFrame, players: list) -> str:
    """Create comparison summary for AI assistant"""
    available_metrics = [m for m in METRICS if m in df.columns]
    
    summary = f"""
    Player Comparison Analysis:
    Players: {', '.join(players)}
    
    Key Observations:
    """
    
    for metric in available_metrics[:3]:
        if metric in df.columns:
            metric_values = []
            for player in players:
                player_data = df[df['Player Name'] == player]
                if not player_data.empty:
                    value = player_data[metric].iloc[0]
                    metric_values.append(f"{player} ({value:.1f})")
            
            if metric_values:
                summary += f"\n- {metric}: {', '.join(metric_values)}"
    
    summary += "\n\nConsider: Position-specific requirements, tactical roles, individual development plans"
    
    return summary

def display_comparison_table(comparison_df: pd.DataFrame, full_df: pd.DataFrame, players: list):
    """Display detailed comparison table"""
    st.markdown("#### Detailed Comparison")
    
    available_metrics = [m for m in METRICS if m in comparison_df.columns]
    comparison_display = comparison_df[["Player Name"] + available_metrics].set_index("Player Name")
    
    # Add averages
    if available_metrics:
        comparison_display.loc["Team Average"] = full_df[available_metrics].mean()
    
    st.dataframe(
        comparison_display.style.background_gradient(cmap='RdYlGn', axis=0),
        use_container_width=True
    )
