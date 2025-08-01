"""Player profile functionality"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from core.data_loader import load_data
from core.constants import METRICS, PERFORMANCE_WEIGHTS
from core.theme import ThemeConfig
from components.metrics import create_metric_card, calculate_performance_score
from components.charts import create_plotly_radar, create_trend_line_chart
from components.ai_assistant import display_ai_assistant, get_ai_coach_insights

def render_player_profile(api_key: str, team_config: dict):
    """Render comprehensive player profile"""
    MATCH_FILES = team_config["match_files"]
    TRAINING_FILES = team_config["training_files"]
    
    st.markdown(f"<h2 style='color: {ThemeConfig.PRIMARY_COLOR};'>📊 Player Profile</h2>", 
                unsafe_allow_html=True)
    
    # Load all available data
    all_data = load_all_player_data(MATCH_FILES, TRAINING_FILES)
    
    if all_data.empty:
        st.warning("No data available for player profiles.")
        return
    
    # Player selection
    available_players = sorted(all_data["Player Name"].unique())
    selected_player = st.sidebar.selectbox(
        "Select Player:",
        available_players,
        key="profile_player_selector"
    )
    
    # Filter player data
    player_data = all_data[all_data["Player Name"] == selected_player]
    
    if player_data.empty:
        st.warning(f"No data available for {selected_player}.")
        return
    
    # Display player header
    st.markdown(f"### {selected_player} - Complete Performance Profile")
    
    # Overview metrics
    display_player_overview_metrics(player_data, api_key)
    
    # Profile tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 Performance Trends", 
                                           "💪 Strengths Analysis", "📅 Session History", "📄 Report"])
    
    with tab1:
        render_player_overview(player_data, all_data, api_key)
    
    with tab2:
        render_player_trends(player_data, api_key)
    
    with tab3:
        render_player_strengths(player_data, all_data, api_key)
    
    with tab4:
        render_session_history(player_data)
    
    with tab5:
        render_player_report(player_data, all_data, selected_player, api_key)

def load_all_player_data(match_files: dict, training_files: dict) -> pd.DataFrame:
    """Load all available player data"""
    all_match_data = pd.concat([load_data(path) for path in match_files.values()], ignore_index=True)
    all_training_data = pd.concat([load_data(path) for path in training_files.values()], ignore_index=True)
    
    # Add data source column
    all_match_data["Data Source"] = "Match"
    all_training_data["Data Source"] = "Training"
    
    # Combine all data
    return pd.concat([all_match_data, all_training_data], ignore_index=True)

def display_player_overview_metrics(player_data: pd.DataFrame, api_key: str):
    """Display player overview metrics"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_sessions = player_data.shape[0]
    available_metrics = [m for m in METRICS if m in player_data.columns]
    
    with col1:
        st.markdown(create_metric_card("Sessions", f"{total_sessions}"), unsafe_allow_html=True)
    
    if "Total Distance" in available_metrics:
        with col2:
            avg_distance = player_data["Total Distance"].mean()
            st.markdown(create_metric_card("Avg Distance", f"{avg_distance:.2f} km"), unsafe_allow_html=True)
    
    if "Max Speed" in available_metrics:
        with col3:
            max_speed_recorded = player_data["Max Speed"].max()
            st.markdown(create_metric_card("Top Speed", f"{max_speed_recorded:.1f} km/h"), unsafe_allow_html=True)
    
    if "No of Sprints" in available_metrics:
        with col4:
            total_sprints = player_data["No of Sprints"].sum()
            st.markdown(create_metric_card("Total Sprints", f"{total_sprints}"), unsafe_allow_html=True)
    
    if "Accelerations" in available_metrics and "Decelerations" in available_metrics:
        with col5:
            avg_load = (player_data["Accelerations"].mean() + player_data["Decelerations"].mean())
            st.markdown(create_metric_card("Avg Load", f"{avg_load:.0f}"), unsafe_allow_html=True)
    
    # AI Assistant for Profile Overview
    profile_summary = create_profile_summary(player_data, total_sessions)
    display_ai_assistant("Player Profile Overview", profile_summary, api_key)

def render_player_overview(player_data: pd.DataFrame, all_data: pd.DataFrame, api_key: str):
    """Render player overview section"""
    st.markdown("### Performance Overview")
    
    # Split by data source
    match_data = player_data[player_data["Data Source"] == "Match"]
    training_data = player_data[player_data["Data Source"] == "Training"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_data_source_metrics(match_data, "Match Performance", ThemeConfig.PRIMARY_COLOR)
    
    with col2:
        display_data_source_metrics(training_data, "Training Performance", ThemeConfig.SECONDARY_COLOR)
    
    # Performance rating
    display_performance_rating(player_data, all_data)

def render_player_trends(player_data: pd.DataFrame, api_key: str):
    """Render player performance trends"""
    st.markdown("### Performance Trends")
    
    # Add session numbers for trending
    player_data = player_data.sort_index()
    player_data["Session_Number"] = range(1, len(player_data) + 1)
    
    # Metric selection
    available_metrics = [m for m in METRICS if m in player_data.columns]
    trend_metrics = st.multiselect(
        "Select metrics to analyze:",
        available_metrics,
        default=available_metrics[:3] if len(available_metrics) >= 3 else available_metrics
    )
    
    if not trend_metrics:
        st.info("Please select at least one metric to display trends.")
        return
    
    # Create trend charts
    for metric in trend_metrics:
        display_metric_trend(player_data, metric)
    
    # AI Assistant for Trend Analysis
    trends_summary = create_trends_summary(player_data, trend_metrics)
    display_ai_assistant("Player Trend Analysis", trends_summary, api_key)

def render_player_strengths(player_data: pd.DataFrame, all_data: pd.DataFrame, api_key: str):
    """Render player strengths analysis"""
    st.markdown("### Strengths & Development Areas")
    
    # Calculate percentiles
    percentiles = calculate_player_percentiles(player_data, all_data)
    
    # Create radar chart
    display_percentile_radar(percentiles, player_data["Player Name"].iloc[0])
    
    # Identify strengths and weaknesses
    display_strengths_weaknesses(percentiles)
    
    # AI Assistant for Strengths Analysis
    strengths_summary = create_strengths_summary(percentiles)
    display_ai_assistant("Strengths & Development Analysis", strengths_summary, api_key)
    
    # Performance consistency
    display_performance_consistency(player_data)

def render_session_history(player_data: pd.DataFrame):
    """Render detailed session history"""
    st.markdown("### Session History")
    
    # Session filters
    col1, col2 = st.columns(2)
    
    with col1:
        data_type_filter = st.selectbox(
            "Filter by type:",
            ["All", "Match", "Training"],
            key="session_history_filter"
        )
    
    with col2:
        available_metrics = [m for m in METRICS if m in player_data.columns]
        metric_to_highlight = st.selectbox(
            "Highlight metric:",
            ["None"] + available_metrics,
            key="session_history_highlight"
        )
    
    # Filter and display data
    display_session_table(player_data, data_type_filter, metric_to_highlight)
    
    # Session statistics
    display_session_statistics(player_data)

def render_player_report(player_data: pd.DataFrame, all_data: pd.DataFrame, 
                        player_name: str, api_key: str):
    """Generate comprehensive player report"""
    st.markdown("### Player Report")
    
    st.info("Generate a comprehensive PDF report with all player analytics.")
    
    # Report options
    report_period = st.selectbox(
        "Select report period:",
        ["All Time", "Last 30 Days", "Last 7 Days", "Custom"],
        key="report_period_selector"
    )
    
    if report_period == "Custom":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", key="report_start_date")
        with col2:
            end_date = st.date_input("End Date", key="report_end_date")
    
    include_sections = st.multiselect(
        "Select sections to include:",
        ["Executive Summary", "Performance Metrics", "Trend Analysis", 
         "Strengths & Weaknesses", "Comparisons", "Recommendations"],
        default=["Executive Summary", "Performance Metrics", "Trend Analysis"],
        key="report_sections"
    )
    
    if st.button("Generate Report", type="primary", key="generate_report_btn"):
        generate_player_report(player_data, all_data, player_name, api_key, include_sections)

# Helper functions for player profile

def create_profile_summary(player_data: pd.DataFrame, total_sessions: int) -> str:
    """Create profile summary for AI assistant"""
    available_metrics = [m for m in METRICS if m in player_data.columns]
    
    summary = f"""
    Player Profile: {player_data['Player Name'].iloc[0]}
    
    Career Statistics:
    - Total Sessions: {total_sessions}
    """
    
    if "Total Distance" in available_metrics:
        summary += f"\n- Average Distance: {player_data['Total Distance'].mean():.2f} km"
    if "Max Speed" in available_metrics:
        summary += f"\n- Top Speed Recorded: {player_data['Max Speed'].max():.1f} km/h"
    if "No of Sprints" in available_metrics:
        summary += f"\n- Total Sprints: {player_data['No of Sprints'].sum()}"
    
    match_count = len(player_data[player_data['Data Source']=='Match'])
    training_count = len(player_data[player_data['Data Source']=='Training'])
    summary += f"\n\nData includes {match_count} matches and {training_count} training sessions."
    
    return summary

def display_data_source_metrics(data: pd.DataFrame, title: str, color: str):
    """Display metrics for a specific data source"""
    st.markdown(f"#### {title}")
    
    if not data.empty:
        available_metrics = [m for m in METRICS if m in data.columns]
        if available_metrics:
            metrics = data[available_metrics].mean()
            
            fig = go.Figure(data=[
                go.Bar(
                    x=available_metrics,
                    y=metrics.values,
                    marker_color=color,
                    text=[f"{v:.1f}" for v in metrics.values],
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                title=f"Average {title.split()[0]} Metrics",
                plot_bgcolor=ThemeConfig.CARD_BACKGROUND,
                paper_bgcolor=ThemeConfig.BACKGROUND_COLOR,
                font=dict(color=ThemeConfig.TEXT_COLOR),
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No {title.lower()} data available")

def display_performance_rating(player_data: pd.DataFrame, all_data: pd.DataFrame):
    """Display overall performance rating"""
    st.markdown("#### Performance Rating")
    
    # Calculate overall performance score
    available_metrics = [m for m in METRICS if m in player_data.columns and m in all_data.columns]
    
    if available_metrics:
        player_avg = player_data[available_metrics].mean()
        all_avg = all_data[available_metrics].mean()
        
        performance_score = calculate_performance_score(player_avg, all_data)
        
        # Display rating
        rating_color = (
            ThemeConfig.SUCCESS_COLOR if performance_score > 110 else
            ThemeConfig.SECONDARY_COLOR if performance_score > 90 else
            ThemeConfig.WARNING_COLOR
        )
        
        st.markdown(f"""
        <div style='text-align: center; background-color: {ThemeConfig.CARD_BACKGROUND}; 
                    padding: 30px; border-radius: 10px; border: 2px solid {rating_color};'>
            <h1 style='color: {rating_color}; font-size: 4em;'>{performance_score:.0f}</h1>
            <p style='font-size: 1.2em;'>Overall Performance Score</p>
            <p style='opacity: 0.7;'>(100 = Team Average)</p>
        </div>
        """, unsafe_allow_html=True)

def display_metric_trend(player_data: pd.DataFrame, metric: str):
    """Display trend for a specific metric"""
    if metric in player_data.columns:
        fig = go.Figure()
        
        # Add actual values
        fig.add_trace(go.Scatter(
            x=player_data["Session_Number"],
            y=player_data[metric],
            mode='lines+markers',
            name='Actual',
            line=dict(color=ThemeConfig.PRIMARY_COLOR, width=2),
            marker=dict(size=8)
        ))
        
        # Add moving average
        window = min(5, len(player_data) // 2)
        if window >= 2:
            player_data[f"{metric}_MA"] = player_data[metric].rolling(window=window, center=True).mean()
            
            fig.add_trace(go.Scatter(
                x=player_data["Session_Number"],
                y=player_data[f"{metric}_MA"],
                mode='lines',
                name=f'{window}-Session MA',
                line=dict(color=ThemeConfig.SECONDARY_COLOR, width=2, dash='dash')
            ))
        
        # Add trend line
        if len(player_data) > 1:
            z = np.polyfit(player_data["Session_Number"], player_data[metric].fillna(0), 1)
            p = np.poly1d(z)
            
            fig.add_trace(go.Scatter(
                x=player_data["Session_Number"],
                y=p(player_data["Session_Number"]),
                mode='lines',
                name='Trend',
                line=dict(color=ThemeConfig.ACCENT_COLOR, width=2, dash='dot')
            ))
        
        fig.update_layout(
            title=f"{metric} Over Time",
            xaxis_title="Session Number",
            yaxis_title=metric,
            plot_bgcolor=ThemeConfig.CARD_BACKGROUND,
            paper_bgcolor=ThemeConfig.BACKGROUND_COLOR,
            font=dict(color=ThemeConfig.TEXT_COLOR),
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Trend analysis metrics
        if len(player_data) > 1 and 'z' in locals():
            slope = z[0]
            trend_direction = "Improving 📈" if slope > 0 else "Declining 📉" if slope < 0 else "Stable ➡️"
            change_per_session = abs(slope)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Trend", trend_direction)
            with col2:
                st.metric("Change/Session", f"{change_per_session:.3f}")
            with col3:
                recent_avg = player_data[metric].tail(5).mean()
                overall_avg = player_data[metric].mean()
                recent_vs_avg = ((recent_avg - overall_avg) / overall_avg * 100) if overall_avg > 0 else 0
                st.metric("Recent vs Average", f"{recent_vs_avg:+.1f}%")

def calculate_player_percentiles(player_data: pd.DataFrame, all_data: pd.DataFrame) -> dict:
    """Calculate percentiles for all metrics"""
    player_avg = player_data[METRICS].mean()
    percentiles = {}
    
    for metric in METRICS:
        if metric in player_avg.index and metric in all_data.columns:
            all_values = all_data[metric].dropna()
            player_value = player_avg[metric]
            percentile = (all_values < player_value).sum() / len(all_values) * 100
            percentiles[metric] = percentile
    
    return percentiles

def display_percentile_radar(percentiles: dict, player_name: str):
    """Display percentile radar chart"""
    if percentiles:
        metrics = list(percentiles.keys())
        values = list(percentiles.values())
        
        fig = create_plotly_radar(
            [values],
            metrics,
            "Performance Percentiles",
            [player_name]
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_strengths_weaknesses(percentiles: dict):
    """Display strengths and weaknesses analysis"""
    sorted_metrics = sorted(percentiles.items(), key=lambda x: x[1], reverse=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💪 Core Strengths")
        for metric, percentile in sorted_metrics[:3]:
            if percentile >= 75:
                badge = "Elite"
                color = ThemeConfig.SUCCESS_COLOR
            elif percentile >= 50:
                badge = "Strong"
                color = ThemeConfig.SECONDARY_COLOR
            else:
                badge = "Average"
                color = ThemeConfig.ACCENT_COLOR
            
            st.markdown(f"""
            <div style='background-color: {ThemeConfig.CARD_BACKGROUND}; padding: 10px; 
                        border-radius: 5px; margin: 5px 0; border-left: 3px solid {color};'>
                <strong>{metric}</strong> - {badge}<br>
                <span style='color: {color};'>{percentile:.0f}th percentile</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📈 Development Opportunities")
        for metric, percentile in sorted_metrics[-3:]:
            improvement_potential = 100 - percentile
            
            st.markdown(f"""
            <div style='background-color: {ThemeConfig.CARD_BACKGROUND}; padding: 10px; 
                        border-radius: 5px; margin: 5px 0; border-left: 3px solid {ThemeConfig.WARNING_COLOR};'>
                <strong>{metric}</strong><br>
                <span style='color: {ThemeConfig.WARNING_COLOR};'>
                    {percentile:.0f}th percentile 
                    ({improvement_potential:.0f}% improvement potential)
                </span>
            </div>
            """, unsafe_allow_html=True)

def display_performance_consistency(player_data: pd.DataFrame):
    """Display performance consistency analysis"""
    st.markdown("#### Performance Consistency")
    
    consistency_scores = {}
    available_metrics = [m for m in METRICS if m in player_data.columns]
    
    for metric in available_metrics:
        values = player_data[metric].dropna()
        if len(values) > 1 and values.mean() > 0:
            cv = values.std() / values.mean() * 100
            consistency = 100 - min(cv, 100)
            consistency_scores[metric] = consistency
    
    if consistency_scores:
        consistency_df = pd.DataFrame(
            list(consistency_scores.items()),
            columns=["Metric", "Consistency %"]
        ).sort_values("Consistency %", ascending=False)
        
        fig = px.bar(
            consistency_df,
            x="Consistency %",
            y="Metric",
            orientation='h',
            color="Consistency %",
            color_continuous_scale=["red", "yellow", "green"],
            range_color=[0, 100],
            title="Metric Consistency (Higher = More Consistent)",
            height=400
        )
        
        fig.update_layout(
            plot_bgcolor=ThemeConfig.CARD_BACKGROUND,
            paper_bgcolor=ThemeConfig.BACKGROUND_COLOR,
            font=dict(color=ThemeConfig.TEXT_COLOR),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

def generate_player_report(player_data: pd.DataFrame, all_data: pd.DataFrame, 
                          player_name: str, api_key: str, sections: list):
    """Generate comprehensive player report"""
    with st.spinner("Generating report..."):
        # Create report content
        report_content = f"""
# Performance Report: {player_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Executive Summary

Total Sessions Analyzed: {len(player_data)}
- Matches: {len(player_data[player_data['Data Source'] == 'Match'])}
- Training: {len(player_data[player_data['Data Source'] == 'Training'])}

### Key Performance Indicators
"""
        
        # Add metrics
        available_metrics = [m for m in METRICS if m in player_data.columns]
        for metric in available_metrics:
            avg_value = player_data[metric].mean()
            if metric in all_data.columns:
                percentile = (all_data[metric] < avg_value).sum() / len(all_data[metric]) * 100
                report_content += f"\n- **{metric}**: {avg_value:.2f} ({percentile:.0f}th percentile)"
        
        # Performance rating
        if available_metrics:
            performance_score = calculate_performance_score(
                player_data[available_metrics].mean(), 
                all_data
            )
            report_content += f"\n\n### Overall Performance Score: {performance_score:.0f}/100"
        
        # AI-generated recommendations
        if "Recommendations" in sections:
            report_summary = f"""
            Player: {player_name}
            Performance Score: {performance_score:.0f}/100
            Sessions: {len(player_data)}
            
            Please provide:
            1. Training recommendations
            2. Tactical suggestions
            3. Recovery considerations
            4. Development priorities
            """
            
            recommendations = get_ai_coach_insights("Player Report Recommendations", report_summary, api_key)
            report_content += f"\n\n## AI Coach Recommendations\n\n{recommendations}"
        
        # Create download button
        st.download_button(
            label="📥 Download Report",
            data=report_content,
            file_name=f"{player_name}_report_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            key="download_report_btn"
        )
        
        st.success("✅ Report generated successfully!")
