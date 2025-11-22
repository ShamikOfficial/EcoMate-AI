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
        /* Global background and text color fixes */
        .stApp {
            background-color: #1E1E1E !important;
        }
        .main .block-container {
            background-color: #1E1E1E !important;
            padding-top: 2rem;
        }
        /* Ensure form labels are visible */
        .stForm label {
            color: #FFFFFF !important;
        }
        /* Ensure error messages are visible */
        .stAlert {
            color: #FFFFFF !important;
        }
        
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
            border: 2px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
            padding: 1rem 1.5rem !important;
            font-size: 1.2rem !important;
            transition: all 0.3s ease;
            background-color: rgba(45, 45, 45, 0.9) !important;
            color: #FFFFFF !important;
            backdrop-filter: blur(5px);
        }
        .stTextInput > div > div > input:focus {
            border-color: #E8F5E9 !important;
            box-shadow: 0 0 0 3px rgba(232, 245, 233, 0.3) !important;
            background-color: rgba(45, 45, 45, 0.95) !important;
            color: #FFFFFF !important;
        }
        .stTextInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.7) !important;
        }
        .stTextInput > div > div > label {
            font-size: 1.1rem !important;
            color: #E8F5E9 !important;
            font-weight: 500 !important;
        }
        .stButton > button {
            width: 100%;
            margin: 1.5rem auto 0;
            display: block;
            background-color: #E8F5E9 !important;
            color: #1B5E20 !important;
            border: none !important;
            padding: 1rem 2rem !important;
            border-radius: 12px !important;
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            animation: fadeIn 1s ease-out 0.9s;
        }
        .stButton > button:hover {
            background-color: #FFFFFF !important;
            color: #1B5E20 !important;
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
                        background-color: rgba(45, 45, 45, 0.9) !important;
                        border: 2px solid rgba(255, 255, 255, 0.3) !important;
                        border-radius: 12px !important;
                        color: #FFFFFF !important;
                        font-size: 1.2rem !important;
                        text-align: center !important;
                        padding: 1rem !important;
                    }
                    .stTextInput > div > div > input:focus {
                        border-color: #E8F5E9 !important;
                        box-shadow: 0 0 0 2px rgba(232, 245, 233, 0.3) !important;
                        background-color: rgba(45, 45, 45, 0.95) !important;
                        color: #FFFFFF !important;
                    }
                    .stTextInput > div > div > input::placeholder {
                        color: rgba(255, 255, 255, 0.7) !important;
                    }
                    .stTextInput > div > div > label {
                        color: #E8F5E9 !important;
                        font-weight: 500 !important;
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
        <style>
            @keyframes slideUp {{
                from {{ transform: translateY(30px); opacity: 0; }}
                to {{ transform: translateY(0); opacity: 1; }}
            }}
            @keyframes sparkle {{
                0% {{ opacity: 0.5; transform: scale(1); }}
                50% {{ opacity: 1; transform: scale(1.2); }}
                100% {{ opacity: 0.5; transform: scale(1); }}
            }}
            .fun-banner {{
                background: radial-gradient(circle at top left, #81C784, #388E3C);
                padding: 3rem 2rem;
                border-radius: 25px;
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
                margin-bottom: 2.5rem;
                position: relative;
                animation: slideUp 1s ease;
                overflow: hidden;
            }}
            .fun-banner h2 {{
                font-size: 2.8rem;
                font-weight: 900;
                color: #FFFFFF;
                text-align: center;
                margin: 0;
                letter-spacing: 1px;
                text-shadow: 2px 2px 6px rgba(0,0,0,0.3);
                position: relative;
                z-index: 2;
            }}
            .fun-banner p {{
                font-size: 1.5rem;
                color: #F1F8E9;
                text-align: center;
                margin-top: 1rem;
                z-index: 2;
                position: relative;
                font-weight: 500;
            }}
            .emoji-sparkle {{
                position: absolute;
                font-size: 2.5rem;
                animation: sparkle 3s ease-in-out infinite;
                opacity: 0.6;
            }}
            .sparkle-1 {{ top: 15%; left: 5%; animation-delay: 0s; }}
            .sparkle-2 {{ top: 40%; right: 8%; animation-delay: 1.5s; }}
            .sparkle-3 {{ bottom: 10%; left: 10%; animation-delay: 2.5s; }}
            .sparkle-4 {{ bottom: 25%; right: 12%; animation-delay: 3s; }}
        </style>

        <div class="fun-banner">
            <div class="emoji-sparkle sparkle-1">🌿</div>
            <div class="emoji-sparkle sparkle-2">✨</div>
            <div class="emoji-sparkle sparkle-3">🌱</div>
            <div class="emoji-sparkle sparkle-4">🍀</div>
            <h2>Hey {st.session_state.user_name}! 🌟</h2>
            <p>Ready to make eco-friendly choices that matter? Let’s dive in! 🌍💪</p>
        </div>
    """, unsafe_allow_html=True)
    


    st.markdown("""
        <style>
        /* Fade and bounce in */
        @keyframes fadeInBounce {
            0% { opacity: 0; transform: translateY(20px); }
            60% { transform: translateY(-10px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        /* Glowing border pulse */
        @keyframes pulse-glow {
            0% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
            100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
        }

        .input-section {
            background: linear-gradient(135deg, #2E7D32, #1B5E20);
            border-radius: 20px;
            padding: 2.5rem;
            margin: 2rem 0;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2);
            animation: fadeInBounce 1s ease;
            transition: all 0.3s ease-in-out;
        }

        .input-title {
            color: #FFFFFF;
            font-size: 2rem;
            font-weight: 900;
            text-align: center;
            margin-bottom: 0.5rem;
            letter-spacing: 1px;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        }

        .input-description {
            color: #E8F5E9;
            font-size: 1.2rem;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: 500;
        }

        /* Input radio buttons */
        .stRadio > div {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }

        .stRadio > div > label {
            background: #66BB6A;
            padding: 1.2rem 2.5rem;
            border-radius: 15px;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            color: white !important;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 3px solid transparent;
            animation: fadeInBounce 1s ease;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        .stRadio > div > label[data-baseweb="radio"] {
            background: #43A047;
            border: 3px solid #C8E6C9;
            animation: pulse-glow 2.5s infinite;
        }

        .stRadio > div > label:hover {
            background: #388E3C;
            transform: scale(1.05);
        }

        /* Upload section styling */
        .upload-section {
            text-align: center;
            padding: 2rem;
            border: 3px dashed #81C784;
            border-radius: 20px;
            margin-top: 1.5rem;
            background: rgba(255, 255, 255, 0.05);
        }

        .upload-icon {
            font-size: 3rem;
            color: #81C784;
            margin-bottom: 1rem;
            animation: pulse-glow 2s infinite;
        }

        /* Text input section */
        .text-input-section {
            background: rgba(255, 255, 255, 0.05);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 18px rgba(0,0,0,0.15);
            margin: 1rem 0;
            animation: fadeInBounce 1s ease;
        }

        .stTextArea > div > div > textarea {
            border: 2px solid #81C784 !important;
            border-radius: 12px !important;
            padding: 1.2rem !important;
            font-size: 1.1rem !important;
            background: #2D2D2D !important;
            color: #FFFFFF !important;
            transition: all 0.3s ease-in-out;
        }

        .stTextArea > div > div > textarea:focus {
            border-color: #A5D6A7 !important;
            box-shadow: 0 0 10px #A5D6A7 !important;
            background: #2D2D2D !important;
            color: #FFFFFF !important;
        }
        
        .stTextArea > div > div > textarea::placeholder {
            color: rgba(255, 255, 255, 0.7) !important;
        }
        
        .stTextArea > div > div > label {
            color: #FFFFFF !important;
            font-weight: 500 !important;
        }

        /* Analyze button */
        .stButton > button {
            background-color: #66BB6A !important;
            color: #FFFFFF !important;
            padding: 1rem 2rem !important;
            border-radius: 12px !important;
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            margin-top: 1rem !important;
            cursor: pointer;
            transition: background 0.3s ease;
            border: none !important;
        }

        .stButton > button:hover {
            background-color: #81C784 !important;
            color: #FFFFFF !important;
        }

        /* Audio section */
        .audio-section {
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
        }

        .audio-icon {
            font-size: 3rem;
            color: #66BB6A;
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)

    
    
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown('<div class="input-title">📊 Your Personal Carbon Footprint Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="input-description">Choose how you\'d like to analyze your carbon footprint</div>', unsafe_allow_html=True)
    
    # Input method selection with enhanced styling
    input_method = st.radio(
        "Select Input Method",
        ["Text Input", "Upload Receipt", "Audio Input"],
        horizontal=True,
        label_visibility="collapsed"
    )
    attached_file_path=[]
    user_input=None
    uploaded_file=None
    audio_file=None
    if input_method == "Text Input":
        st.markdown('<div class="text-input-section">', unsafe_allow_html=True)
        st.markdown('<p style="color: #FFFFFF; font-size: 1.1rem; margin-bottom: 1rem;">Describe your daily activities</p>', unsafe_allow_html=True)
        user_input = st.text_area(
            "Activity Description",
            placeholder="Describe your daily activities (e.g., 'Had beef burger, took Uber, ran AC for 5 hrs')",
            height=100,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif input_method == "Upload Receipt":
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
    
    # Add JavaScript to scroll down when spinner appears
    st.markdown("""
        <script>
            (function() {
                function scrollToSpinner() {
                    // Wait for spinner to appear, then scroll
                    setTimeout(function() {
                        const spinner = document.querySelector('[data-testid="stSpinner"]');
                        if (spinner) {
                            const spinnerPosition = spinner.getBoundingClientRect().top;
                            const streamlitNavbarHeight = 56;
                            const customNavbarHeight = 80;
                            const totalNavbarHeight = streamlitNavbarHeight + customNavbarHeight;
                            const scrollPosition = window.pageYOffset + spinnerPosition - totalNavbarHeight - 50;
                            window.scrollTo({ top: Math.max(0, scrollPosition), behavior: 'smooth' });
                        } else {
                            // Fallback: scroll down by a fixed amount
                            window.scrollBy({ top: 300, behavior: 'smooth' });
                        }
                    }, 200);
                }
                
                // Watch for spinner appearance
                const observer = new MutationObserver(function() {
                    const spinner = document.querySelector('[data-testid="stSpinner"]');
                    if (spinner && !window.spinnerScrolled) {
                        window.spinnerScrolled = true;
                        scrollToSpinner();
                    }
                });
                
                observer.observe(document.body, { childList: true, subtree: true });
                
                // Also check immediately in case spinner already exists
                if (document.querySelector('[data-testid="stSpinner"]')) {
                    scrollToSpinner();
                }
            })();
        </script>
    """, unsafe_allow_html=True)
    
    if st.button("Analyze", key="analyze_button"):
        if input_method == "Text Input" and user_input:
            with st.spinner("Analyzing your activities..."):
                # Get activities from backend
                activities = analyze_text(user_input, context_files=attached_file_path)
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
                
        elif input_method == "Upload Receipt" and uploaded_file:
            with st.spinner("Analyzing your receipt..."):
                # Get activities from backend
                activities = analyze_text(user_input, context_files=attached_file_path)
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
                    st.warning("No activities were detected in your receipt. Please try again with a clearer image.")
        elif input_method == "Audio Input" and audio_file:
            st.info("Audio analysis coming soon!")
        else:
            st.warning("Please provide input to analyze")
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
            /* Override Streamlit's default light theme - ensure white text on dark background */
            .stTextInput > div > div > input {
                background-color: #2D2D2D !important;
                color: #FFFFFF !important;
                border-color: #3D3D3D !important;
            }
            .stTextArea > div > div > textarea {
                background-color: #2D2D2D !important;
                color: #FFFFFF !important;
                border-color: #3D3D3D !important;
            }
            .stSelectbox > div > div > div {
                background-color: #2D2D2D !important;
                color: #FFFFFF !important;
                border-color: #3D3D3D !important;
            }
            .stRadio > div > div > label {
                color: #FFFFFF !important;
            }
            /* Ensure text is visible in input fields */
            .stTextInput > div > div > input::placeholder,
            .stTextArea > div > div > textarea::placeholder {
                color: rgba(255, 255, 255, 0.7) !important;
            }
            .stTextInput > div > div > input:focus,
            .stTextArea > div > div > textarea:focus {
                color: #FFFFFF !important;
                background-color: #2D2D2D !important;
            }
            /* Button styling - white background with dark text for visibility */
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

def validate_and_sanitize_carbon_data(carbon_data: List[Dict]) -> List[Dict]:
    """
    Validate and sanitize carbon data to handle edge cases.
    
    Args:
        carbon_data: List of carbon emission dictionaries
        
    Returns:
        List of validated and sanitized carbon emission dictionaries
    """
    if not carbon_data or not isinstance(carbon_data, list):
        return []
    
    MAX_CO2E_PER_ITEM = 10000  # Maximum reasonable CO2e per item in kg
    MAX_TOTAL_CO2E = 1000000   # Maximum reasonable total CO2e in kg
    
    validated_data = []
    
    for item in carbon_data:
        if not isinstance(item, dict):
            continue
            
        try:
            # Extract and validate co2e
            co2e = item.get('co2e', 0)
            if not isinstance(co2e, (int, float)):
                try:
                    co2e = float(co2e)
                except (ValueError, TypeError):
                    co2e = 0
            
            # Cap ridiculously large numbers
            if co2e > MAX_CO2E_PER_ITEM:
                co2e = MAX_CO2E_PER_ITEM
            
            # Ensure non-negative
            if co2e < 0:
                co2e = 0
            
            # Validate other required fields
            validated_item = {
                'co2e': co2e,
                'text': str(item.get('text', item.get('activity', 'Unknown Activity'))),
                'category': str(item.get('category', 'Unknown')),
                'quantity': float(item.get('quantity', 0)) if isinstance(item.get('quantity'), (int, float)) else 0,
                'unit': str(item.get('unit', '')),
                'co2e_impact_level': str(item.get('co2e_impact_level', '1')),
                'suggestion': str(item.get('suggestion', 'Consider alternatives'))
            }
            
            validated_data.append(validated_item)
            
        except Exception as e:
            # Skip invalid items
            continue
    
    # Check total CO2e
    total_co2 = sum(item['co2e'] for item in validated_data)
    if total_co2 > MAX_TOTAL_CO2E:
        # Scale down proportionally if total is too large
        scale_factor = MAX_TOTAL_CO2E / total_co2
        for item in validated_data:
            item['co2e'] = item['co2e'] * scale_factor
    
    return validated_data


def display_results():
    # Validate and sanitize data first
    try:
        if not hasattr(st.session_state, 'carbon_data') or not st.session_state.carbon_data:
            st.error("⚠️ No carbon data available. Please analyze your activities first.")
            return
        
        st.session_state.carbon_data = validate_and_sanitize_carbon_data(st.session_state.carbon_data)
        
        if not st.session_state.carbon_data:
            st.error("⚠️ No valid carbon data found. Please try analyzing again.")
            return
            
    except Exception as e:
        st.error(f"⚠️ Error validating data: {str(e)}")
        return
    
    st.markdown("""
        <style>
            /* Navigation Menubar - Fixed position below Streamlit's default menubar */
            .nav-menubar {
                position: fixed;
                top: 3.5rem; /* Position below Streamlit's default menubar (typically 3.5rem/56px) */
                left: 0;
                right: 0;
                background: rgba(30, 30, 30, 0.98);
                backdrop-filter: blur(10px);
                padding: 1rem 2rem;
                z-index: 999;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                border-bottom: 2px solid rgba(76, 175, 80, 0.3);
                width: 100%;
                box-sizing: border-box;
            }
            /* Add padding to body to account for both Streamlit's menubar and our custom navbar */
            .main .block-container {
                padding-top: 9rem; /* Streamlit menubar (3.5rem) + our menubar (5.5rem) */
            }
            .nav-menu {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 1.5rem;
                flex-wrap: wrap;
            }
            .nav-item {
                padding: 0.6rem 1.2rem;
                background: rgba(76, 175, 80, 0.2);
                border: 1px solid rgba(76, 175, 80, 0.4);
                border-radius: 20px;
                color: #FFFFFF;
                text-decoration: none;
                font-size: 0.9rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                white-space: nowrap;
            }
            .nav-item:hover {
                background: rgba(76, 175, 80, 0.4);
                border-color: rgba(76, 175, 80, 0.6);
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
            }
            .nav-item:active {
                transform: translateY(0);
            }
            /* Responsive design for mobile */
            @media (max-width: 768px) {
                .nav-menubar {
                    padding: 0.8rem 1rem;
                }
                .nav-menu {
                    gap: 0.8rem;
                }
                .nav-item {
                    padding: 0.5rem 0.8rem;
                    font-size: 0.8rem;
                }
            }
            /* Section anchors with offset for both Streamlit's menubar and our custom navbar */
            .section-anchor {
                scroll-margin-top: 150px; /* Streamlit menubar (56px) + our menubar (80px) + buffer */
                display: block;
            }
            /* Ensure smooth scrolling is enabled */
            html {
                scroll-behavior: smooth;
            }
            body {
                scroll-behavior: smooth;
            }
            
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
    
    # Navigation Menubar
    st.markdown("""
        <div class="nav-menubar">
            <div class="nav-menu">
                <a href="#overview" class="nav-item">📊 Overview</a>
                <a href="#riskometer" class="nav-item">⚠️ Impact Level</a>
                <a href="#statistics" class="nav-item">📊 Statistics</a>
                <a href="#analysis" class="nav-item">🌱 Analysis</a>
            </div>
        </div>
        <script>
            (function() {
                // Wait for DOM to be ready
                function initSmoothScroll() {
                    // Smooth scroll with offset for fixed navbar
                    document.querySelectorAll('.nav-item').forEach(item => {
                        item.addEventListener('click', function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            const targetId = this.getAttribute('href').substring(1);
                            const targetElement = document.getElementById(targetId);
                            if (targetElement) {
                                const streamlitNavbarHeight = 56; // Streamlit's default menubar height
                                const customNavbarHeight = 80; // Our custom navbar height
                                const totalNavbarHeight = streamlitNavbarHeight + customNavbarHeight;
                                const elementPosition = targetElement.getBoundingClientRect().top;
                                const offsetPosition = elementPosition + window.pageYOffset - totalNavbarHeight;
                                
                                // Use smooth scroll
                                window.scrollTo({
                                    top: Math.max(0, offsetPosition),
                                    behavior: 'smooth'
                                });
                            }
                        });
                    });
                }
                
                // Initialize when DOM is ready
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', initSmoothScroll);
                } else {
                    initSmoothScroll();
                }
                
                // Re-initialize after Streamlit reruns (for dynamic content)
                setTimeout(initSmoothScroll, 100);
                setTimeout(initSmoothScroll, 500);
            })();
        </script>
    """, unsafe_allow_html=True)
    
    st.markdown('<div id="overview" class="section-anchor"><div class="header-text">Your Carbon Footprint Analysis</div></div>', unsafe_allow_html=True)
    
    # Calculate total CO2e with error handling
    try:
        total_co2 = sum(item.get('co2e', 0) for item in st.session_state.carbon_data)
        # Ensure total_co2 is a valid number
        if not isinstance(total_co2, (int, float)) or not (0 <= total_co2 <= 1000000):
            total_co2 = 0
    except Exception as e:
        st.warning(f"⚠️ Error calculating total CO2: {str(e)}")
        total_co2 = 0
    
    # Add congratulatory message if carbon emission is 0
    try:
        if abs(total_co2) < 0.1:  # Using a small epsilon to account for floating point precision
            st.markdown("""
                <div id="congrats-message" style="
                    position: fixed;
                    top: 136px; /* Streamlit menubar (56px) + our menubar (80px) */
                    left: 0;
                    right: 0;
                    background: rgba(46, 125, 50, 0.9);
                    color: white;
                    padding: 1rem;
                    text-align: center;
                    z-index: 998;
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
    except Exception as e:
        pass  # Silently handle any errors in congratulatory message
    
    # st.markdown('<div class="carbon-label">Total Carbon Footprint</div>', unsafe_allow_html=True)
    # st.markdown(f'<div class="carbon-number">{total_co2:.2f} kg CO₂e</div>', unsafe_allow_html=True)

    def generate_dynamic_summary(co2: float) -> str:
        # Validate input
        if not isinstance(co2, (int, float)) or co2 < 0:
            co2 = 0
        if co2 > 1000000:  # Cap at reasonable maximum
            co2 = 1000000
        
        global_average = 12
        
        # Calculate equivalents with error handling
        try:
            smartphones = (co2 * 1000 / 404) if co2 > 0 else 0
            if not isinstance(smartphones, (int, float)) or smartphones < 0:
                smartphones = 0
        except (ZeroDivisionError, ValueError, TypeError):
            smartphones = 0
        
        try:
            tshirts = (co2 * 1000 / 190) if co2 > 0 else 0
            if not isinstance(tshirts, (int, float)) or tshirts < 0:
                tshirts = 0
        except (ZeroDivisionError, ValueError, TypeError):
            tshirts = 0
        
        try:
            car_km = (co2 * 1000 / 200) if co2 > 0 else 0
            if not isinstance(car_km, (int, float)) or car_km < 0:
                car_km = 0
        except (ZeroDivisionError, ValueError, TypeError):
            car_km = 0
        
        try:
            percent_diff = ((co2 - global_average) / global_average) * 100
            if not isinstance(percent_diff, (int, float)):
                percent_diff = 0
        except (ZeroDivisionError, ValueError, TypeError):
            percent_diff = 0

        # Calculate projections with validation
        try:
            projected_co2_current = co2 * 365
            if not isinstance(projected_co2_current, (int, float)) or projected_co2_current < 0:
                projected_co2_current = 0
        except (ValueError, TypeError):
            projected_co2_current = 0
        
        try:
            projected_co2_suggested = projected_co2_current * 0.7  # 30% reduction
            if not isinstance(projected_co2_suggested, (int, float)) or projected_co2_suggested < 0:
                projected_co2_suggested = 0
        except (ValueError, TypeError):
            projected_co2_suggested = 0

        if co2 < 4:
            behavior_tag = "EXCELLENT 🌟"
            tone = "👏 You're far below the global average! Your lifestyle is highly sustainable."
            bg_gradient = "linear-gradient(135deg, #43cea2, #185a9d)"
            status_color = "#4CAF50"
            status_icon = "🌟"
        elif co2 < 10:
            behavior_tag = "GOOD 🌿"
            tone = "👍 You're doing well! A few mindful changes can make your impact even greener."
            bg_gradient = "linear-gradient(135deg, #8BC34A, #558B2F)"
            status_color = "#8BC34A"
            status_icon = "🌿"
        elif co2 < 16:
            behavior_tag = "CONCERNING ⚠️"
            tone = "⚠️ You're above the average. It's a good time to explore greener alternatives."
            bg_gradient = "linear-gradient(135deg, #FFC107, #FF9800)"
            status_color = "#FFC107"
            status_icon = "⚠️"
        else:
            behavior_tag = "CRITICAL 🚨"
            tone = "🚨 Your carbon footprint is quite high. Small consistent changes can help reverse this trend."
            bg_gradient = "linear-gradient(135deg, #EF5350, #B71C1C)"
            status_color = "#F44336"
            status_icon = "🚨"

        return f"""
        <style>
            .summary-box {{
                background: {bg_gradient};
                color: white;
                padding: 1.5rem;
                border-radius: 20px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
                font-family: 'Segoe UI', sans-serif;
                animation: fadeIn 1s ease-in-out;
                display: flex;
                flex-direction: column;
                margin: 0.5rem;
                position: relative;
                overflow: visible;
            }}
            .summary-header {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-size: 1.5rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
            }}
            .summary-tone {{
                font-size: 1.1rem;
                margin-bottom: 1rem;
            }}
            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 1rem;
                margin-bottom: 1rem;
                flex-grow: 1;
            }}
            .summary-column {{
                background: rgba(255, 255, 255, 0.1);
                padding: 1rem;
                border-radius: 12px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
            }}
            .column-title {{
                font-size: 1.1rem;
                font-weight: bold;
                margin-bottom: 0.8rem;
                padding-bottom: 0.3rem;
                border-bottom: 2px solid rgba(255, 255, 255, 0.2);
                text-align: center;
            }}
            .summary-card {{
                background: rgba(255, 255, 255, 0.05);
                padding: 0.8rem;
                border-radius: 8px;
                margin-bottom: 0.8rem;
                flex-grow: 1;
            }}
            .summary-card h4 {{
                margin: 0;
                font-size: 0.9rem;
                font-weight: bold;
                color: rgba(255, 255, 255, 0.9);
            }}
            .summary-card p {{
                margin: 0.2rem 0 0;
                font-size: 1.1rem;
                font-weight: bold;
            }}
            .status-section {{
                background: rgba(255, 255, 255, 0.1);
                padding: 1rem;
                border-radius: 12px;
                margin-bottom: 1rem;
                text-align: center;
            }}
            .status-icon {{
                font-size: 2rem;
                margin-bottom: 0.5rem;
            }}
            .status-title {{
                font-size: 1.3rem;
                font-weight: bold;
                margin-bottom: 0.3rem;
            }}
            .status-description {{
                font-size: 1rem;
                opacity: 0.9;
                margin-bottom: 0.3rem;
            }}
            .impact-badge {{
                background-color: rgba(255, 255, 255, 0.2);
                padding: 0.4rem 0.8rem;
                border-radius: 20px;
                display: inline-block;
                font-weight: bold;
                font-size: 1.4rem;
                box-shadow: inset 0 0 5px rgba(255,255,255,0.3);
                text-align: center;
                margin: 0.3rem 0;
            }}
            .impact-footer {{
                text-align: center;
                font-size: 1rem;
                margin-top: 1rem;
                padding: 1rem 0;
                border-top: 2px solid rgba(255, 255, 255, 0.2);
                position: relative;
                z-index: 1;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
        </style>

        <div class="summary-box">
            <div class="summary-header">🧠 Personalized Sustainability Reflection</div>
            <div class="summary-tone">{tone}</div>

            <div class="status-section">
                <div class="status-icon">{status_icon}</div>
                <div class="status-title">Current Status</div>
                <div class="status-description">Your carbon footprint is currently at <span class="impact-badge">{co2:.2f} kg CO₂e</span> per day</div>
                <div class="status-description">This is {abs(percent_diff):.1f}% {"below" if percent_diff < 0 else "above"} the global average</div>
            </div>

            <div class="summary-grid">
                

                <div class="summary-column">
                    <div class="column-title">📈 Projected if Current Continues</div>
                    <div class="summary-card">
                        <h4>🌍 Annual CO₂ Emissions</h4>
                        <p>{projected_co2_current:.2f} kg</p>
                    </div>
                    <div class="summary-card">
                        <h4>📊 Compared to Global Avg</h4>
                        <p>{percent_diff:+.1f}%</p>
                    </div>
                    <div class="summary-card">
                        <h4>📱 Smartphones Produced</h4>
                        <p>{(projected_co2_current * 1000 / 404):.1f}</p>
                    </div>
                    <div class="summary-card">
                        <h4>👕 T-Shirts Manufactured</h4>
                        <p>{(projected_co2_current * 1000 / 190):.1f}</p>
                    </div>
                    <div class="summary-card">
                        <h4>🚗 Car Kilometers</h4>
                        <p>{(projected_co2_current * 1000 / 200):.1f} km</p>
                    </div>
                </div>

                <div class="summary-column">
                    <div class="column-title">🌿 Projected with Green Suggestions</div>
                    <div class="summary-card">
                        <h4>🌍 Annual CO₂ Emissions</h4>
                        <p>{projected_co2_suggested:.2f} kg</p>
                    </div>
                    <div class="summary-card">
                        <h4>📊 Compared to Global Avg</h4>
                        <p>{(projected_co2_suggested/365 - global_average)/global_average*100:+.1f}%</p>
                    </div>
                    <div class="summary-card">
                        <h4>📱 Smartphones Produced</h4>
                        <p>{(projected_co2_suggested * 1000 / 404):.1f}</p>
                    </div>
                    <div class="summary-card">
                        <h4>👕 T-Shirts Manufactured</h4>
                        <p>{(projected_co2_suggested * 1000 / 190):.1f}</p>
                    </div>
                    <div class="summary-card">
                        <h4>🚗 Car Kilometers</h4>
                        <p>{(projected_co2_suggested * 1000 / 200):.1f} km</p>
                    </div>
                </div>
            </div>

            <div class="impact-footer">
                Your current status: <span class="impact-badge">{behavior_tag}</span>
            </div>
        </div>
        """

    # Overview Summary Section
    try:
        st.markdown('<div id="sustainability" class="section-anchor"></div>', unsafe_allow_html=True)
        if total_co2 >= 0 and total_co2 <= 1000000:  # Valid range check
            components.html(generate_dynamic_summary(total_co2), height=1100)
        else:
            st.warning("⚠️ Unable to display summary due to invalid data.")
    except Exception as e:
        st.warning(f"⚠️ Error displaying overview summary: {str(e)}")
    
    # Riskometer Section
    try:
        # Calculate risk level and fill percentage with exponential scaling
        max_co2 = 24  # Maximum CO2 for 100% fill
        base = 2  # Exponential base for more dramatic scaling
        
        # Validate total_co2 before calculations
        if not isinstance(total_co2, (int, float)) or total_co2 < 0:
            total_co2 = 0
        
        # Calculate exponential fill percentage
        if total_co2 <= 0:
            fill_percentage = 0
        else:
            # Exponential scaling: percentage = (base^(x/max) - 1) * 100
            try:
                fill_percentage = min((pow(base, total_co2/max_co2) - 1) * 100, 100)
                if not isinstance(fill_percentage, (int, float)) or fill_percentage < 0:
                    fill_percentage = 0
                if fill_percentage > 100:
                    fill_percentage = 100
            except (OverflowError, ValueError):
                fill_percentage = 100
        
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
        arrow_position = max(0, min(100, fill_percentage))  # Clamp between 0 and 100
        
        st.markdown(f"""
            <div id="riskometer" class="section-anchor"></div>
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
    except Exception as e:
        st.warning(f"⚠️ Error displaying impact level: {str(e)}")
    
    # Metrics Section
    try:
        # Recalculate total_co2 for metrics (in case it was modified)
        total_co2 = sum(item.get('co2e', 0) for item in st.session_state.carbon_data)
        if not isinstance(total_co2, (int, float)) or total_co2 < 0:
            total_co2 = 0
        
        # Create metrics row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Carbon Footprint", f"{total_co2:.2f} kg CO₂e")
        with col2:
            st.metric("Daily Average", f"{total_co2/1:.2f} kg CO₂e/day")
        with col3:
            global_average = 12
            try:
                percentage_diff = ((total_co2 - global_average) / global_average) * 100
                if not isinstance(percentage_diff, (int, float)):
                    percentage_diff = 0
            except (ZeroDivisionError, ValueError, TypeError):
                percentage_diff = 0
            st.metric("Compared to Global Average", 
                     f"{total_co2:.2f} kg CO₂e",
                     f"{percentage_diff:+.1f}%",
                     delta_color="inverse")
    except Exception as e:
        st.warning(f"⚠️ Error displaying metrics: {str(e)}")

    # Statistics Section - Combined Distribution and Activities
    try:
        st.markdown('<div id="statistics" class="section-anchor"></div>', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #FFFFFF; font-size: 2rem; font-weight: bold; text-align: center; margin: 2rem 0;">📊 Statistics</h2>', unsafe_allow_html=True)
        
        # Validate data before creating charts
        if not st.session_state.carbon_data:
            st.warning("⚠️ No data available for statistics.")
        else:
            # Create two columns for charts
            col1, col2 = st.columns(2)

            # Pie Chart with conditional display
            with col1:
                try:
                    st.subheader("Distribution by Category")
                    if total_co2 > 0 and len(st.session_state.carbon_data) > 0:
                        # Regular pie chart for non-zero emissions
                        df = pd.DataFrame(st.session_state.carbon_data)
                        
                        # Validate DataFrame
                        if 'co2e' not in df.columns or 'category' not in df.columns:
                            st.warning("⚠️ Missing required data columns for pie chart.")
                        else:
                            # Filter out invalid values
                            df = df[df['co2e'] > 0].copy()
                            
                            if len(df) > 0:
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
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                )
                                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
                            else:
                                st.info("No valid data points for pie chart.")
                    else:
                        # Zero emission pie chart (all green)
                        fig_pie = px.pie(
                            values=[1],
                            names=['Zero Emission'],
                            title='Carbon Footprint Distribution',
                            color_discrete_sequence=['#4CAF50']
                        )
                        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                        fig_pie.update_layout(
                            showlegend=False,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                        )
                        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
                except Exception as e:
                    st.warning(f"⚠️ Error displaying pie chart: {str(e)}")

            # Bar Chart
            with col2:
                try:
                    st.subheader("Emissions by Activity")
                    if total_co2 > 0 and len(st.session_state.carbon_data) > 0:
                        df = pd.DataFrame(st.session_state.carbon_data)
                        
                        # Validate DataFrame
                        if 'co2e' not in df.columns or 'text' not in df.columns or 'category' not in df.columns:
                            st.warning("⚠️ Missing required data columns for bar chart.")
                        else:
                            # Filter out invalid values
                            df = df[df['co2e'] > 0].copy()
                            
                            if len(df) > 0:
                                # Limit number of activities shown to prevent overcrowding
                                df = df.nlargest(20, 'co2e')
                                
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
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                )
                                fig_bar.update_traces(texttemplate='%{x:.1f} kg', textposition='outside')
                                st.plotly_chart(fig_bar, use_container_width=True)
                            else:
                                st.info("No valid data points for bar chart.")
                    else:
                        # Display a message for zero emissions
                        st.markdown(
                            """
                            <div style='text-align: center; padding: 20px; color: black; background: #E8F5E9; border-radius: 10px;'>
                                <h3>No Emissions Recorded!</h3>
                                <p>Great job maintaining zero carbon emissions!</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                except Exception as e:
                    st.warning(f"⚠️ Error displaying bar chart: {str(e)}")
    except Exception as e:
        st.warning(f"⚠️ Error displaying statistics section: {str(e)}")
    # st.markdown('<div class="graph-title" style="text-align: left;">Carbon Footprint by Category</div>', unsafe_allow_html=True)
    # st.plotly_chart(fig, use_container_width=True)
   
    # Activity Impact Analysis Section
    st.markdown("""
        <style>
            .section-header {
                font-size: 4.5rem;
                font-weight: bold;
                color: #FFFFFF;
                text-align: center;
                margin: 2rem 0;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            .stExpander {
                background: rgba(45, 45, 45, 0.8);
                border-radius: 20px;
                padding: 1rem;
                margin: 1rem 0;
            }
            .stExpander > div > div > div {
                padding: 1.5rem;
                font-size: 1.8rem;
                font-weight: bold;
                color: #FFFFFF;
                text-align: center;
            }
            .activity-card {
                position: relative;
                padding: 1rem;
                border-radius: 12px;
                margin-bottom: 0.8rem;
                transition: all 0.3s ease;
            }
            .activity-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            .impact-button {
                position: absolute;
                top: 0.5rem;
                right: 0.5rem;
                padding: 0.3rem 0.8rem;
                border-radius: 15px;
                font-size: 0.9rem;
                font-weight: bold;
                border: none;
                cursor: pointer;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }
            .activity-line {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-bottom: 0.5rem;
                padding-right: 5rem;
            }
            .activity-label {
                font-size: 0.9rem;
                color: rgba(255, 255, 255, 0.8);
                min-width: 80px;
            }
            .activity-value {
                font-size: 1rem;
                color: #FFFFFF;
            }
            .suggestion-line {
                background: rgba(255, 255, 255, 0.1);
                padding: 0.8rem;
                border-radius: 8px;
                margin-top: 0.5rem;
            }
            /* Impact level color themes */
            .card-low {
                background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(45, 45, 45, 0.8));
                border-left: 4px solid #4CAF50;
            }
            .card-medium {
                background: linear-gradient(135deg, rgba(255, 193, 7, 0.2), rgba(45, 45, 45, 0.8));
                border-left: 4px solid #FFC107;
            }
            .card-high {
                background: linear-gradient(135deg, rgba(255, 87, 34, 0.2), rgba(45, 45, 45, 0.8));
                border-left: 4px solid #FF5722;
            }
            .card-very-high {
                background: linear-gradient(135deg, rgba(244, 67, 54, 0.2), rgba(45, 45, 45, 0.8));
                border-left: 4px solid #F44336;
            }
            .button-low {
                background: #4CAF50;
                color: white;
            }
            .button-medium {
                background: #FFC107;
                color: #000000;
            }
            .button-high {
                background: #FF5722;
                color: white;
            }
            .button-very-high {
                background: #F44336;
                color: white;
            }
            @media (max-width: 768px) {
                .activity-line {
                    flex-direction: column;
                    gap: 0.2rem;
                    padding-right: 0;
                }
                .activity-label {
                    min-width: auto;
                }
                .impact-button {
                    position: relative;
                    top: 0;
                    right: 0;
                    margin-bottom: 0.5rem;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    # Activity Impact Analysis Section
    try:
        # Display the main header outside the expander
        st.markdown('<div id="analysis" class="section-anchor"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🌱 Activity Impact Analysis</div>', unsafe_allow_html=True)

        # Get the number of tasks
        num_tasks = len(st.session_state.carbon_data) if st.session_state.carbon_data else 0

        if num_tasks == 0:
            st.info("No activities to display.")
        else:
            # Create the expander with task count in the header
            with st.expander(f"📋 {num_tasks} Activities Analyzed", expanded=True):
                # Create compact rows for each activity
                for idx, activity in enumerate(st.session_state.carbon_data):
                    try:
                        # Validate activity data
                        if not isinstance(activity, dict):
                            continue
                        
                        # Map impact levels and get color class
                        impact_level = str(activity.get('co2e_impact_level', '1')).lower()
                        impact_mapping = {
                            '1': ('LOW', 'low'),
                            '2': ('MEDIUM', 'medium'),
                            '3': ('HIGH', 'high'),
                            '4': ('VERY HIGH', 'very-high'),
                            'low': ('LOW', 'low'),
                            'medium': ('MEDIUM', 'medium'),
                            'high': ('HIGH', 'high'),
                            'very high': ('VERY HIGH', 'very-high'),
                            'very_high': ('VERY HIGH', 'very-high')
                        }
                        display_impact, impact_class = impact_mapping.get(impact_level, ('LOW', 'low'))
                        
                        # Get safe values with defaults
                        activity_text = str(activity.get("text", activity.get("activity", "Unknown Activity")))
                        category = str(activity.get("category", "Unknown"))
                        quantity = activity.get("quantity", 0)
                        unit = str(activity.get("unit", ""))
                        co2e = activity.get("co2e", 0)
                        suggestion = str(activity.get('suggestion', 'Consider alternatives'))
                        
                        # Validate co2e
                        if not isinstance(co2e, (int, float)) or co2e < 0:
                            co2e = 0
                        
                        st.markdown(f"""
                            <div class="activity-card card-{impact_class}">
                                <button class="impact-button button-{impact_class}">{display_impact}</button>
                                <div class="activity-line">
                                    <span class="activity-label">Activity:</span>
                                    <span class="activity-value">{activity_text}</span>
                                    <span class="activity-label">Category:</span>
                                    <span class="activity-value">{category}</span>
                                </div>
                                <div class="activity-line">
                                    <span class="activity-label">Quantity:</span>
                                    <span class="activity-value">{quantity} {unit}</span>
                                    <span class="activity-label">CO₂e:</span>
                                    <span class="activity-value">{co2e:.2f} kg</span>
                                </div>
                                <div class="suggestion-line">
                                    <span class="activity-label">Suggestion:</span>
                                    <span class="activity-value">{suggestion}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        # Skip this activity if there's an error
                        continue
    except Exception as e:
        st.warning(f"⚠️ Error displaying activity analysis: {str(e)}")

    # Impact comparison with colorful flash cards
    try:
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
        
        # Validate total_co2 before calculations
        if not isinstance(total_co2, (int, float)) or total_co2 < 0:
            total_co2 = 0
        
        # Calculate equivalents with error handling
        try:
            smartphones = (total_co2 * 1000 / 404) if total_co2 > 0 else 0
            if not isinstance(smartphones, (int, float)) or smartphones < 0:
                smartphones = 0
        except (ZeroDivisionError, ValueError, TypeError):
            smartphones = 0
        
        try:
            tshirts = (total_co2 * 1000 / 190) if total_co2 > 0 else 0
            if not isinstance(tshirts, (int, float)) or tshirts < 0:
                tshirts = 0
        except (ZeroDivisionError, ValueError, TypeError):
            tshirts = 0
        
        try:
            car_km = (total_co2 * 1000 / 200) if total_co2 > 0 else 0
            if not isinstance(car_km, (int, float)) or car_km < 0:
                car_km = 0
        except (ZeroDivisionError, ValueError, TypeError):
            car_km = 0
        
        # Smartphones card
        st.markdown(f"""
            <div class="impact-card impact-card-1">
                <div class="impact-icon">📱</div>
                <div class="impact-title">Smartphones</div>
                <div class="impact-value">{smartphones:.1f}</div>
                <div class="impact-description">Equivalent to manufacturing this many smartphones (404 kg CO₂e each)</div>
            </div>
        """, unsafe_allow_html=True)
        
        # T-shirts card
        st.markdown(f"""
            <div class="impact-card impact-card-2">
                <div class="impact-icon">👕</div>
                <div class="impact-title">T-shirts</div>
                <div class="impact-value">{tshirts:.1f}</div>
                <div class="impact-description">Equivalent to manufacturing this many t-shirts (190 kg CO₂e each)</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Car kilometers card
        st.markdown(f"""
            <div class="impact-card impact-card-3">
                <div class="impact-icon">🚗</div>
                <div class="impact-title">Car Kilometers</div>
                <div class="impact-value">{car_km:.1f}</div>
                <div class="impact-description">Equivalent to driving this many kilometers (200g CO₂e per km)</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"⚠️ Error displaying impact comparison: {str(e)}")
    
    # Detailed Explanation Section
    try:
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
    except Exception as e:
        st.warning(f"⚠️ Error displaying detailed explanation: {str(e)}")

    





if __name__ == "__main__":
    main() 