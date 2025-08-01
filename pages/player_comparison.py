"""Player comparison functionality"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from core.data_loader import load_data, load_multiple_files
from core.constants import METRICS, PERFORMANCE_WEIGHTS
from core.theme import ThemeConfig
from components.metrics import create_metric_card, calculate_performance_score
from components.charts import create_plotly_radar, create_trend_line_chart, create_heatmap
from components.ai_assistant import display_ai_assistant

def render_player_comparison(api_key: str, team_config: dict):
    """Render player comparison across matches"""
    st.markdown(f"<h2 style='color: {ThemeConfig.PRIMARY_COLOR};'>👥 Player Comparison Tool</h2>", 
                unsafe_allow_html=True)
    
    # Get files from team_config
    MATCH_FILES = team_config.get("match_files", {})
    TRAINING_FILES = team_config.get("training_files", {})
    
    # Data source selection
    data_source = st.sidebar.radio(
        "Select Data Source:",
        ["Match Data", "Training Data", "Combined"],
        key="comparison_data_source"
    )
    
    # Load appropriate data
    df = load_comparison_data(data_source, MATCH_FILES, TRAINING_FILES)
    
    if df.empty:
        st.warning(f"No data available for {data_source}.")
        return
    
    # Player selection
    available_players = sorted(df["Player Name"].unique())
    selected_players = st.multiselect(
        "Select players to compare (2-4):",
        available_players,
        default=available_players[:3] if len(available_players) >= 3 else available_players[:2],
        max_selections=4,
        key="comparison_players_selection"
    )
    
    if len(selected_players) < 2:
        st.info("Please select at least 2 players for comparison.")
        return
    
    # Filter data
    comparison_df = df[df["Player Name"].isin(selected_players)]
    
    # Comparison type
    comparison_type = st.radio(
        "Select Comparison Type:",
        ["Overall Performance", "Head-to-Head", "Trend Analysis", "Statistical Analysis"],
        horizontal=True
    )
    
    if comparison_type == "Overall Performance":
        render_overall_performance_comparison(comparison_df, selected_players, df, api_key)
    elif comparison_type == "Head-to-Head":
        render_head_to_head_comparison(comparison_df, selected_players, api_key)
    elif comparison_type == "Trend Analysis":
        render_trend_comparison(comparison_df, selected_players, api_key, MATCH_FILES)
    elif comparison_type == "Statistical Analysis":
        render_statistical_comparison(comparison_df, selected_players, api_key)

def load_comparison_data(data_source: str, match_files: dict, training_files: dict) -> pd.DataFrame:
    """Load data based on selected source"""
    if data_source == "Match Data":
        return load_multiple_files(match_files)
    elif data_source == "Training Data":
        return load_multiple_files(training_files)
    else:  # Combined
        match_df = load_multiple_files(match_files)
        training_df = load_multiple_files(training_files)
        return pd.concat([match_df, training_df], ignore_index=True)

def render_overall_performance_comparison(df: pd.DataFrame, players: list, 
                                        full_df: pd.DataFrame, api_key: str):
    """Render overall performance comparison"""
    st.markdown("### Overall Performance Comparison")
    
    if df.empty:
        st.warning("No data available for comparison.")
        return
    
    # Calculate averages
    available_metrics = [m for m in METRICS if m in df.columns]
    player_averages = df.groupby("Player Name")[available_metrics].mean()
    
    # Performance scores
    display_performance_scores(player_averages, players, available_metrics)
    
    # AI Assistant
    overall_summary = create_overall_comparison_summary(player_averages, players)
    display_ai_assistant("Overall Performance Comparison", overall_summary, api_key)
    
    # Detailed metrics comparison
    display_detailed_metrics_comparison(df, player_averages, players, available_metrics, full_df)
    
    # Strengths and weaknesses matrix
    display_strengths_weaknesses_matrix(player_averages, players, available_metrics)

def render_head_to_head_comparison(df: pd.DataFrame, players: list, api_key: str):
    """Render head-to-head comparison"""
    st.markdown("### 👥 Head-to-Head Comparison")
    
    if len(players) != 2:
        st.info("Please select exactly 2 players for head-to-head comparison.")
        players = select_two_players(df)
        if not players:
            return
    else:
        players = players[:2]
    
    player1, player2 = players
    
    # Get player data
    p1_data = df[df["Player Name"] == player1]
    p2_data = df[df["Player Name"] == player2]
    
    if p1_data.empty or p2_data.empty:
        st.warning("Insufficient data for head-to-head comparison.")
        return
    
    # Head-to-head metrics
    display_head_to_head_metrics(p1_data, p2_data, player1, player2)
    
    # Win/Loss summary
    display_win_loss_summary(p1_data, p2_data, player1, player2)
    
    # AI Assistant
    h2h_summary = create_head_to_head_summary(p1_data, p2_data, player1, player2)
    display_ai_assistant("Head-to-Head Comparison", h2h_summary, api_key)

def render_trend_comparison(df: pd.DataFrame, players: list, api_key: str, match_files: dict):
    """Render trend comparison analysis"""
    st.markdown("### Trend Comparison Analysis")
    
    # Add time information
    df = add_time_information(df, match_files)
    
    if "Time_Order" not in df.columns:
        st.warning("No time-based information available for trend analysis.")
        return
    
    # Metric selection
    available_metrics = [m for m in METRICS if m in df.columns]
    trend_metric = st.selectbox(
        "Select metric for trend analysis:",
        available_metrics,
        key="trend_comparison_metric"
    )
    
    if trend_metric:
        # Display trend chart
        display_trend_chart(df, players, trend_metric)
        
        # Growth analysis
        display_growth_analysis(df, players, trend_metric)
        
        # AI Assistant
        trend_summary = create_trend_comparison_summary(df, players, trend_metric)
        display_ai_assistant("Trend Comparison Analysis", trend_summary, api_key)

def render_statistical_comparison(df: pd.DataFrame, players: list, api_key: str):
    """Render statistical comparison"""
    st.markdown("### Statistical Analysis")
    
    if df.empty:
        st.warning("No data available for statistical analysis.")
        return
    
    # Distribution analysis
    display_distribution_analysis(df, players)
    
    # Statistical summary
    display_statistical_summary(df, players)
    
    # Consistency analysis
    display_consistency_analysis(df, players)

# Helper functions for player comparison

def display_performance_scores(player_averages: pd.DataFrame, players: list, metrics: list):
    """Display performance score cards"""
    st.markdown("#### Performance Scores")
    
    performance_scores = []
    for player in players:
        if player in player_averages.index:
            score = sum(player_averages.loc[player, metric] * PERFORMANCE_WEIGHTS.get(metric, 0.1) 
                       for metric in metrics if metric in PERFORMANCE_WEIGHTS)
            performance_scores.append({"Player": player, "Score": score})
    
    if performance_scores:
        scores_df = pd.DataFrame(performance_scores).sort_values("Score", ascending=False)
        
        # Display performance cards
        cols = st.columns(len(players))
        for i, (_, row) in enumerate(scores_df.iterrows()):
            with cols[i]:
                rank = i + 1
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
                
                st.markdown(f"""
                <div style='text-align: center; background-color: {ThemeConfig.CARD_BACKGROUND}; 
                            padding: 20px; border-radius: 10px; border: 2px solid {ThemeConfig.PRIMARY_COLOR};'>
                    <h1>{medal}</h1>
                    <h3>{row['Player']}</h3>
                    <h2 style='color: {ThemeConfig.PRIMARY_COLOR};'>{row['Score']:.1f}</h2>
                    <p>Performance Score</p>
                </div>
                """, unsafe_allow_html=True)

def create_overall_comparison_summary(player_averages: pd.DataFrame, players: list) -> str:
    """Create overall comparison summary for AI assistant"""
    summary = f"""
    Overall Performance Comparison:
    Players: {', '.join(players)}
    
    Performance Rankings:
    """
    
    # Add rankings
    for i, player in enumerate(players):
        if player in player_averages.index:
            summary += f"\n{i+1}. {player}"
    
    summary += "\n\nKey Insights: Consider position-specific requirements, playing time, and role in team tactics"
    
    return summary

def display_detailed_metrics_comparison(df: pd.DataFrame, player_averages: pd.DataFrame, 
                                       players: list, metrics: list, full_df: pd.DataFrame):
    """Display detailed metrics comparison"""
    st.markdown("#### Detailed Metrics")
    
    # Create spider plot
    percentile_data = []
    for player in players:
        if player in player_averages.index:
            player_percentiles = []
            for metric in metrics:
                all_values = full_df[metric].dropna()
                player_value = player_averages.loc[player, metric]
                percentile = (all_values < player_value).sum() / len(all_values) * 100
                player_percentiles.append(percentile)
            percentile_data.append(player_percentiles)
    
    if percentile_data:
        fig = create_plotly_radar(
            percentile_data,
            metrics,
            "Player Performance Comparison - Percentiles",
            players
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_strengths_weaknesses_matrix(player_averages: pd.DataFrame, players: list, metrics: list):
    """Display strengths and weaknesses matrix"""
    st.markdown("#### Strengths & Weaknesses Matrix")
    
    if not player_averages.empty:
        # Create heatmap
        normalized_data = (player_averages.loc[players] - player_averages.min()) / (player_averages.max() - player_averages.min())
        
        fig = px.imshow(
            normalized_data.T,
            labels=dict(x="Player", y="Metric", color="Normalized Score"),
            color_continuous_scale="RdYlGn",
            aspect="auto",
            title="Performance Heatmap (Normalized)",
            height=400
        )
        
        fig.update_layout(
            plot_bgcolor=ThemeConfig.CARD_BACKGROUND,
            paper_bgcolor=ThemeConfig.BACKGROUND_COLOR,
            font=dict(color=ThemeConfig.TEXT_COLOR)
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Additional helper functions would continue here...
