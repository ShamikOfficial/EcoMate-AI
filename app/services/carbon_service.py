import pandas as pd
import os
from typing import Dict, List
import re
import logging
import requests
logger = logging.getLogger(__name__)

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

        """Send text to backend for analysis"""
        try:
            response = requests.post(
                "http://localhost:8000/generate/suggestions",
                params={"text": str(activities)}
            )
            response.raise_for_status()
            print("suggestion:",response.json())
            return response.json()["suggestions"]
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            return []
