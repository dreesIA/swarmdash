"""Calculation utilities"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from core.constants import METRICS, PERFORMANCE_WEIGHTS

def calculate_percentile_values(selected_df: pd.DataFrame, full_df: pd.DataFrame, 
                               metrics: List[str]) -> pd.DataFrame:
    """Calculate percentile values for radar charts"""
    percentile_df = selected_df.copy()
    for metric in metrics:
        if metric in full_df.columns:
            all_values = full_df[metric].dropna()
            if len(all_values) > 0:
                percentile_df[metric] = selected_df[metric].apply(
                    lambda val: (all_values < val).sum() / len(all_values) * 100 
                    if pd.notna(val) else 0
                )
    return percentile_df

def calculate_growth_rate(data: pd.Series) -> float:
    """Calculate growth rate from time series data"""
    if len(data) < 2:
        return 0.0
    
    first_value = data.iloc[0]
    last_value = data.iloc[-1]
    
    if first_value == 0:
        return 100.0 if last_value > 0 else 0.0
    
    return ((last_value - first_value) / first_value) * 100

def calculate_consistency_score(data: pd.Series) -> float:
    """Calculate consistency score (lower CV = more consistent)"""
    if len(data) < 2 or data.mean() == 0:
        return 100.0
    
    cv = (data.std() / data.mean()) * 100
    return max(0, 100 - cv)

def calculate_z_scores(df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
    """Calculate z-scores for normalization"""
    z_scores = df.copy()
    for metric in metrics:
        if metric in df.columns:
            mean = df[metric].mean()
            std = df[metric].std()
            if std > 0:
                z_scores[metric] = (df[metric] - mean) / std
            else:
                z_scores[metric] = 0
    return z_scores

def calculate_composite_score(data: pd.Series, weights: Dict[str, float]) -> float:
    """Calculate weighted composite score"""
    score = 0
    total_weight = 0
    
    for metric, weight in weights.items():
        if metric in data.index and pd.notna(data[metric]):
            score += data[metric] * weight
            total_weight += weight
    
    return score / total_weight if total_weight > 0 else 0

def identify_outliers(data: pd.Series, threshold: float = 2.5) -> pd.Series:
    """Identify outliers using z-score method"""
    if len(data) < 3:
        return pd.Series(False, index=data.index)
    
    z_scores = np.abs((data - data.mean()) / data.std())
    return z_scores > threshold

def calculate_trend_coefficient(x: np.array, y: np.array) -> Tuple[float, float]:
    """Calculate trend line coefficients"""
    if len(x) < 2 or len(y) < 2:
        return 0.0, np.mean(y) if len(y) > 0 else 0.0
    
    coefficients = np.polyfit(x, y, 1)
    return coefficients[0], coefficients[1]  # slope, intercept

def calculate_performance_index(player_metrics: pd.Series, team_metrics: pd.Series) -> float:
    """Calculate performance index relative to team average"""
    if team_metrics.empty or player_metrics.empty:
        return 100.0
    
    index_values = []
    for metric in METRICS:
        if metric in player_metrics.index and metric in team_metrics.index:
            team_val = team_metrics[metric]
            player_val = player_metrics[metric]
            if team_val > 0:
                index_values.append((player_val / team_val) * 100)
    
    return np.mean(index_values) if index_values else 100.0

def calculate_load_score_advanced(df: pd.DataFrame) -> pd.Series:
    """Calculate advanced load score with injury risk factors"""
    base_weights = {
        "Total Distance": 0.25,
        "Sprint Distance": 0.20,
        "High Speed Running": 0.20,
        "Accelerations": 0.15,
        "Decelerations": 0.15,
        "Max Speed": 0.05
    }
    
    load_score = pd.Series(0, index=df.index)
    
    for metric, weight in base_weights.items():
        if metric in df.columns:
            # Normalize to 0-100 scale
            normalized = (df[metric] - df[metric].min()) / (df[metric].max() - df[metric].min()) * 100
            load_score += normalized * weight
    
    return load_score

def calculate_fatigue_index(current_load: float, historical_avg: float, 
                           historical_std: float) -> str:
    """Calculate fatigue index based on load deviation"""
    if historical_std == 0:
        return "Normal"
    
    z_score = (current_load - historical_avg) / historical_std
    
    if z_score > 2:
        return "High Risk"
    elif z_score > 1:
        return "Moderate Risk"
    elif z_score < -1:
        return "Under-loaded"
    else:
        return "Normal"

def calculate_session_intensity(df: pd.DataFrame) -> pd.Series:
    """Calculate session intensity score"""
    intensity_metrics = {
        "Max Speed": 0.3,
        "Sprint Distance": 0.25,
        "High Speed Running": 0.25,
        "No of Sprints": 0.2
    }
    
    intensity_score = pd.Series(0, index=df.index)
    
    for metric, weight in intensity_metrics.items():
        if metric in df.columns:
            intensity_score += df[metric] * weight
    
    return intensity_score

def calculate_recovery_time(load_score: float, age: Optional[int] = None) -> int:
    """Estimate recovery time based on load score and age"""
    base_recovery = 24  # hours
    
    # Load factor
    if load_score > 80:
        base_recovery += 24
    elif load_score > 60:
        base_recovery += 12
    
    # Age factor (if provided)
    if age:
        if age > 30:
            base_recovery += 12
        elif age > 35:
            base_recovery += 24
    
    return base_recovery
