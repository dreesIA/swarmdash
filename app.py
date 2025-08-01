import streamlit as st
from core.theme import setup_theme, setup_page_config
from teams_config import TEAMS_CONFIG
from pages.landing import render_landing_page
from pages.match_report import render_match_report
from pages.training_weekly import render_weekly_training_report
from pages.training_daily import render_daily_training_report
from pages.player_comparison import render_player_comparison
from pages.player_profile import render_player_profile
from components.sidebar import setup_sidebar

def main():
    """Main application entry point"""
    # Setup page configuration and theme
    setup_page_config()
    setup_theme()
    
    # Initialize session state
    if 'selected_team' not in st.session_state:
        st.session_state.selected_team = None
    
    # Show landing page or team dashboard
    if st.session_state.selected_team is None:
        render_landing_page()
    else:
        # Get team configuration
        team_config = TEAMS_CONFIG.get(st.session_state.selected_team)
        if not team_config:
            st.error(f"Team configuration not found for {st.session_state.selected_team}")
            st.session_state.selected_team = None
            st.rerun()
            return
        
        # Setup sidebar and get selections
        report_type, api_key = setup_sidebar(team_config)
        
        # Display header
        st.markdown(f"""
        <h1 style='text-align: center; color: #D72638; font-size: 3em; margin-bottom: 0;'>
            {st.session_state.selected_team} Performance Analytics
        </h1>
        <p style='text-align: center; color: #FFFFFF; opacity: 0.8; font-size: 1.2em;'>
            {team_config['description']} - Advanced Analytics Dashboard with AI Insights
        </p>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Route to appropriate report
        if report_type == "Match Report":
            render_match_report(api_key, team_config)
        elif report_type == "Weekly Training Report":
            render_weekly_training_report(api_key, team_config)
        elif report_type == "Daily Training Report":
            render_daily_training_report(api_key, team_config)
        elif report_type == "Compare Players":
            render_player_comparison(api_key, team_config)
        elif report_type == "Player Profile":
            render_player_profile(api_key, team_config)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <p style='text-align: center; color: #FFFFFF; opacity: 0.6;'>
            Built for SSA | Powered by Statsports & Nacsport | Enhanced with AI Insights | © 2025
        </p>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
