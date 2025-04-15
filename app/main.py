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
        .welcome-section {
            padding: 4rem 0;
            background: linear-gradient(160deg, #ffffff 0%, #f0f7f0 100%);
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .main-title {
            font-size: 4.5rem;
            font-weight: 700;
            color: #1B5E20;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }
        .slogan {
            font-size: 2rem;
            color: #388E3C;
            font-weight: 500;
            margin-bottom: 2rem;
            letter-spacing: 1px;
        }
        .eco-icon {
            font-size: 3.5rem;
            margin-bottom: 1rem;
        }
        .input-section {
            max-width: 600px;
            margin: 2rem auto;
            padding: 2rem;
        }
        .stButton > button {
            width: 200px;
            margin: 2rem auto;
            display: block;
            background-color: #1B5E20;
            color: white;
        }
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
            <div style='text-align: center;'>
                <div class="eco-icon">🌱</div>
                <h1 class="main-title">EcoMate-AI</h1>
                <h2 class="slogan">Small Swaps. Big Impact.</h2>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        name = st.text_input("First Name", value=st.session_state.user_name)
        surname = st.text_input("Last Name", value=st.session_state.user_surname)
        
        if st.button("Get Started"):
            if name.strip() and surname.strip():
                st.session_state.user_name = name
                st.session_state.user_surname = surname
                st.session_state.page = 'main'
                st.rerun()
            else:
                st.error("Please enter both your first and last name to continue.")
        st.markdown('</div>', unsafe_allow_html=True)

def main_page():
    # Welcome banner with user's name
    st.markdown(f"""
        <div style='background-color: #f0f7f0; padding: 1rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h2 style='color: #1B5E20; margin: 0;'>Welcome, {st.session_state.user_name} {st.session_state.user_surname}! 👋</h2>
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
            'Food': '#FF9999',
            'Transport': '#66B2FF',
            'Energy': '#99FF99',
            'Shopping': '#FFCC99'
        }
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