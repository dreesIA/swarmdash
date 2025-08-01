"""AI Assistant Coach functionality"""
import streamlit as st
from typing import Optional

def get_ai_coach_insights(context: str, data_summary: str, api_key: str) -> str:
    """Get AI coach insights based on current context and data"""
    if not api_key:
        return "Please enter your OpenAI API key in the sidebar to enable AI Coach insights."
    
    try:
        import openai
    except ImportError:
        return "OpenAI library not installed. Please run: pip install openai"
    
    try:
        from openai import OpenAI
        
        # Initialize client with API key
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        You are an expert soccer coach analyzing performance data for SSA Swarm USL2 team.
        
        Current Context: {context}
        
        Data Summary:
        {data_summary}
        
        Please provide:
        1. Key insights from this data
        2. Tactical recommendations
        3. Areas of concern
        4. Positive trends to reinforce
        
        Keep your response concise and actionable, focusing on practical coaching insights.
        """
        
        # Try GPT-4 first, fall back to GPT-3.5-turbo if not available
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert soccer performance analyst and coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            # If GPT-4 fails, try GPT-3.5-turbo
            if "model" in str(e).lower() or "404" in str(e):
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert soccer performance analyst and coach."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )
                    return response.choices[0].message.content
                except Exception as fallback_error:
                    return f"AI Coach unavailable: {str(fallback_error)}. Please check your API key."
            else:
                return f"AI Coach unavailable: {str(e)}. Please check your API key."
    
    except Exception as e:
        return f"AI Coach unavailable: {str(e)}. Please ensure you have the latest OpenAI library installed."

def display_ai_assistant(context: str, data_summary: str, api_key: str):
    """Display AI assistant coach insights"""
    with st.expander("🤖 AI Assistant Coach", expanded=False):
        # Create a unique key based on context
        button_key = f"ai_button_{context.replace(' ', '_').replace('/', '_').replace(':', '_')}"
        
        if st.button("Get AI Insights", key=button_key):
            with st.spinner("Analyzing data..."):
                insights = get_ai_coach_insights(context, data_summary, api_key)
                # Store insights in session state
                st.session_state[f"insights_{button_key}"] = insights
        
        # Display insights if they exist in session state
        if f"insights_{button_key}" in st.session_state:
            st.markdown(st.session_state[f"insights_{button_key}"])
