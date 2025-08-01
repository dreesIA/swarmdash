"""Landing page for team selection"""
import streamlit as st
from teams_config import TEAMS_CONFIG
from core.theme import ThemeConfig
from components.sidebar import create_circular_image

def render_landing_page():
    """Render the landing page for team selection"""
    # Header
    st.markdown(f"""
    <h1 style='text-align: center; color: {ThemeConfig.PRIMARY_COLOR}; font-size: 3.5em; margin-bottom: 0;'>
        Swarm Performance Analytics Hub
    </h1>
    <p style='text-align: center; color: {ThemeConfig.TEXT_COLOR}; opacity: 0.8; font-size: 1.3em; margin-bottom: 50px;'>
        Select a team to access their performance dashboard
    </p>
    """, unsafe_allow_html=True)
    
    # Team selection grid
    teams_list = list(TEAMS_CONFIG.items())
    num_teams = len(teams_list)
    
    # Create rows of 3 teams each
    for row_start in range(0, num_teams, 3):
        cols = st.columns(3)
        
        # Get up to 3 teams for this row
        for col_idx in range(3):
            team_idx = row_start + col_idx
            
            if team_idx < num_teams:
                team_name, team_config = teams_list[team_idx]
                
                with cols[col_idx]:
                    # Create team card button first (full width)
                    if st.button(f"Select {team_name}", key=f"team_{team_name}", use_container_width=True):
                        st.session_state.selected_team = team_name
                        st.rerun()
                    
                    # Team logo - centered using columns
                    logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])
                    with logo_col2:
                        try:
                            logo = create_circular_image(team_config["logo"])
                            if logo:
                                st.image(logo, use_container_width=True)
                            else:
                                st.markdown(f"""
                                <div style='width: 150px; height: 150px; background-color: {ThemeConfig.PRIMARY_COLOR}; 
                                            border-radius: 50%; margin: 0 auto; display: flex; 
                                            align-items: center; justify-content: center;'>
                                    <h2 style='color: white; margin: 0;'>{team_name[:3]}</h2>
                                </div>
                                """, unsafe_allow_html=True)
                        except:
                            st.markdown(f"""
                            <div style='width: 150px; height: 150px; background-color: {ThemeConfig.PRIMARY_COLOR}; 
                                        border-radius: 50%; margin: 0 auto; display: flex; 
                                        align-items: center; justify-content: center;'>
                                <h2 style='color: white; margin: 0;'>{team_name[:3]}</h2>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Team info - ensure text is centered
                    st.markdown(f"""
                    <div style='text-align: center; width: 100%;'>
                        <h3 style='color: {ThemeConfig.PRIMARY_COLOR}; margin: 10px 0;'>{team_name}</h3>
                        <p style='color: {ThemeConfig.TEXT_COLOR}; opacity: 0.8; margin: 5px 0;'>{team_config['description']}</p>
                        <p style='color: {ThemeConfig.ACCENT_COLOR}; margin: 5px 0;'>
                            {len(team_config['match_files'])} Matches | {len(team_config['training_files'])} Training Sessions
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
