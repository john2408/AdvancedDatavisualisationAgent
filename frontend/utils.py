"""
Utility functions for handling CSS and other frontend assets.
"""
import streamlit as st
import os
from pathlib import Path

def load_css(file_path: str):
    """
    Load CSS from a file and inject it into the Streamlit app.
    
    Args:
        file_path (str): Path to the CSS file relative to the project root
    """
    # Get the absolute path to the CSS file
    current_dir = Path(__file__).parent.parent
    css_path = current_dir / file_path
    
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Inject CSS into Streamlit
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.error(f"CSS file not found: {css_path}")
    except Exception as e:
        st.error(f"Error loading CSS file: {e}")

def load_multiple_css(file_paths: list):
    """
    Load multiple CSS files.
    
    Args:
        file_paths (list): List of CSS file paths relative to the project root
    """
    for file_path in file_paths:
        load_css(file_path)
