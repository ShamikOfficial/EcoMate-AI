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

def analyze_text(text: str) -> list:
    """Analyze text directly using GenAI model"""
    try:
        result = genai_model.analyze_emissions(
            text=text,
            emission_schema=EMISSION_SCHEMA,
            context_files=[os.path.join("data", "emission_factor.pdf")]
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
        <div class="welcome-section">
            <div class="leaf-decoration leaf-1">🌿</div>
            <div class="leaf-decoration leaf-2">🍃</div>
            <div class="leaf-decoration leaf-3">🌱</div>
            <div class="leaf-decoration leaf-4">🌿</div>
            <div style='text-align: center;'>
                <div class="eco-icon">🌱</div>
                <h1 class="main-title">EcoMate-AI</h1>
                <h2 class="slogan">Small Swaps. Big Impact.</h2>
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
                background-color: #f8f9fa;
                border-radius: 15px;
                padding: 2rem;
                margin: 2rem 0;
            }
            .input-title {
                color: #1B5E20;
                font-size: 1.5rem;
                font-weight: bold;
                margin-bottom: 1.5rem;
                text-align: center;
            }
            .input-description {
                color: #666;
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
                background: white;
                padding: 1rem 2rem;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                cursor: pointer;
            }
            .stRadio > div > label[data-baseweb="radio"] {
                background: #1B5E20;
                color: white;
            }
            .upload-section {
                text-align: center;
                padding: 2rem;
                border: 2px dashed #1B5E20;
                border-radius: 15px;
                margin: 1rem 0;
            }
            .upload-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
                color: #1B5E20;
            }
            .text-input-section {
                padding: 2rem;
                background: white;
                border-radius: 15px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin: 1rem 0;
            }
            .stTextArea > div > div > textarea {
                border: 2px solid #1B5E20;
                border-radius: 10px;
                padding: 1rem;
                font-size: 1.1rem;
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
                background: white;
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
        "Input Method",
        ["Upload Receipt", "Text Input", "Audio Input"],
        horizontal=True
    )
    
    if input_method == "Upload Receipt":
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown('<div class="upload-icon">📄</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #1B5E20; font-size: 1.1rem;">Upload your receipt to analyze your purchases</p>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Receipt Upload",
            type=['png', 'jpg', 'jpeg'],
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Receipt', use_column_width=True)
            # TODO: Process image with OCR
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif input_method == "Text Input":
        st.markdown('<div class="text-input-section">', unsafe_allow_html=True)
        st.markdown('<p style="color: #1B5E20; font-size: 1.1rem; margin-bottom: 1rem;">Describe your daily activities</p>', unsafe_allow_html=True)
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
        st.markdown('<p style="color: #1B5E20; font-size: 1.1rem; margin-bottom: 1rem;">Record your daily activities</p>', unsafe_allow_html=True)
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
            with st.spinner("Analyzing your activities..."):
                # Get activities from backend
                activities = analyze_text(user_input)
                if activities:
                    # Calculate carbon footprint
                    from services.carbon_service import CarbonCalculator
                    calculator = CarbonCalculator()
                    results = calculator.calculate_carbon_footprint(activities)
                    print(results)
                    suggestions = calculator.get_sustainability_suggestions(results)

                    # Update session state
                    st.session_state.carbon_data = results
                    st.session_state.suggestions = suggestions
                else:
                    st.warning("No activities were detected in your input. Please try again with more specific details.")
        elif input_method == "Upload Receipt" and uploaded_file:
            st.info("Receipt analysis coming soon!")
        elif input_method == "Audio Input" and audio_file:
            st.info("Audio analysis coming soon!")
        else:
            st.warning("Please provide input to analyze")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Results section
    if st.session_state.carbon_data:
        display_results()

def main():
    if st.session_state.page == 'welcome':
        welcome_page()
    else:
        main_page()

def display_results():
    st.header("Your Carbon Footprint Analysis")
    
    # Total CO2e
    total_co2 = sum(item['co2e'] for item in st.session_state.carbon_data)
    st.metric("Total Carbon Footprint", f"{total_co2:.2f} kg CO₂e")
    
    # Category breakdown - Modified to fix the FutureWarning
    df = pd.DataFrame(st.session_state.carbon_data)
    fig = px.pie(
        df,
        values='co2e',
        names='category',
        title='Carbon Footprint by Category',
        color_discrete_map={
            'Food': '#FF9999',
            'Transport': '#66B2FF',
            'Energy': '#99FF99',
            'Shopping': '#FFCC99'
        }
    ).update_traces(
        textinfo='percent+label'
    )
    
    # Optional: Add any additional styling to the figure
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
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
            background: #FFFFFF;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }

        .section-title {
            color: var(--primary-green);
            font-size: 2rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid #E8F5E9;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }

        /* Card Styling - More Lively Colors */
        .flash-card {
            padding: 1.8rem;
            margin-bottom: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .flash-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 25px rgba(0, 0, 0, 0.12);
        }

        /* Activity Card Variations */
        .activity-card-1 { background: linear-gradient(135deg, #E3F2FD 0%, #FFFFFF 100%); }
        .activity-card-2 { background: linear-gradient(135deg, #E8F5E9 0%, #FFFFFF 100%); }
        .activity-card-3 { background: linear-gradient(135deg, #F3E5F5 0%, #FFFFFF 100%); }
        .activity-card-4 { background: linear-gradient(135deg, #E0F2F1 0%, #FFFFFF 100%); }

        /* Insight Card Variations */
        .insight-card-1 { background: linear-gradient(135deg, #E8EAF6 0%, #FFFFFF 100%); }
        .insight-card-2 { background: linear-gradient(135deg, #FFF3E0 0%, #FFFFFF 100%); }
        .insight-card-3 { background: linear-gradient(135deg, #FCE4EC 0%, #FFFFFF 100%); }
        .insight-card-4 { background: linear-gradient(135deg, #E0F7FA 0%, #FFFFFF 100%); }

        .card-header {
            color: #1B5E20;
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            padding-bottom: 0.8rem;
            border-bottom: 2px solid rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* Content Styling with Better Contrast */
        .content-label {
            color: #1B5E20;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.3rem;
        }

        .content-value {
            color: #000000;
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 1rem;
            padding: 0.8rem;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            border-left: 3px solid #2E7D32;
        }

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
            color: white;
        }

        .impact-high {
            background: #FF7043;
            color: white;
        }

        .impact-medium {
            background: #FFA726;
            color: white;
        }

        .impact-low {
            background: #66BB6A;
            color: white;
        }

        /* Suggestion Box Styling - Improved Contrast */
        .suggestion-box {
            background: #FFFFFF;
            padding: 1.2rem;
            border-radius: 12px;
            margin-top: 1rem;
            border-left: 4px solid #2E7D32;
            position: relative;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }

        .suggestion-text {
            color: #000000;
            font-size: 1.1rem;
            line-height: 1.5;
        }

        /* Divider Styling */
        .activity-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, #E8F5E9, transparent);
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
        display_impact = impact_mapping.get(impact_level, 'MEDIUM')
        
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
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 