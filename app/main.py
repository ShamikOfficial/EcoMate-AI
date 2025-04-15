import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import io
import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv("env1.env")

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
    """Send text to backend for analysis"""
    try:
        response = requests.post(
            "http://localhost:8000/analyze/text",
            params={"text": text}
        )
        response.raise_for_status()
        return response.json()["activities"]
    except Exception as e:
        st.error(f"Error analyzing text: {str(e)}")
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
        <div style='background-color: #f0f7f0; padding: 1rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h2 style='color: #1B5E20; margin: 0;'>Welcome, {st.session_state.user_name}! 👋</h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Your Personal Carbon Footprint Analyzer")
    #print(os.getenv("API_PORT"))
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Upload Receipt", "Text Input"],
        horizontal=True
    )
    
    if input_method == "Upload Receipt":
        uploaded_file = st.file_uploader("Upload your receipt", type=['png', 'jpg', 'jpeg'])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Receipt', use_column_width=True)
            # TODO: Process image with OCR
    
    else:
        user_input = st.text_area(
            "Describe your daily activities (e.g., 'Had beef burger, took Uber, ran AC for 5 hrs')",
            height=100
        )
        if st.button("Analyze"):
            if user_input:
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
    
    # Category breakdown
    df = pd.DataFrame(st.session_state.carbon_data)
    fig = px.pie(
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
    fig.update_layout(
        title={
            'text': "Carbon Footprint by Category",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'size': 24,
                'family': "Arial, sans-serif",
                'color': '#1B5E20'
            }
        },
        font={
            'size': 16,
            'family': "Arial, sans-serif",
            'color': '#333333'
        },
        legend={
            'title': {
                'text': 'Categories',
                'font': {
                    'size': 18,
                    'family': "Arial, sans-serif",
                    'color': '#1B5E20'
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
        width=800,
        showlegend=False  # Hide legend since we're using labels
    )
    
    # Update traces for better visibility
    fig.update_traces(
        textposition='outside',
        textinfo='percent+label',
        textfont={
            'size': 16,
            'family': "Arial, sans-serif",
            'color': '#333333'
        },
        hovertemplate='<b>%{label}</b><br>CO₂e: %{value:.2f} kg<br>Percentage: %{percent:.1%}<extra></extra>',
        marker=dict(
            line=dict(color='#ffffff', width=2),
            colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        ),
        pull=[0.1, 0, 0, 0],  # Slightly pull the first slice for emphasis
        rotation=45  # Rotate the pie for better label placement
    )
    
    # Add annotations for better label visibility
    fig.update_annotations(
        font=dict(
            size=16,
            family="Arial, sans-serif",
            color="#333333"
        ),
        showarrow=True,
        arrowhead=1,
        arrowcolor="#666666",
        arrowsize=1,
        arrowwidth=2,
        ax=20,
        ay=-40
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed breakdown
    st.subheader("Detailed Breakdown")
    for item in st.session_state.carbon_data:
        with st.expander(f"{item['text']} - {item['co2e']:.2f} kg CO₂e"):
            st.write(f"Category: {item['category']}")
            st.write(f"Quantity: {item['quantity']} {item.get('unit', 'item')}")
            st.write(f"CO₂e: {item['co2e']:.2f} kg")
    
    # Suggestions
    if st.session_state.suggestions:
        st.header("🌿 Sustainability Suggestions")
        for suggestion in st.session_state.suggestions:
            st.info(suggestion)
    
    # Impact comparison
    st.subheader("🌍 Impact Comparison")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Equivalent to",
            f"{(total_co2 * 1000 / 404):.1f} smartphones",
            help="Average carbon footprint of manufacturing one smartphone is 404 kg CO₂e"
        )
    
    with col2:
        st.metric(
            "Equivalent to",
            f"{(total_co2 * 1000 / 190):.1f} t-shirts",
            help="Average carbon footprint of manufacturing one t-shirt is 190 kg CO₂e"
        )
    
    with col3:
        st.metric(
            "Equivalent to",
            f"{(total_co2 * 1000 / 200):.1f} km by car",
            help="Average car emits about 200g CO₂e per km"
        )

if __name__ == "__main__":
    main() 