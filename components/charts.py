"""Chart creation functions"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Optional
from core.theme import ThemeConfig
from core.constants import METRICS

def create_plotly_radar(data: List[List[float]], categories: List[str], 
                       title: str, names: Optional[List[str]] = None) -> go.Figure:
    """Create an enhanced Plotly radar chart"""
    fig = go.Figure()
    
    if names is None:
        names = [f"Player {i+1}" for i in range(len(data))]
    
    colors = [ThemeConfig.PRIMARY_COLOR, ThemeConfig.SECONDARY_COLOR, 
              ThemeConfig.ACCENT_COLOR, ThemeConfig.SUCCESS_COLOR]
    
    for i, (name, values) in enumerate(zip(names, data)):
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=name,
            line_color=colors[i % len(colors)],
            fillcolor=colors[i % len(colors)],
            opacity=0.6
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color=ThemeConfig.TEXT_COLOR)
            ),
            angularaxis=dict(
                tickfont=dict(color=ThemeConfig.TEXT_COLOR)
            ),
            bgcolor=ThemeConfig.BACKGROUND_COLOR
        ),
        showlegend=True,
        title=dict(
            text=title,
            font=dict(color=ThemeConfig.PRIMARY_COLOR, size=20)
        ),
        paper_bgcolor=ThemeConfig.BACKGROUND_COLOR,
        plot_bgcolor=ThemeConfig.BACKGROUND_COLOR,
        font=dict(color=ThemeConfig.TEXT_COLOR),
        height=500
    )
    
    return fig

def create_performance_bar_chart(data: pd.DataFrame, metric: str, 
                                title: str, show_average: bool = True) -> go.Figure:
    """Create a standardized performance bar chart"""
    chart_data = data.groupby("Player Name")[metric].mean().reset_index()
    chart_data = chart_data.sort_values(by=metric, ascending=False)
    
    fig = px.bar(
        chart_data,
        x="Player Name",
        y=metric,
        color=metric,
        color_continuous_scale=["#1A1A1D", ThemeConfig.PRIMARY_COLOR],
        title=title,
        height=400
    )
    
    fig.update_layout(
        plot_bgcolor=ThemeConfig.CARD_BACKGROUND,
        paper_bgcolor=ThemeConfig.BACKGROUND_COLOR,
        font=dict(color=ThemeConfig.TEXT_COLOR),
        xaxis=dict(tickangle=-45),
        showlegend=False
    )
    
    if show_average and not chart_data.empty:
        avg_value = chart_data[metric].mean()
        fig.add_hline(
            y=avg_value,
            line_dash="dash",
            line_color=ThemeConfig.SECONDARY_COLOR,
            annotation_text=f"Team Avg: {avg_value:.1f}",
            annotation_position="top right"
        )
    
    return fig

def create_trend_line_chart(data: pd.DataFrame, metric: str, 
                           group_by: str, time_column: str,
                           title: str) -> go.Figure:
    """Create a trend line chart with optional trend lines"""
    fig = go.Figure()
    
    # Group data
    grouped_data = data.groupby([time_column, group_by])[metric].mean().reset_index()
    
    # Add lines for each group
    for group in grouped_data[group_by].unique():
        group_data = grouped_data[grouped_data[group_by] == group]
        
        fig.add_trace(go.Scatter(
            x=group_data[time_column],
            y=group_data[metric],
            mode='lines+markers',
            name=group,
            line=dict(width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=time_column,
        yaxis_title=metric,
        plot_bgcolor=ThemeConfig.CARD_BACKGROUND,
        paper_bgcolor=ThemeConfig.BACKGROUND_COLOR,
        font=dict(color=ThemeConfig.TEXT_COLOR),
        height=500,
        hovermode='x unified'
    )
    
    return fig

def create_heatmap(data: pd.DataFrame, title: str) -> go.Figure:
    """Create a heatmap visualization"""
    fig = px.imshow(
        data,
        color_continuous_scale=["#1A1A1D", ThemeConfig.PRIMARY_COLOR],
        title=title,
        height=600
    )
    
    fig.update_layout(
        plot_bgcolor=ThemeConfig.CARD_BACKGROUND,
        paper_bgcolor=ThemeConfig.BACKGROUND_COLOR,
        font=dict(color=ThemeConfig.TEXT_COLOR)
    )
    
    return fig

def create_distribution_plot(data: pd.Series, metric: str, title: str) -> go.Figure:
    """Create a distribution plot with histogram and box plot"""
    fig = go.Figure()
    
    # Add histogram
    fig.add_trace(go.Histogram(
        x=data,
        name="Distribution",
        nbinsx=20,
        marker_color=ThemeConfig.PRIMARY_COLOR,
        opacity=0.7
    ))
    
    # Add box plot
    fig.add_trace(go.Box(
        y=data,
        name="Box Plot",
        boxpoints='all',
        jitter=0.3,
        pointpos=-1.8,
        marker_color=ThemeConfig.SECONDARY_COLOR,
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=metric,
        yaxis_title="Count",
        yaxis2=dict(
            overlaying='y',
            side='right',
            showgrid=False
        ),
        plot_bgcolor=ThemeConfig.CARD_BACKGROUND,
        paper_bgcolor=ThemeConfig.BACKGROUND_COLOR,
        font=dict(color=ThemeConfig.TEXT_COLOR),
        height=500,
        showlegend=False
    )
    
    return fig
