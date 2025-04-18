import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import io
import json
import os
from dotenv import load_dotenv
from genai_model import GenAIModel  # Import the GenAI model directly
import pytesseract
import google.generativeai as genai
import streamlit.components.v1 as components
from typing import Dict, Any, Optional, Union, List
# Load environment variables
load_dotenv("env1.env")

# Initialize GenAI Model
API_KEY = os.getenv("GOOGLE_API_KEY")
genai_model = GenAIModel(api_key=API_KEY)

# Define schemas (moved from api.py)
EMISSION_SCHEMA = {
    "type": "object",
    "properties": {
        "emission_record": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "type_obj": {"type": "string"},
                    "activity": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit": {"type": "string"},
                    "co2e_per_unit": {"type": "number"},
                    "co2e_impact_level":{"type":"string"},
                    "suggestion":{"type": "string"}
                },
                "required": ["category", "activity", "type_obj", "unit", "quantity", "co2e_per_unit","co2e_impact_level","suggestion"]
            }
        }
    },
    "required": ["emission_record"]
}

# Page config
st.set_page_config(
    page_title="EcoMate-AI",
    page_icon="🌱",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .welcome-section {
            padding: 8rem 2rem;
            background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
            border-radius: 20px;
            margin: 2rem 0;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            color: white;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .welcome-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path fill="rgba(255,255,255,0.1)" d="M0,0 L100,0 L100,100 L0,100 Z"/></svg>');
            opacity: 0.1;
            animation: pulse 4s infinite;
        }
        .main-title {
            font-size: 4.5rem;
            font-weight: 800;
            color: white;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            letter-spacing: 1px;
            animation: fadeIn 1s ease-out;
        }
        .slogan {
            font-size: 2.2rem;
            color: #E8F5E9;
            font-weight: 500;
            margin-bottom: 3rem;
            letter-spacing: 1px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
            animation: fadeIn 1s ease-out 0.3s;
        }
        .eco-icon {
            font-size: 4rem;
            margin-bottom: 1.5rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            animation: float 3s ease-in-out infinite;
        }
        .input-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem;
            animation: fadeIn 1s ease-out 0.6s;
        }
        .stTextInput > div > div > input {
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            font-size: 1.2rem;
            transition: all 0.3s ease;
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            backdrop-filter: blur(5px);
        }
        .stTextInput > div > div > input:focus {
            border-color: #E8F5E9;
            box-shadow: 0 0 0 3px rgba(232, 245, 233, 0.3);
            background-color: rgba(255, 255, 255, 0.15);
        }
        .stTextInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.7);
        }
        .stTextInput > div > div > label {
            font-size: 1.1rem;
            color: #E8F5E9;
            font-weight: 500;
        }
        .stButton > button {
            width: 100%;
            margin: 1.5rem auto 0;
            display: block;
            background-color: #E8F5E9;
            color: #1B5E20;
            border: none;
            padding: 1rem 2rem;
            border-radius: 12px;
            font-size: 1.2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            animation: fadeIn 1s ease-out 0.9s;
        }
        .stButton > button:hover {
            background-color: white;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .leaf-decoration {
            position: absolute;
            font-size: 2rem;
            opacity: 0.3;
            animation: float 4s ease-in-out infinite;
        }
        .leaf-1 { top: 20%; left: 10%; animation-delay: 0s; }
        .leaf-2 { top: 40%; right: 15%; animation-delay: 1s; }
        .leaf-3 { bottom: 20%; left: 15%; animation-delay: 2s; }
        .leaf-4 { bottom: 40%; right: 10%; animation-delay: 3s; }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'user_name' not in st.session_state:
    st.session_state.user_name = ''
if 'user_surname' not in st.session_state:
    st.session_state.user_surname = ''
if 'carbon_data' not in st.session_state:
    st.session_state.carbon_data = []
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = []

def analyze_text(text: str,context_files:Optional[List[str]] = []) -> list:
    """Analyze text directly using GenAI model"""
    try:
        result = genai_model.extract_tasks(
            text=text,
            schema=EMISSION_SCHEMA,
            context_files=[os.path.join("data", "emission_factor.pdf")]+context_files
        )
        return result['emission_record']
    except Exception as e:
        st.error(f"Error analyzing text: {str(e)}")
        return []

def analyze_receipt(image) -> list:
    """Process receipt image and extract activities"""
    try:
        text = pytesseract.image_to_string(image)
        return analyze_text(text)
    except Exception as e:
        st.error(f"Error processing receipt: {str(e)}")
        return []

def welcome_page():
    st.markdown("""
        <div class="welcome-section" style="padding: 2rem 2rem;">
            <div class="leaf-decoration leaf-1">🌿</div>
            <div class="leaf-decoration leaf-2">🍃</div>
            <div class="leaf-decoration leaf-3">🌱</div>
            <div class="leaf-decoration leaf-4">🌿</div>
            <div style='text-align: center;'>
                <div class="eco-icon" style="font-size: 2rem;">🌱</div>
                <h1 class="main-title" style="font-size: 2.5rem;">EcoMate-AI</h1>
                <h2 class="slogan" style="font-size: 1.5rem;">Small Swaps. Big Impact.</h2>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Create a container for the input and button
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Custom styled input field
            st.markdown("""
                <style>
                    .stTextInput > div > div > input {
                        background-color: rgba(255, 255, 255, 0.1);
                        border: 2px solid rgba(255, 255, 255, 0.3);
                        border-radius: 12px;
                        color: white;
                        font-size: 1.2rem;
                        text-align: center;
                        padding: 1rem;
                    }
                    .stTextInput > div > div > input:focus {
                        border-color: #E8F5E9;
                        box-shadow: 0 0 0 2px rgba(232, 245, 233, 0.3);
                    }
                    .stTextInput > div > div > input::placeholder {
                        color: rgba(255, 255, 255, 0.7);
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # Create a form to handle both Enter key and button click
            with st.form("name_form"):
                name = st.text_input(
                    "Name",
                    placeholder="Enter your name",
                    key="name_input",
                    label_visibility="collapsed"
                )
                submitted = st.form_submit_button("Get Started")
                
                if submitted or name:  # This will trigger on both button click and Enter key
                    if name.strip():
                        st.session_state.user_name = name
                        st.session_state.page = 'main'
                        st.rerun()
                    else:
                        st.error("Please enter your name to continue.")

def main_page():
    # Welcome banner with user's name
    st.markdown(f"""
        <div style='background-color: #1B5E20; padding: 2rem; border-radius: 15px; margin-bottom: 2rem;'>
            <h2 style='color: white; margin: 0; text-align: center;'>Welcome, {st.session_state.user_name}! 👋</h2>
            <p style='color: #E8F5E9; text-align: center; margin: 0.5rem 0 0;'>Let's analyze your carbon footprint together</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
            .input-section {
                background-color: #2D2D2D;
                border-radius: 15px;
                padding: 2rem;
                margin: 2rem 0;
            }
            .input-title {
                color: #FFFFFF;
                font-size: 1.5rem;
                font-weight: bold;
                margin-bottom: 1.5rem;
                text-align: center;
            }
            .input-description {
                color: #CCCCCC;
                text-align: center;
                margin-bottom: 2rem;
                font-size: 1.1rem;
            }
            .stRadio > div {
                display: flex;
                justify-content: center;
                gap: 2rem;
                margin-bottom: 2rem;
            }
            .stRadio > div > label {
                background: #1B5E20;
                padding: 1.5rem 3rem;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                cursor: pointer;
                color: #FFFFFF !important;
                font-weight: 900 !important;
                font-size: 2rem !important;
                min-width: 300px;
                text-align: center;
            }
            .stRadio > div > label[data-baseweb="radio"] {
                background: #2E7D32;
                color: #FFFFFF !important;
                font-weight: 900 !important;
                font-size: 2rem !important;
            }
            .stRadio > div > label:hover {
                background: #388E3C;
                color: #FFFFFF !important;
            }
            .upload-section {
                text-align: center;
                padding: 2rem;
                border: 2px dashed #1B5E20;
                border-radius: 15px;
                margin: 1rem 0;
                background: #3D3D3D;
            }
            .upload-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
                color: #1B5E20;
            }
            .text-input-section {
                padding: 2rem;
                background: #3D3D3D;
                border-radius: 15px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin: 1rem 0;
            }
            .stTextArea > div > div > textarea {
                border: 2px solid #1B5E20;
                border-radius: 10px;
                padding: 1rem;
                font-size: 1.1rem;
                background: #2D2D2D;
                color: #FFFFFF;
            }
            .stTextArea > div > div > textarea:focus {
                border-color: #2E7D32;
                box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.2);
            }
            .analyze-button {
                background-color: #1B5E20;
                color: white;
                border: none;
                padding: 1rem 2rem;
                border-radius: 10px;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                width: 100%;
                text-align: center;
                margin-top: 1rem;
            }
            .analyze-button:hover {
                background-color: #2E7D32;
            }
            .audio-section {
                text-align: center;
                padding: 2rem;
                background: #3D3D3D;
                border-radius: 15px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin: 1rem 0;
            }
            .audio-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
                color: #1B5E20;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown('<div class="input-title">📊 Your Personal Carbon Footprint Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="input-description">Choose how you\'d like to analyze your carbon footprint</div>', unsafe_allow_html=True)
    
    # Input method selection with enhanced styling
    input_method = st.radio(
        "Select Input Method",
        ["Upload Receipt", "Text Input", "Audio Input"],
        horizontal=True,
        label_visibility="collapsed"
    )
    attached_file_path=[]
    user_input=None
    uploaded_file=None
    audio_file=None
    if input_method == "Upload Receipt":
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown('<div class="upload-icon">📄</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #FFFFFF; font-size: 1.1rem;">Upload your receipt to analyze your purchases</p>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Receipt Upload",
            type=['png', 'jpg', 'jpeg'],
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            
            user_input=f"Extract text from Image attached:{uploaded_file.name}"
            # Create cache directory if it doesn't exist
            cache_dir = os.path.join('data', 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            
            # Save the uploaded file in cache
            file_path = os.path.join(cache_dir, uploaded_file.name)
            attached_file_path.append(file_path)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Display the saved image
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Receipt', width=200)
            
            # Show the relative path
            st.markdown(f'<p style="color: #FFFFFF; font-size: 1rem;">Image saved at: {file_path}</p>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif input_method == "Text Input":
        st.markdown('<div class="text-input-section">', unsafe_allow_html=True)
        st.markdown('<p style="color: #FFFFFF; font-size: 1.1rem; margin-bottom: 1rem;">Describe your daily activities</p>', unsafe_allow_html=True)
        user_input = st.text_area(
            "Activity Description",
            placeholder="Describe your daily activities (e.g., 'Had beef burger, took Uber, ran AC for 5 hrs')",
            height=100,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:  # Audio Input
        st.markdown('<div class="audio-section">', unsafe_allow_html=True)
        st.markdown('<div class="audio-icon">🎤</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #FFFFFF; font-size: 1.1rem; margin-bottom: 1rem;">Record your daily activities</p>', unsafe_allow_html=True)
        audio_file = st.file_uploader(
            "Audio Upload",
            type=['wav', 'mp3', 'ogg'],
            label_visibility="collapsed"
        )
        if audio_file is not None:
            st.audio(audio_file, format='audio/wav')
            # TODO: Process audio with speech-to-text
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Analyze", key="analyze_button"):
        if input_method == "Text Input" and user_input:
            pass
                
        elif input_method == "Upload Receipt" and uploaded_file:
            pass
            #st.info("Receipt analysis coming soon!")
        elif input_method == "Audio Input" and audio_file:
            st.info("Audio analysis coming soon!")
        else:
            st.warning("Please provide input to analyze")

        with st.spinner("Analyzing your activities..."):
            if user_input:
                # Get activities from backend
                activities = analyze_text(user_input,context_files=attached_file_path)
                for each_attached_file_path in attached_file_path:
                    if os.path.exists(each_attached_file_path):
                        os.remove(each_attached_file_path)
                if activities:
                    # Calculate carbon footprint
                    from services.carbon_service import CarbonCalculator
                    calculator = CarbonCalculator()
                    results = calculator.calculate_carbon_footprint(activities)
                    
                    # Update session state
                    st.session_state.carbon_data = results
                else:
                    st.warning("No activities were detected in your input. Please try again with more specific details.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Results section
    if st.session_state.carbon_data:
        display_results()

def main():
    # Set dark theme by default
    st.markdown("""
        <style>
            /* Force dark theme */
            .stApp {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            /* Override Streamlit's default light theme */
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea,
            .stSelectbox > div > div > div,
            .stRadio > div > div > label,
            .stButton > button {
                background-color: #2D2D2D;
                color: #000000 !important;  /* Force dark text color */
                border-color: #3D3D3D;
            }
            /* Ensure text is visible in input fields */
            .stTextInput > div > div > input::placeholder,
            .stTextArea > div > div > textarea::placeholder {
                color: #666666 !important;
            }
            .stTextInput > div > div > input:focus,
            .stTextArea > div > div > textarea:focus {
                color: #000000 !important;
            }
            /* Button styling */
            .stButton > button {
                background-color: #FFFFFF !important;
                color: #000000 !important;
                border: 1px solid #3D3D3D !important;
            }
            .stButton > button:hover {
                background-color: #F0F0F0 !important;
                color: #000000 !important;
            }
            /* Custom dark theme styles */
            .text-color {
                color: #FFFFFF;
            }
            .card-background {
                background: rgba(45, 45, 45, 0.8);
            }
            .background-color {
                background: rgba(30, 30, 30, 0.9);
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Add padding to prevent content from being hidden behind the fixed button
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    if st.session_state.page == 'welcome':
        welcome_page()
    else:
        main_page()
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_results():
    st.markdown("""
        <style>
            .header-text {
                color: #FFFFFF;
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 1rem;
            }
            .metric-text {
                color: #FFFFFF;
                font-size: 1.5rem;
                font-weight: bold;
            }
            .carbon-number {
                color: #FFFFFF;
                font-size: 3.5rem;
                font-weight: 900;
                text-align: center;
                margin: 1rem 0;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            .carbon-label {
                color: #FFFFFF;
                font-size: 1.2rem;
                font-weight: bold;
                text-align: center;
                margin-bottom: 0.5rem;
            }
            .section-title {
                color: #FFFFFF;
                font-size: 2rem;
                font-weight: 700;
                text-align: center;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 3px solid #90CAF9;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            }
            .card-header {
                color: #FFFFFF;
                font-size: 1.4rem;
                font-weight: 700;
                margin-bottom: 1.5rem;
                padding-bottom: 0.8rem;
                border-bottom: 2px solid #90CAF9;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .content-label {
                color: #FFFFFF;
                font-size: 0.9rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 0.3rem;
            }
            .content-value {
                color: #FFFFFF;
                font-size: 1.1rem;
                font-weight: 500;
                margin-bottom: 1rem;
                padding: 0.8rem;
                background: rgba(45, 45, 45, 0.8);
                border-radius: 8px;
                border-left: 3px solid #1976D2;
            }
            .suggestion-text {
                color: #FFFFFF;
                font-size: 1.1rem;
                line-height: 1.5;
            }
            .suggestion-box {
                background: rgba(45, 45, 45, 0.8);
                padding: 1.2rem;
                border-radius: 12px;
                margin-top: 1rem;
                border-left: 4px solid #1976D2;
                position: relative;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            }
            .graph-title {
                color: #FFFFFF;
                font-size: 1.5rem;
                font-weight: bold;
                text-align: center;
                margin-bottom: 1rem;
            }
            .confetti {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 9999;
            }
            .confetti-piece {
                position: absolute;
                width: 10px;
                height: 10px;
                background-color: #f00;
                opacity: 0;
            }
            @keyframes confetti-fall {
                0% {
                    transform: translateY(-100vh) rotate(0deg);
                    opacity: 1;
                }
                100% {
                    transform: translateY(100vh) rotate(360deg);
                    opacity: 0;
                }
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="header-text">Your Carbon Footprint Analysis</div>', unsafe_allow_html=True)
    
    # Total CO2e
    total_co2 = sum(item['co2e'] for item in st.session_state.carbon_data)
    
    # Add congratulatory message if carbon emission is 0
    if abs(total_co2) < 0.1:  # Using a small epsilon to account for floating point precision
        st.markdown("""
            <div id="congrats-message" style="
                position: fixed;
                top: 60px;
                left: 0;
                right: 0;
                background: rgba(46, 125, 50, 0.9);
                color: white;
                padding: 1rem;
                text-align: center;
                z-index: 1000;
                opacity: 1;
                transition: opacity 0.5s ease-out;
            ">
                <span style="font-size: 1.2rem;">🎉 Congratulations! Your activities have no carbon emission. Thanks for Saving our world and being a good example!!!</span>
            </div>
            <script>
                // Auto-close after 5 seconds
                setTimeout(function() {
                    var element = document.getElementById('congrats-message');
                    element.style.opacity = '0';
                    setTimeout(function() {
                        element.style.display = 'none';
                    }, 500);
                }, 5000);
            </script>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="carbon-label">Total Carbon Footprint</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="carbon-number">{total_co2:.2f} kg CO₂e</div>', unsafe_allow_html=True)
    
    # Riskometer
    # Calculate risk level and fill percentage with exponential scaling
    max_co2 = 24  # Maximum CO2 for 100% fill
    base = 2  # Exponential base for more dramatic scaling
    
    # Calculate exponential fill percentage
    if total_co2 <= 0:
        fill_percentage = 0
    else:
        # Exponential scaling: percentage = (base^(x/max) - 1) * 100
        fill_percentage = min((pow(base, total_co2/max_co2) - 1) * 100, 100)
    
    # Determine risk level and color
    if total_co2 > 16:
        risk_level = "HIGH"
        risk_color = "#F44336"  # Red
    elif total_co2 > 8:
        risk_level = "MEDIUM"
        risk_color = "#FFC107"  # Yellow
    else:
        risk_level = "LOW"
        risk_color = "#4CAF50"  # Green
    
    st.markdown("""
        <style>
            .riskometer-container {
                width: 100%;
                margin: 2rem 0;
                padding: 1rem;
                background: rgba(45, 45, 45, 0.8);
                border-radius: 15px;
            }
            .riskometer-title {
                color: #FFFFFF;
                font-size: 1.2rem;
                text-align: center;
                margin-bottom: 1rem;
            }
            .riskometer-bar-container {
                width: 100%;
                height: 30px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                position: relative;
                overflow: hidden;
            }
            .riskometer-fill {
                height: 100%;
                border-radius: 15px;
                transition: width 1s ease-in-out;
            }
            .riskometer-marker {
                position: absolute;
                top: 0;
                height: 100%;
                width: 2px;
                background: #FFFFFF;
                box-shadow: 0 0 5px rgba(255, 255, 255, 0.8);
            }
            .riskometer-arrow {
                position: absolute;
                top: -20px;
                width: 0;
                height: 0;
                border-left: 10px solid transparent;
                border-right: 10px solid transparent;
                border-bottom: 20px solid #FFFFFF;
                transition: left 1s ease-in-out;
            }
            .riskometer-labels {
                display: flex;
                justify-content: space-between;
                margin-top: 0.5rem;
                color: #FFFFFF;
                font-size: 1rem;
            }
            .riskometer-level {
                color: #FFFFFF;
                font-size: 1.2rem;
                text-align: center;
                margin-top: 1rem;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Calculate arrow position based on fill percentage
    arrow_position = fill_percentage
    
    st.markdown(f"""
        <div class="riskometer-container">
            <div class="riskometer-title">Environmental Impact Level</div>
            <div class="riskometer-bar-container">
                <div class="riskometer-fill" style="width: {fill_percentage}%; background: {risk_color};"></div>
                <div class="riskometer-marker" style="left: 33%;"></div>
                <div class="riskometer-marker" style="left: 66%;"></div>
                <div class="riskometer-arrow" style="left: {arrow_position}%;"></div>
            </div>
            <div class="riskometer-labels">
                <span>Low</span>
                <span>Medium</span>
                <span>High</span>
            </div>
            <div class="riskometer-level" style="color: {risk_color};">Current Level: {risk_level}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Category breakdown - Modified to fix the FutureWarning
    df = pd.DataFrame(st.session_state.carbon_data)
    fig = px.pie(
        df,
        values='co2e',
        names='category',
        title='',
        color_discrete_map={
            'Food': '#FF9999',
            'Transport': '#66B2FF',
            'Energy': '#99FF99',
            'Shopping': '#FFCC99'
        }
    ).update_traces(
        textinfo='percent+label',
        textfont=dict(color='#FFFFFF')
    )
    
    # Update layout for transparent background
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='#FFFFFF')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            color='#FFFFFF'  # Changed to white for better visibility
        )
    )
    total_co2 = sum(item['co2e'] for item in st.session_state.carbon_data)
    
    # Create metrics row (keep existing code)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Carbon Footprint", f"{total_co2:.2f} kg CO₂e")
    with col2:
        st.metric("Daily Average", f"{total_co2/1:.2f} kg CO₂e/day")
    with col3:
        global_average = 12
        percentage_diff = ((total_co2 - global_average) / global_average) * 100
        st.metric("Compared to Global Average", 
                 f"{total_co2:.2f} kg CO₂e",
                 f"{percentage_diff:+.1f}%",
                 delta_color="inverse")

    # Create two columns for charts
    col1, col2 = st.columns(2)

    # Pie Chart with conditional display
    with col1:
        st.subheader("Distribution by Category")
        if total_co2 > 0:
            # Regular pie chart for non-zero emissions
            df = pd.DataFrame(st.session_state.carbon_data)
            fig_pie = px.pie(
                df,
                values='co2e',
                names='category',
                title='Carbon Footprint Distribution',
                color='category',
                color_discrete_map={
                    'Food': '#FF9999',
                    'Transport': '#66B2FF',
                    'Energy': '#99FF99',
                    'Shopping': '#FFCC99'
                }
            )
        else:
            # Zero emission pie chart (all green)
            fig_pie = px.pie(
                values=[1],  # Single value for full circle
                names=['Zero Emission'],
                title='Carbon Footprint Distribution',
                color_discrete_sequence=['#4CAF50']  # Green color
            )
            
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
            plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot area
            # annotations=[
            #     dict(
            #         text="Zero Carbon Emission!" if total_co2 == 0 else "",
            #         x=0.5,
            #         y=0.5,
            #         font_size=16,
            #         font_color='#1B5E20',
            #         showarrow=False,
            #         font_family="Arial"
            #     )
            # ]
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})  # Hide the mode bar for cleaner look

    # Bar Chart (keep existing code)
    with col2:
        st.subheader("Emissions by Activity")
        if total_co2 > 0:
            df = pd.DataFrame(st.session_state.carbon_data)
            fig_bar = px.bar(
                df,
                x='co2e',
                y='text',
                orientation='h',
                color='category',
                color_discrete_map={
                    'Food': '#FF9999',
                    'Transport': '#66B2FF',
                    'Energy': '#99FF99',
                    'Shopping': '#FFCC99'
                },
                title='Emissions by Individual Activity'
            )
            fig_bar.update_layout(
                xaxis_title="CO₂e (kg)",
                yaxis_title="Activity",
                showlegend=True,
                legend_title="Category",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.5,
                    xanchor="center",
                    x=0.5
                ),
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
                plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot area
            )
            fig_bar.update_traces(texttemplate='%{x:.1f} kg', textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            # Display a message for zero emissions
            st.markdown(
                """
                <div style='text-align: center; padding: 20px; color: 'black'; background: #E8F5E9; border-radius: 10px;'>
                    <h3>No Emissions Recorded!</h3>
                    <p>Great job maintaining zero carbon emissions!</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    # st.markdown('<div class="graph-title" style="text-align: left;">Carbon Footprint by Category</div>', unsafe_allow_html=True)
    # st.plotly_chart(fig, use_container_width=True)
    
    # Enhanced styling with better contrast and more lively colors
    st.markdown("""
        <style>
        /* Modern Vibrant Color Palette */
        :root {
            --primary-green: #2E7D32;
            --primary-teal: #00796B;
            --primary-blue: #1976D2;
            --primary-purple: #6A1B9A;
            --accent-orange: #F57C00;
            --accent-pink: #C2185B;
        }

        /* Section Styling */
        .section-container {
            background: rgba(45, 45, 45, 0.8);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            position: relative;
            z-index: 1;
            transform: translateY(-10px);
            transition: all 0.3s ease;
        }

        .section-container:hover {
            transform: translateY(-15px);
            box-shadow: 0 12px 25px rgba(0, 0, 0, 0.2);
        }

        /* Card Styling - More Lively Colors */
        .flash-card {
            padding: 1.8rem;
            margin-bottom: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            background: rgba(45, 45, 45, 0.8);
        }

        .flash-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 25px rgba(0, 0, 0, 0.12);
        }

        /* Activity Card Variations */
        .activity-card-1 { background: rgba(45, 45, 45, 0.8); }
        .activity-card-2 { background: rgba(45, 45, 45, 0.8); }
        .activity-card-3 { background: rgba(45, 45, 45, 0.8); }
        .activity-card-4 { background: rgba(45, 45, 45, 0.8); }

        /* Insight Card Variations */
        .insight-card-1 { background: rgba(45, 45, 45, 0.8); }
        .insight-card-2 { background: rgba(45, 45, 45, 0.8); }
        .insight-card-3 { background: rgba(45, 45, 45, 0.8); }
        .insight-card-4 { background: rgba(45, 45, 45, 0.8); }

        /* Impact Badge Styling - More Vibrant */
        .impact-badge {
            padding: 0.6rem 1.2rem;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
            margin: 0.5rem 0;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.9rem;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        .impact-very-high {
            background: #FF5252;
            color: #FFFFFF;
        }

        .impact-high {
            background: #FF7043;
            color: #FFFFFF;
        }

        .impact-medium {
            background: #FFA726;
            color: #FFFFFF;
        }

        .impact-low {
            background: #66BB6A;
            color: #FFFFFF;
        }

        /* Divider Styling */
        .activity-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, #90CAF9, transparent);
            margin: 2rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Section Container
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🌱 Activity Impact Analysis</div>', unsafe_allow_html=True)
    
    # Create flash cards for each activity
    for idx, activity in enumerate(st.session_state.carbon_data):
        cols = st.columns(2)
        
        # Map impact levels
        impact_level = str(activity.get('co2e_impact_level', '')).lower()
        impact_mapping = {
            '1': 'LOW',
            '2': 'MEDIUM',
            '3': 'HIGH',
            '4': 'VERY HIGH',
            'low': 'LOW',
            'medium': 'MEDIUM',
            'high': 'HIGH',
            'very high': 'VERY HIGH',
            'very_high': 'VERY HIGH'
        }
        display_impact = impact_mapping.get(impact_level, 'LOW')
        
        # Activity Details Card
        with cols[0]:
            card_variation = (idx % 4) + 1
            st.markdown(f'<div class="flash-card activity-card-{card_variation}">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📊 Activity Details</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="content-label">Activity</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="content-value">{activity["text"]}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="content-label">Category</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="content-value">{activity["category"]}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="content-label">Quantity</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="content-value">{activity["quantity"]} {activity.get("unit", "")}</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="content-label">CO₂e Impact</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="content-value">{activity["co2e"]:.2f} kg</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Sustainability Insight Card
        with cols[1]:
            st.markdown(f'<div class="flash-card insight-card-{card_variation}">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">💡 Sustainability Insight</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="content-label">Impact Level</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="impact-badge impact-{display_impact.lower().replace(" ", "-")}">{display_impact}</div>', 
                      unsafe_allow_html=True)
            
            st.markdown('<div class="content-label">Suggestion</div>', unsafe_allow_html=True)
            suggestion = activity.get('suggestion', 'Consider more sustainable alternatives for this activity.')
            st.markdown(f'<div class="suggestion-box"><div class="suggestion-text">{suggestion}</div></div>', 
                      unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Add divider between activities (except for the last one)
        if idx < len(st.session_state.carbon_data) - 1:
            st.markdown('<div class="activity-divider"></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Impact comparison with colorful flash cards
    st.markdown("""
        <style>
            @keyframes slideIn {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            @keyframes float {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-5px); }
                100% { transform: translateY(0px); }
            }
            .impact-container {
                display: flex;
                justify-content: space-between;
                gap: 2rem;
                padding: 2rem;
                margin: 2rem 0;
            }
            .impact-card {
                flex: 1;
                border-radius: 15px;
                padding: 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                animation: slideIn 0.5s ease-out;
                transition: all 0.3s ease;
                min-width: 250px;
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
            }
            .impact-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            }
            .impact-icon {
                font-size: 2.5rem;
                margin-bottom: 1.5rem;
                animation: float 3s ease-in-out infinite;
            }
            .impact-title {
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 1rem;
                color: #FFFFFF;
            }
            .impact-value {
                font-size: 2.5rem;
                font-weight: bold;
                margin: 1.5rem 0;
                color: #FFFFFF;
            }
            .impact-description {
                font-size: 1.2rem;
                color: rgba(255, 255, 255, 0.9);
                margin-top: 1.5rem;
            }
            .impact-card-1 {
                background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
            }
            .impact-card-2 {
                background: linear-gradient(135deg, #4ECDC4 0%, #6EE7E7 100%);
            }
            .impact-card-3 {
                background: linear-gradient(135deg, #45B7D1 0%, #7AD7F0 100%);
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.header("🌍 Impact Comparison")
    st.markdown('<div class="impact-container">', unsafe_allow_html=True)
    
    # Smartphones card
    st.markdown(f"""
        <div class="impact-card impact-card-1">
            <div class="impact-icon">📱</div>
            <div class="impact-title">Smartphones</div>
            <div class="impact-value">{(total_co2 * 1000 / 404):.1f}</div>
            <div class="impact-description">Equivalent to manufacturing this many smartphones (404 kg CO₂e each)</div>
        </div>
    """, unsafe_allow_html=True)
    
    # T-shirts card
    st.markdown(f"""
        <div class="impact-card impact-card-2">
            <div class="impact-icon">👕</div>
            <div class="impact-title">T-shirts</div>
            <div class="impact-value">{(total_co2 * 1000 / 190):.1f}</div>
            <div class="impact-description">Equivalent to manufacturing this many t-shirts (190 kg CO₂e each)</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Car kilometers card
    st.markdown(f"""
        <div class="impact-card impact-card-3">
            <div class="impact-icon">🚗</div>
            <div class="impact-title">Car Kilometers</div>
            <div class="impact-value">{(total_co2 * 1000 / 200):.1f}</div>
            <div class="impact-description">Equivalent to driving this many kilometers (200g CO₂e per km)</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Detailed Explanation Section
    st.markdown("""
        <style>
            .summary-section {
                margin-top: 2rem;
                background: rgba(45, 45, 45, 0.9);
                padding: 2rem;
                border-radius: 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            }
            .summary-title {
                font-size: 1.8rem;
                font-weight: bold;
                margin-bottom: 1rem;
                color: #E8F5E9;
            }
            .summary-text {
                font-size: 1.1rem;
                line-height: 1.6;
                color: #FFFFFF;
            }
        </style>
        <div class="summary-section">
            <div class="summary-title">📘 What Do These Equivalents Mean?</div>
            <div class="summary-text">
                To help you understand the real-world impact of your carbon footprint, we've translated your total emissions into familiar items:
                <br><br>
                <strong>📱 Smartphones:</strong> The carbon cost of producing a single smartphone is roughly <code>404 kg CO₂e</code>. By comparing your activities to this, you can gauge the hidden emissions behind everyday tech.
                <br><br>
                <strong>👕 T-Shirts:</strong> Manufacturing a cotton t-shirt can emit about <code>190 kg CO₂e</code>, factoring in water usage, transport, and production. This comparison helps you reflect on clothing consumption's hidden footprint.
                <br><br>
                <strong>🚗 Car Kilometers:</strong> Driving a standard car emits around <code>200 g CO₂e per km</code>. This helps visualize how far you'd need to drive to equal your daily impact — great for translating emissions into tangible distance.
                <br><br>
                These equivalents help make abstract numbers like "12.34 kg CO₂e" more relatable. By tying emissions to real-world objects, you can better understand the scale of your actions and discover which habits might be worth adjusting for a greener lifestyle.
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    def generate_dynamic_summary(co2: float) -> str:
        global_average = 12
        smartphones = co2 * 1000 / 404
        tshirts = co2 * 1000 / 190
        car_km = co2 * 1000 / 200
        percent_diff = ((co2 - global_average) / global_average) * 100

        if co2 < 4:
            behavior_tag = "EXCELLENT 🌟"
            tone = "👏 You're far below the global average! Your lifestyle is highly sustainable."
            bg_gradient = "linear-gradient(135deg, #43cea2, #185a9d)"
        elif co2 < 10:
            behavior_tag = "GOOD 🌿"
            tone = "👍 You're doing well! A few mindful changes can make your impact even greener."
            bg_gradient = "linear-gradient(135deg, #8BC34A, #558B2F)"
        elif co2 < 16:
            behavior_tag = "CONCERNING ⚠️"
            tone = "⚠️ You're above the average. It's a good time to explore greener alternatives."
            bg_gradient = "linear-gradient(135deg, #FFC107, #FF9800)"
        else:
            behavior_tag = "CRITICAL 🚨"
            tone = "🚨 Your carbon footprint is quite high. Small consistent changes can help reverse this trend."
            bg_gradient = "linear-gradient(135deg, #EF5350, #B71C1C)"

        return f"""
        <style>
            .summary-box {{
                background: {bg_gradient};
                color: white;
                padding: 2rem;
                border-radius: 20px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                font-family: 'Segoe UI', sans-serif;
                animation: fadeIn 1s ease-in-out;
            }}
            .summary-header {{
                display: flex;
                align-items: center;
                gap: 0.8rem;
                font-size: 1.8rem;
                font-weight: bold;
                margin-bottom: 0.8rem;
            }}
            .summary-tone {{
                font-size: 1.2rem;
                margin-bottom: 2rem;
            }}
            .summary-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1.5rem;
                margin-bottom: 2rem;
            }}
            .summary-card {{
                background: rgba(255, 255, 255, 0.1);
                padding: 1rem 1.5rem;
                border-radius: 12px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            }}
            .summary-card h4 {{
                margin: 0;
                font-size: 1.1rem;
                font-weight: bold;
            }}
            .summary-card p {{
                margin: 0.3rem 0 0;
                font-size: 1rem;
            }}
            .impact-badge {{
                background-color: rgba(255, 255, 255, 0.2);
                padding: 0.5rem 1.2rem;
                border-radius: 20px;
                display: inline-block;
                font-weight: bold;
                font-size: 1rem;
                box-shadow: inset 0 0 5px rgba(255,255,255,0.3);
                text-align: center;
            }}
            .impact-footer {{
                text-align: right;
                font-size: 1.1rem;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
        </style>

        <div class="summary-box">
            <div class="summary-header">🧠 Personalized Sustainability Reflection</div>
            <div class="summary-tone">{tone}</div>

            <div class="summary-grid">
                <div class="summary-card">
                    <h4>🌍 Daily CO₂ Emissions</h4>
                    <p>{co2:.2f} kg</p>
                </div>
                <div class="summary-card">
                    <h4>📊 Compared to Global Avg</h4>
                    <p>{percent_diff:+.1f}%</p>
                </div>
                <div class="summary-card">
                    <h4>📱 Smartphones Produced</h4>
                    <p>{smartphones:.1f}</p>
                </div>
                <div class="summary-card">
                    <h4>👕 T-Shirts Manufactured</h4>
                    <p>{tshirts:.1f}</p>
                </div>
                <div class="summary-card">
                    <h4>🚗 Car Kilometers</h4>
                    <p>{car_km:.1f} km</p>
                </div>
            </div>

            <div class="impact-footer">
                Your current status: <span class="impact-badge">{behavior_tag}</span>
            </div>
        </div>
        """

    components.html(generate_dynamic_summary(total_co2), height=550)


    st.markdown("</div>", unsafe_allow_html=True)

    # Assign CO2 values using real-time user data
    current_co2 = total_co2
    projected_co2_current = current_co2 * 365
    projected_co2_suggested = projected_co2_current * 0.7  # Assume 30% reduction

    # Keep this right above the new components.html block
    smartphone_kg = 404
    tshirt_kg = 190
    car_g_per_km = 200

    # Place this near the end of display_results()
    components.html(f"""
    <style>
    .card-grid {{
        display: flex;
        justify-content: space-between;
        gap: 2rem;
        flex-wrap: wrap;
        margin-top: 3rem;
    }}
    .card-column {{
        flex: 1;
        min-width: 250px;
    }}
    .card {{
        background: #2D2D2D;
        color: red;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        animation: fadeIn 0.5s ease-in-out;
    }}
    .card h4 {{
        margin: 0;
        font-size: 1.1rem;
        color: #90CAF9;
    }}
    .card p {{
        font-size: 1.6rem;
        font-weight: bold;
        font-family: 'Segoe UI', sans-serif;
        margin-top: 0.3rem;
    }}
    .column-title {{
        font-size: 1.4rem;
        color: black;
        margin-bottom: 1rem;
        font-weight: bold;
        text-align: center;
        border-bottom: 2px solid #90CAF9;
        padding-bottom: 0.5rem;
    }}
    </style>

    <div class="card-grid">
        <div class="card-column">
            <div class="column-title">📊 Current Snapshot</div>
            <div class="card"><h4>🌍 Daily CO₂ Emissions</h4><p>{current_co2:.2f} kg</p></div>
            <div class="card"><h4>📊 Compared to Global Avg</h4><p>-37.3%</p></div>
            <div class="card"><h4>📱 Smartphones Produced</h4><p>{(current_co2 * 1000 / smartphone_kg):.1f}</p></div>
            <div class="card"><h4>👕 T-Shirts Manufactured</h4><p>{(current_co2 * 1000 / tshirt_kg):.1f}</p></div>
            <div class="card"><h4>🚗 Car Kilometers</h4><p>{(current_co2 * 1000 / car_g_per_km):.1f} km</p></div>
        </div>

        <div class="card-column">
            <div class="column-title">📈 Projected if Current Continues</div>
            <div class="card"><h4>🌍 CO₂ (Annual)</h4><p>{projected_co2_current:.2f} kg</p></div>
            <div class="card"><h4>📊 Compared to Global Avg</h4><p>-37.3%</p></div>
            <div class="card"><h4>📱 Smartphones Produced</h4><p>{(projected_co2_current * 1000 / smartphone_kg):.1f}</p></div>
            <div class="card"><h4>👕 T-Shirts Manufactured</h4><p>{(projected_co2_current * 1000 / tshirt_kg):.1f}</p></div>
            <div class="card"><h4>🚗 Car Kilometers</h4><p>{(projected_co2_current * 1000 / car_g_per_km):.1f} km</p></div>
        </div>

        <div class="card-column">
            <div class="column-title">🌿 Projected with Green Suggestions</div>
            <div class="card"><h4>🌍 CO₂ (Annual)</h4><p>{projected_co2_suggested:.2f} kg</p></div>
            <div class="card"><h4>📊 Compared to Global Avg</h4><p>-60.0%</p></div>
            <div class="card"><h4>📱 Smartphones Produced</h4><p>{(projected_co2_suggested * 1000 / smartphone_kg):.1f}</p></div>
            <div class="card"><h4>👕 T-Shirts Manufactured</h4><p>{(projected_co2_suggested * 1000 / tshirt_kg):.1f}</p></div>
            <div class="card"><h4>🚗 Car Kilometers</h4><p>{(projected_co2_suggested * 1000 / car_g_per_km):.1f} km</p></div>
        </div>
    </div>
    """, height=900)





if __name__ == "__main__":
    main() 