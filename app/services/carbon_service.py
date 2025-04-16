import pandas as pd
import os
from typing import Dict, List
import re
import logging
import sys
from dotenv import load_dotenv

# Add the parent directory to system path to allow imports from app directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genai_model import GenAIModel

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv("env1.env")

# Initialize GenAI Model
API_KEY = os.getenv("GOOGLE_API_KEY")
genai_model = GenAIModel(api_key=API_KEY)

# Define the suggestion schema
SUGGESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "suggestions": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": ["suggestions"]
}

class CarbonCalculator:
    def __init__(self):
        try:
            self.emission_factors = pd.read_csv('data/emission_factor.csv')
            logger.info("Successfully loaded emission factors")
        except Exception as e:
            logger.error(f"Failed to load emission factors: {str(e)}")
            raise
    
    def calculate_carbon_footprint(self, activities: List[Dict]) -> List[Dict]:
        """Calculate carbon footprint for a list of activities"""
        results = []
        
        try:
            for activity in activities:
                try:
                    if activity['co2e_per_unit'] is not None and activity['co2e_per_unit']!='NA':
                        co2e = float(activity['quantity']) * float(activity['co2e_per_unit'])
                        results.append({
                            'text': activity['activity'],
                            'category': activity['category'],
                            'type': activity['type'],
                            'co2e_per_unit': activity['co2e_per_unit'],
                            'co2e': co2e,
                            'quantity': activity['quantity'],
                            'unit': activity['unit']
                        })
                    else:
                        logger.warning(f"No emission factor found for activity: {activity['text']}")
                except Exception as e:
                    logger.error(f"Error processing activity {activity}: {str(e)}")
                    continue
            
            if not results:
                logger.warning("No carbon footprint calculations were successful")
            
            return results
        except Exception as e:
            logger.error(f"Error in calculate_carbon_footprint: {str(e)}")
            raise
    
    def get_sustainability_suggestions(self, activities: List[Dict]) -> List[str]:
        """Generate sustainability suggestions directly using GenAI model"""
        try:
            # Convert activities to a more readable format for the AI model
            activity_summary = []
            for activity in activities:
                summary = (
                    f"{activity['text']} "
                    f"(Category: {activity['category']}, "
                    f"CO2e: {activity['co2e']:.2f} kg)"
                )
                activity_summary.append(summary)
            
            # Join all activities into a single text
            activities_text = "\n".join(activity_summary)
            
            # Generate suggestions using the GenAI model
            result = genai_model.generate_suggestions(
                text=activities_text,
                suggestion_schema=SUGGESTION_SCHEMA
            )
            
            return result.get('suggestions', [])
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return []
