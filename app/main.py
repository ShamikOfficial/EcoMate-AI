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
print(API_KEY)
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
                    "type": {"type": "string"},
                    "activity": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit": {"type": "string"},
                    "co2e_per_unit": {"type": "number"}
                },
                "required": ["category", "activity", "type", "unit", "quantity", "co2e_per_unit"]
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
                name = st.text_input("", placeholder="Enter your name", key="name_input", label_visibility="collapsed")
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
        "",
        ["Upload Receipt", "Text Input", "Audio Input"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if input_method == "Upload Receipt":
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown('<div class="upload-icon">📄</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #1B5E20; font-size: 1.1rem;">Upload your receipt to analyze your purchases</p>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "",
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
            "",
            placeholder="e.g., 'Had beef burger for lunch, took Uber to work, ran AC for 5 hours'",
            height=150,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:  # Audio Input
        st.markdown('<div class="audio-section">', unsafe_allow_html=True)
        st.markdown('<div class="audio-icon">🎤</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #1B5E20; font-size: 1.1rem; margin-bottom: 1rem;">Record your daily activities</p>', unsafe_allow_html=True)
        audio_file = st.file_uploader(
            "",
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
    
    # Total CO2e with enhanced styling
    total_co2 = sum(item['co2e'] for item in st.session_state.carbon_data)
    
    st.markdown("""
        <style>
            .total-footprint-container {
                background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
                border-radius: 20px;
                padding: 2rem;
                margin: 2rem 0;
                text-align: center;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.1);
                animation: pulse 2s infinite;
            }
            .total-footprint-title {
                font-size: 1.8rem;
                color: #E8F5E9;
                margin-bottom: 1rem;
                font-weight: 600;
            }
            .total-footprint-value {
                font-size: 4rem;
                font-weight: 800;
                color: #FFFFFF;
                margin: 1rem 0;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            .total-footprint-unit {
                font-size: 1.5rem;
                color: #E8F5E9;
                margin-top: 0.5rem;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.02); }
                100% { transform: scale(1); }
            }
            .eco-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
                animation: float 3s ease-in-out infinite;
            }
            @keyframes float {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
                100% { transform: translateY(0px); }
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="total-footprint-container">
            <div class="eco-icon">🌱</div>
            <div class="total-footprint-title">Your Total Carbon Footprint</div>
            <div class="total-footprint-value">{total_co2:.2f}</div>
            <div class="total-footprint-unit">kg CO₂e</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Category breakdown
    df = pd.DataFrame(st.session_state.carbon_data)
    
    # Create two columns for the charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        fig_pie = px.pie(
            df,
            values='co2e',
            names='category',
            title='Carbon Footprint by Category',
            color='category',
            color_discrete_map={
                'Food': '#FF6B6B',      # Bright coral
                'Transport': '#4ECDC4',  # Bright turquoise
                'Energy': '#45B7D1',     # Bright blue
                'Shopping': '#96CEB4'    # Soft green
            }
        )
        
        # Update layout for better aesthetics
        fig_pie.update_layout(
            title={
                'text': "Carbon Footprint by Category",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    'size': 24,
                    'family': "Arial, sans-serif",
                    'color': '#FFFFFF'
                }
            },
            font={
                'size': 16,
                'family': "Arial, sans-serif",
                'color': '#FFFFFF'
            },
            legend={
                'title': {
                    'text': 'Categories',
                    'font': {
                        'size': 20,
                        'family': "Arial, sans-serif",
                        'color': '#FFFFFF'
                    }
                },
                'font': {
                    'size': 16,
                    'family': "Arial, sans-serif"
                },
                'orientation': 'h',
                'yanchor': "bottom",
                'y': -0.2,
                'xanchor': "center",
                'x': 0.5
            },
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=100, b=100, l=50, r=50),
            height=600,
            showlegend=False  # Hide legend since we're using labels
        )
        
        # Update traces for better visibility
        fig_pie.update_traces(
            textposition='outside',
            textinfo='percent+label',
            textfont={
                'size': 20,
                'family': "Arial, sans-serif",
                'color': '#FFFFFF'
            },
            hovertemplate='<b>%{label}</b><br>CO₂e: <span style="font-size: 20px;">%{value:.2f} kg</span><br>Percentage: <span style="font-size: 20px;">%{percent:.1%}</span><extra></extra>',
            marker=dict(
                line=dict(color='#ffffff', width=2),
                colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            ),
            pull=[0.1, 0, 0, 0],
            rotation=45
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar chart
        fig_bar = px.bar(
            df,
            x='co2e',
            y='category',
            orientation='h',
            title='Carbon Footprint Comparison',
            color='category',
            color_discrete_map={
                'Food': '#FF6B6B',      # Bright coral
                'Transport': '#4ECDC4',  # Bright turquoise
                'Energy': '#45B7D1',     # Bright blue
                'Shopping': '#96CEB4'    # Soft green
            }
        )
        
        # Update layout for better aesthetics
        fig_bar.update_layout(
            title={
                'text': "Carbon Footprint Comparison",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    'size': 24,
                    'family': "Arial, sans-serif",
                    'color': '#FFFFFF'
                }
            },
            font={
                'size': 16,
                'family': "Arial, sans-serif",
                'color': '#FFFFFF'
            },
            xaxis_title="CO₂e (kg)",
            yaxis_title="Category",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=100, b=100, l=50, r=50),
            height=600,
            showlegend=False
        )
        
        # Update traces for better visibility
        fig_bar.update_traces(
            hovertemplate='<b>%{y}</b><br>CO₂e: <span style="font-size: 20px;">%{x:.2f} kg</span><extra></extra>',
            marker=dict(
                line=dict(color='#ffffff', width=2)
            ),
            textfont=dict(size=20),
            textposition='auto'
        )
        
        # Update axes
        fig_bar.update_xaxes(
            gridcolor='rgba(255, 255, 255, 0.1)',
            zerolinecolor='rgba(255, 255, 255, 0.1)'
        )
        fig_bar.update_yaxes(
            gridcolor='rgba(255, 255, 255, 0.1)',
            zerolinecolor='rgba(255, 255, 255, 0.1)'
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Detailed breakdown with themed cards
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
            .breakdown-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2.5rem;
                padding: 2rem;
                margin: 1rem 0;
            }
            .breakdown-card {
                border-radius: 15px;
                padding: 2rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                animation: slideIn 0.5s ease-out;
                transition: all 0.3s ease;
                height: 100%;
                display: flex;
                flex-direction: column;
                margin: 0.5rem 0;
            }
            .breakdown-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            }
            .breakdown-icon {
                font-size: 2rem;
                margin-bottom: 1.5rem;
                animation: float 3s ease-in-out infinite;
            }
            .breakdown-content {
                font-size: 1.1rem;
                line-height: 1.6;
                flex-grow: 1;
                margin-top: 0.5rem;
            }
            .breakdown-header {
                font-size: 1.3rem;
                font-weight: bold;
                margin-bottom: 1rem;
            }
            .breakdown-metric {
                font-size: 1.8rem;
                font-weight: bold;
                margin-top: 1.5rem;
                padding: 1rem;
                border-radius: 8px;
                text-align: center;
            }
            .high-impact {
                background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
                border-left: 5px solid #D32F2F;
                color: #B71C1C;
            }
            .medium-impact {
                background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
                border-left: 5px solid #F57C00;
                color: #E65100;
            }
            .low-impact {
                background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
                border-left: 5px solid #388E3C;
                color: #1B5E20;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.header("📊 Detailed Breakdown")
    st.markdown('<div class="breakdown-container">', unsafe_allow_html=True)
    
    for item in st.session_state.carbon_data:
        # Determine impact level based on CO2e
        co2e = item['co2e']
        if co2e > 5:  # High impact
            impact_class = "high-impact"
            icon = "⚠️"
        elif co2e > 2:  # Medium impact
            impact_class = "medium-impact"
            icon = "ℹ️"
        else:  # Low impact
            impact_class = "low-impact"
            icon = "✅"
        
        st.markdown(f"""
            <div class="breakdown-card {impact_class}">
                <div class="breakdown-icon">{icon}</div>
                <div class="breakdown-header">{item['text']}</div>
                <div class="breakdown-content">
                    <div><strong>Category:</strong> {item['category']}</div>
                    <div><strong>Quantity:</strong> {item['quantity']} {item.get('unit', 'item')}</div>
                </div>
                <div class="breakdown-metric">
                    CO₂e: {item['co2e']:.2f} kg
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Suggestions with individual flash cards
    if st.session_state.suggestions:
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
                .suggestions-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 3.5rem;  /* Increased gap between cards */
                    padding: 2.5rem;  /* Increased padding around container */
                    margin: 2rem 0;  /* Added margin around container */
                }
                .suggestion-card {
                    background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
                    border-radius: 15px;
                    padding: 2.5rem;  /* Increased padding inside cards */
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    border-left: 5px solid #1B5E20;
                    animation: slideIn 0.5s ease-out;
                    transition: all 0.3s ease;
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                    margin: 0.5rem 0;
                }
                .suggestion-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
                }
                .suggestion-icon {
                    font-size: 2.5rem;  /* Increased icon size */
                    margin-bottom: 2rem;  /* Increased margin below icon */
                    color: #1B5E20;
                    animation: float 3s ease-in-out infinite;
                }
                .suggestion-content {
                    color: #1B5E20;
                    font-size: 1.1rem;
                    line-height: 1.8;  /* Increased line height */
                    flex-grow: 1;
                    margin-top: 1rem;  /* Added margin above content */
                }
                .suggestion-header {
                    font-size: 1.4rem;  /* Increased header size */
                    font-weight: bold;
                    margin-bottom: 1.5rem;  /* Increased margin below header */
                    color: #1B5E20;
                }
            </style>
        """, unsafe_allow_html=True)
        
        st.header("🌿 Sustainability Suggestions")
        st.markdown('<div class="suggestions-container">', unsafe_allow_html=True)
        
        for i, suggestion in enumerate(st.session_state.suggestions):
            icon = "💡" if i % 3 == 0 else "🌱" if i % 3 == 1 else "♻️"
            header = "Smart Tip" if i % 3 == 0 else "Green Living" if i % 3 == 1 else "Eco Action"
            
            st.markdown(f"""
                <div class="suggestion-card">
                    <div class="suggestion-icon">{icon}</div>
                    <div class="suggestion-header">{header}</div>
                    <div class="suggestion-content">{suggestion}</div>
                </div>
            """, unsafe_allow_html=True)
        
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