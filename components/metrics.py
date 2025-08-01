"""Metric cards and calculations"""
import pandas as pd
from typing import Optional, Dict, List
from core.theme import ThemeConfig
from core.constants import METRICS, PERFORMANCE_WEIGHTS

def create_metric_card(label: str, value: str, delta: Optional[float] = None) -> str:
    """Create a custom metric card HTML"""
    delta_html = ""
    if delta is not None:
        delta_symbol = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        delta_color_code = (ThemeConfig.SUCCESS_COLOR if delta > 0 
                           else ThemeConfig.PRIMARY_COLOR if delta < 0 
                           else ThemeConfig.TEXT_COLOR)
        delta_html = f'<div style="color: {delta_color_code}; font-size: 0.9em;">{delta_symbol} {abs(delta):.1f}%</div>'
    
    return f"""
    <div class="custom-metric">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """

def calculate_performance_score(player_data: pd.Series, all_data: pd.DataFrame) -> float:
    """Calculate weighted performance score for a player"""
    score = 0
    valid_metrics = 0
    
    for metric, weight in PERFORMANCE_WEIGHTS.items():
        if metric in player_data.index and metric in all_data.columns:
            player_value = player_data[metric]
            avg_value = all_data[metric].mean()
            if avg_value > 0:
                score += (player_value / avg_value) * weight
                valid_metrics += weight
    
    return (score / valid_metrics * 100) if valid_metrics > 0 else 0

def calculate_percentile_values(selected_df: pd.DataFrame, full_df: pd.DataFrame, 
                               metrics: List[str]) -> pd.DataFrame:
    """Calculate percentile values for radar charts"""
    percentile_df = selected_df.copy()
    for metric in metrics:
        if metric in full_df.columns:
            all_values = full_df[metric].dropna()
            percentile_df[metric] = selected_df[metric].apply(
                lambda val: (all_values < val).sum() / len(all_values) * 100 
                if pd.notna(val) else 0
            )
    return percentile_df

def create_performance_summary(df: pd.DataFrame, player_name: Optional[str] = None) -> Dict[str, str]:
    """Create a performance summary with key insights"""
    if player_name:
        df = df[df["Player Name"] == player_name]
    
    summary = {}
    if not df.empty:
        if "Total Distance" in df.columns:
            summary["Total Distance"] = f"{df['Total Distance'].mean():.2f} km"
        if "Max Speed" in df.columns:
            summary["Max Speed"] = f"{df['Max Speed'].mean():.2f} km/h"
        if "No of Sprints" in df.columns:
            summary["Sprint Count"] = f"{df['No of Sprints'].mean():.0f}"
        if "High Speed Running" in df.columns:
            summary["High Speed Running"] = f"{df['High Speed Running'].mean():.0f} m"
        if "Accelerations" in df.columns and "Decelerations" in df.columns:
            summary["Work Rate"] = f"{(df['Accelerations'].mean() + df['Decelerations'].mean()):.0f} actions"
    
    return summary

def calculate_load_score(df: pd.DataFrame) -> pd.Series:
    """Calculate composite load score for players"""
    weights = {
        "Total Distance": 0.3,
        "Sprint Distance": 0.2,
        "High Speed Running": 0.2,
        "Accelerations": 0.15,
        "Decelerations": 0.15
    }
    
    load_score = pd.Series(0, index=df.index)
    
    for metric, weight in weights.items():
        if metric in df.columns:
            load_score += df[metric] * weight
    
    return load_score
