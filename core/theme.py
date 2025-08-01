"""Theme configuration and styling"""
import streamlit as st

class ThemeConfig:
    """Color scheme and styling constants"""
    PRIMARY_COLOR = "#D72638"
    SECONDARY_COLOR = "#ffffff"
    BACKGROUND_COLOR = "#1A1A1D"
    CARD_BACKGROUND = "#2D2D30"
    TEXT_COLOR = "#FFFFFF"
    ACCENT_COLOR = "#FF6B6B"
    SUCCESS_COLOR = "#4ECDC4"
    WARNING_COLOR = "#FFE66D"

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Swarm Performance Analytics Hub",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'About': "SSA Swarm Performance Analytics Dashboard"
        }
    )

def setup_theme():
    """Apply custom CSS theme"""
    st.markdown(f"""
    <style>
        /* Main container styling */
        .main {{
            background-color: {ThemeConfig.BACKGROUND_COLOR};
            color: {ThemeConfig.TEXT_COLOR};
        }}
        
        /* Sidebar styling */
        .css-1d391kg {{
            background-color: {ThemeConfig.CARD_BACKGROUND};
        }}
        
        /* Headers styling */
        h1, h2, h3, h4, h5, h6 {{
            color: {ThemeConfig.PRIMARY_COLOR};
            font-weight: 600;
        }}
        
        /* Metric cards */
        div[data-testid="metric-container"] {{
            background-color: {ThemeConfig.CARD_BACKGROUND};
            border: 1px solid {ThemeConfig.PRIMARY_COLOR};
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        /* Dataframe styling */
        .dataframe {{
            background-color: {ThemeConfig.CARD_BACKGROUND};
            color: {ThemeConfig.TEXT_COLOR};
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {ThemeConfig.CARD_BACKGROUND};
            border-radius: 10px;
        }}
        
        /* Button styling */
        .stButton > button {{
            background-color: {ThemeConfig.PRIMARY_COLOR};
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s;
        }}
        
        .stButton > button:hover {{
            background-color: {ThemeConfig.SECONDARY_COLOR};
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            background-color: {ThemeConfig.CARD_BACKGROUND};
            color: {ThemeConfig.TEXT_COLOR};
            border-radius: 5px;
        }}
        
        /* Custom info box */
        .info-box {{
            background-color: {ThemeConfig.CARD_BACKGROUND};
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid {ThemeConfig.PRIMARY_COLOR};
            margin: 10px 0;
        }}
        
        /* Custom metric box */
        .custom-metric {{
            text-align: center;
            padding: 20px;
            background-color: {ThemeConfig.CARD_BACKGROUND};
            border-radius: 10px;
            border: 1px solid {ThemeConfig.PRIMARY_COLOR};
            transition: all 0.3s;
        }}
        
        .custom-metric:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(215, 38, 56, 0.3);
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: {ThemeConfig.PRIMARY_COLOR};
        }}
        
        .metric-label {{
            font-size: 1.1em;
            color: {ThemeConfig.TEXT_COLOR};
            opacity: 0.8;
        }}

        /* Team card styling */
        .team-card {{
            background-color: {ThemeConfig.CARD_BACKGROUND};
            border: 2px solid {ThemeConfig.PRIMARY_COLOR};
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            margin: 10px;
        }}
        
        .team-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 10px 30px rgba(215, 38, 56, 0.4);
            border-color: {ThemeConfig.SECONDARY_COLOR};
        }}
    </style>
    """, unsafe_allow_html=True)
