"""Export and report generation utilities"""
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from core.theme import ThemeConfig

def generate_pdf_report(data: Dict, filename: str) -> bytes:
    """Generate PDF report from data dictionary"""
    # This would integrate with a PDF library like ReportLab
    # For now, returning a placeholder
    return b"PDF Report Content"

def export_to_excel(dataframes: Dict[str, pd.DataFrame], filename: str) -> bytes:
    """Export multiple dataframes to Excel with formatting"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Add formatting
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D72638',
                'font_color': '#FFFFFF',
                'border': 1
            })
            
            # Write headers with formatting
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Auto-adjust column widths
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(idx, idx, max_len)
    
    return output.getvalue()

def create_report_markdown(player_name: str, data: Dict, sections: List[str]) -> str:
    """Create markdown report content"""
    report = f"""# Performance Report: {player_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

"""
    
    if "Executive Summary" in sections:
        report += create_executive_summary(data)
    
    if "Performance Metrics" in sections:
        report += create_performance_metrics_section(data)
    
    if "Trend Analysis" in sections:
        report += create_trend_analysis_section(data)
    
    if "Strengths & Weaknesses" in sections:
        report += create_strengths_section(data)
    
    if "Comparisons" in sections:
        report += create_comparisons_section(data)
    
    return report

def create_executive_summary(data: Dict) -> str:
    """Create executive summary section"""
    return f"""## Executive Summary

### Overview
- Total Sessions: {data.get('total_sessions', 0)}
- Date Range: {data.get('date_range', 'N/A')}
- Performance Score: {data.get('performance_score', 0):.0f}/100

### Key Highlights
{format_bullet_points(data.get('highlights', []))}

### Areas of Excellence
{format_bullet_points(data.get('strengths', []))}

### Development Priorities
{format_bullet_points(data.get('development_areas', []))}

---

"""

def create_performance_metrics_section(data: Dict) -> str:
    """Create performance metrics section"""
    metrics = data.get('metrics', {})
    
    section = "## Performance Metrics\n\n"
    section += "| Metric | Value | Percentile | Trend |\n"
    section += "|--------|-------|------------|-------|\n"
    
    for metric, values in metrics.items():
        section += f"| {metric} | {values['value']:.2f} | {values['percentile']:.0f}th | {values['trend']} |\n"
    
    section += "\n---\n\n"
    return section

def create_trend_analysis_section(data: Dict) -> str:
    """Create trend analysis section"""
    return f"""## Trend Analysis

### Performance Evolution
{data.get('trend_summary', 'No trend data available.')}

### Key Patterns
{format_bullet_points(data.get('patterns', []))}

### Projections
{data.get('projections', 'Maintain current training intensity for continued improvement.')}

---

"""

def create_strengths_section(data: Dict) -> str:
    """Create strengths and weaknesses section"""
    return f"""## Strengths & Development Areas

### Core Strengths
{format_bullet_points(data.get('core_strengths', []))}

### Competitive Advantages
{format_bullet_points(data.get('advantages', []))}

### Development Priorities
{format_bullet_points(data.get('development_priorities', []))}

### Recommended Actions
{format_bullet_points(data.get('recommendations', []))}

---

"""

def create_comparisons_section(data: Dict) -> str:
    """Create comparisons section"""
    return f"""## Comparative Analysis

### Team Comparison
{data.get('team_comparison', 'Performance metrics compared to team averages.')}

### Position Group Analysis
{data.get('position_analysis', 'Analysis within position group.')}

### League Benchmarks
{data.get('league_benchmarks', 'Comparison to league standards where available.')}

---

"""

def format_bullet_points(items: List[str]) -> str:
    """Format list as markdown bullet points"""
    if not items:
        return "- No data available\n"
    return "\n".join([f"- {item}" for item in items]) + "\n"

def export_to_json(data: Dict, filename: str) -> str:
    """Export data to JSON format"""
    # Convert pandas objects to serializable format
    serializable_data = {}
    for key, value in data.items():
        if isinstance(value, pd.DataFrame):
            serializable_data[key] = value.to_dict(orient='records')
        elif isinstance(value, pd.Series):
            serializable_data[key] = value.to_dict()
        else:
            serializable_data[key] = value
    
    return json.dumps(serializable_data, indent=2, default=str)

def create_comparison_chart(data: pd.DataFrame, player_names: List[str], 
                           metric: str, output_format: str = 'base64') -> str:
    """Create comparison chart for export"""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Filter data for selected players
    chart_data = data[data['Player Name'].isin(player_names)]
    
    # Create bar chart
    x_pos = range(len(player_names))
    values = [chart_data[chart_data['Player Name'] == p][metric].mean() 
              for p in player_names]
    
    bars = ax.bar(x_pos, values, color=ThemeConfig.PRIMARY_COLOR)
    
    # Customize chart
    ax.set_xlabel('Players', fontsize=12)
    ax.set_ylabel(metric, fontsize=12)
    ax.set_title(f'{metric} Comparison', fontsize=16, color=ThemeConfig.PRIMARY_COLOR)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(player_names, rotation=45, ha='right')
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}', ha='center', va='bottom')
    
    # Style
    ax.set_facecolor(ThemeConfig.CARD_BACKGROUND)
    fig.patch.set_facecolor(ThemeConfig.BACKGROUND_COLOR)
    
    plt.tight_layout()
    
    if output_format == 'base64':
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, 
                   facecolor=ThemeConfig.BACKGROUND_COLOR)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        return f"data:image/png;base64,{image_base64}"
    else:
        return fig

def generate_csv_export(df: pd.DataFrame, filename: str) -> str:
    """Generate CSV export with proper formatting"""
    # Round numeric columns
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df_export = df.copy()
    df_export[numeric_columns] = df_export[numeric_columns].round(2)
    
    return df_export.to_csv(index=False)

def create_session_summary_table(sessions_data: pd.DataFrame) -> str:
    """Create formatted session summary table"""
    summary = sessions_data.groupby(['Session Type', 'Data Source']).agg({
        'Total Distance': ['mean', 'std'],
        'Max Speed': ['mean', 'max'],
        'No of Sprints': ['mean', 'sum']
    }).round(2)
    
    return summary.to_html(classes='summary-table')

def export_player_card(player_data: Dict) -> str:
    """Create player card for export/sharing"""
    card_html = f"""
    <div style="background-color: {ThemeConfig.CARD_BACKGROUND}; 
                padding: 20px; border-radius: 10px; 
                border: 2px solid {ThemeConfig.PRIMARY_COLOR};
                max-width: 400px; margin: auto;">
        <h2 style="color: {ThemeConfig.PRIMARY_COLOR}; text-align: center;">
            {player_data['name']}
        </h2>
        <div style="text-align: center; margin: 20px 0;">
            <div style="font-size: 3em; color: {ThemeConfig.PRIMARY_COLOR};">
                {player_data['performance_score']:.0f}
            </div>
            <div style="color: {ThemeConfig.TEXT_COLOR}; opacity: 0.8;">
                Performance Score
            </div>
        </div>
        <hr style="border-color: {ThemeConfig.PRIMARY_COLOR};">
        <div style="margin: 20px 0;">
            <h4 style="color: {ThemeConfig.TEXT_COLOR};">Key Stats</h4>
            <ul style="list-style: none; padding: 0;">
    """
    
    for stat, value in player_data['key_stats'].items():
        card_html += f"""
                <li style="margin: 10px 0; color: {ThemeConfig.TEXT_COLOR};">
                    <strong>{stat}:</strong> {value}
                </li>
        """
    
    card_html += """
            </ul>
        </div>
    </div>
    """
    
    return card_html

def create_training_load_chart(load_data: pd.DataFrame, player_name: str) -> str:
    """Create training load progression chart"""
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                   gridspec_kw={'height_ratios': [3, 1]})
    
    # Main load chart
    sessions = range(len(load_data))
    ax1.plot(sessions, load_data['Load Score'], 
            color=ThemeConfig.PRIMARY_COLOR, linewidth=2, label='Load Score')
    ax1.fill_between(sessions, load_data['Load Score'], 
                    alpha=0.3, color=ThemeConfig.PRIMARY_COLOR)
    
    # Add rolling average
    if len(load_data) > 7:
        rolling_avg = load_data['Load Score'].rolling(window=7).mean()
        ax1.plot(sessions, rolling_avg, 
                color=ThemeConfig.SECONDARY_COLOR, 
                linewidth=2, linestyle='--', label='7-day Average')
    
    ax1.set_ylabel('Load Score', fontsize=12)
    ax1.set_title(f'Training Load Progression - {player_name}', 
                 fontsize=16, color=ThemeConfig.PRIMARY_COLOR)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Load zones chart
    load_zones = pd.cut(load_data['Load Score'], 
                       bins=[0, 40, 70, 100], 
                       labels=['Low', 'Optimal', 'High'])
    zone_counts = load_zones.value_counts()
    
    colors = [ThemeConfig.SUCCESS_COLOR, ThemeConfig.SECONDARY_COLOR, ThemeConfig.WARNING_COLOR]
    ax2.bar(zone_counts.index, zone_counts.values, color=colors)
    ax2.set_ylabel('Sessions', fontsize=12)
    ax2.set_xlabel('Load Zone', fontsize=12)
    ax2.set_title('Load Distribution', fontsize=14)
    
    # Style
    for ax in [ax1, ax2]:
        ax.set_facecolor(ThemeConfig.CARD_BACKGROUND)
    fig.patch.set_facecolor(ThemeConfig.BACKGROUND_COLOR)
    
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, 
               facecolor=ThemeConfig.BACKGROUND_COLOR)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return f"data:image/png;base64,{image_base64}"

def export_team_report(team_data: Dict, format: str = 'html') -> str:
    """Export comprehensive team report"""
    if format == 'html':
        report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Team Performance Report</title>
            <style>
                body {{
                    background-color: {ThemeConfig.BACKGROUND_COLOR};
                    color: {ThemeConfig.TEXT_COLOR};
                    font-family: Arial, sans-serif;
                    padding: 20px;
                }}
                h1, h2, h3 {{
                    color: {ThemeConfig.PRIMARY_COLOR};
                }}
                .metric-card {{
                    background-color: {ThemeConfig.CARD_BACKGROUND};
                    padding: 20px;
                    border-radius: 10px;
                    margin: 10px 0;
                    border: 1px solid {ThemeConfig.PRIMARY_COLOR};
                }}
                .chart-container {{
                    margin: 20px 0;
                    text-align: center;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid {ThemeConfig.PRIMARY_COLOR};
                }}
                th {{
                    background-color: {ThemeConfig.PRIMARY_COLOR};
                    color: white;
                }}
            </style>
        </head>
        <body>
            <h1>Team Performance Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            
            <div class="metric-card">
                <h2>Team Overview</h2>
                <p>Total Players: {team_data['total_players']}</p>
                <p>Sessions Analyzed: {team_data['total_sessions']}</p>
                <p>Average Team Performance Score: {team_data['avg_performance_score']:.1f}</p>
            </div>
            
            <div class="metric-card">
                <h2>Top Performers</h2>
                <table>
                    <tr>
                        <th>Rank</th>
                        <th>Player</th>
                        <th>Performance Score</th>
                        <th>Key Strength</th>
                    </tr>
        """
        
        for i, player in enumerate(team_data['top_performers'], 1):
            report += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{player['name']}</td>
                        <td>{player['score']:.1f}</td>
                        <td>{player['strength']}</td>
                    </tr>
            """
        
        report += """
                </table>
            </div>
            
            <div class="metric-card">
                <h2>Team Metrics Summary</h2>
                <div class="chart-container">
                    <!-- Chart would be inserted here -->
                </div>
            </div>
            
        </body>
        </html>
        """
        
        return report
    
    elif format == 'json':
        return export_to_json(team_data, 'team_report.json')
    
    else:
        return "Format not supported"

def create_backup_data(all_data: pd.DataFrame, metadata: Dict) -> bytes:
    """Create backup of all data with metadata"""
    backup = {
        'metadata': {
            'created': datetime.now().isoformat(),
            'version': '1.0',
            'team': metadata.get('team', 'Unknown'),
            'total_records': len(all_data)
        },
        'data': all_data.to_dict(orient='records'),
        'columns': list(all_data.columns),
        'dtypes': {col: str(dtype) for col, dtype in all_data.dtypes.items()}
    }
    
    return json.dumps(backup, indent=2, default=str).encode('utf-8')
