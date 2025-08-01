"""Sidebar configuration and navigation"""
import streamlit as st
from PIL import Image, ImageDraw
from core.theme import ThemeConfig
from typing import Tuple, Optional

def create_circular_image(image_path: str) -> Optional[Image.Image]:
    """Create a circular version of an image"""
    try:
        import os
        if not os.path.exists(image_path):
            return None
        
        # Open and convert image
        img = Image.open(image_path)
        
        # If JPEG, it might not have alpha channel
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Get the smaller dimension to make it square
        size = min(img.size)
        
        # Create a mask
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        
        # Crop image to square
        left = (img.width - size) // 2
        top = (img.height - size) // 2
        img_cropped = img.crop((left, top, left + size, top + size))
        
        # Create output image with transparency
        output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        output.paste(img_cropped, (0, 0))
        output.putalpha(mask)
        
        return output
        
    except Exception as e:
        return None

def setup_sidebar(team_config: dict) -> Tuple[str, str]:
    """Configure the sidebar with logo and navigation"""
    # Back to teams button
    if st.sidebar.button("← Back to Teams", use_container_width=True):
        st.session_state.selected_team = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Team logo
    try:
        logo = create_circular_image(team_config["logo"])
        if logo:
            st.sidebar.image(logo, width=200)
        else:
            st.sidebar.markdown(
                f"<h1 style='color: {ThemeConfig.PRIMARY_COLOR}; text-align: center;'>"
                f"{st.session_state.selected_team}</h1>", 
                unsafe_allow_html=True
            )
    except:
        st.sidebar.markdown(
            f"<h1 style='color: {ThemeConfig.PRIMARY_COLOR}; text-align: center;'>"
            f"{st.session_state.selected_team}</h1>", 
            unsafe_allow_html=True
        )
    
    st.sidebar.markdown("---")
    
    # API Key input
    st.sidebar.markdown("### 🤖 AI Assistant Settings")
    api_key = st.sidebar.text_input(
        "Enter OpenAI API Key:", 
        type="password", 
        help="Your OpenAI API key for AI Coach insights"
    )
    
    st.sidebar.markdown("---")
    
    # Report type selection
    report_type = st.sidebar.selectbox(
        "📊 Select Report Type",
        ["Match Report", "Weekly Training Report", "Daily Training Report", 
         "Compare Players", "Player Profile"],
        help="Choose the type of analysis you want to view"
    )
    
    return report_type, api_key
