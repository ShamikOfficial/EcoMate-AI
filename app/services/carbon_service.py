import pandas as pd
import os
from typing import Dict, List
import re
import logging

logger = logging.getLogger(__name__)

class CarbonCalculator:
    def __init__(self):
        try:
            self.emission_factors = pd.read_csv('data/emission_factors.csv')
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
                    # Find matching emission factor
                    factor = self._find_emission_factor(activity['text'], activity['category'])
                    
                    if factor is not None:
                        co2e = activity['quantity'] * factor['co2e_per_unit']
                        results.append({
                            'text': activity['text'],
                            'category': activity['category'],
                            'co2e': co2e,
                            'quantity': activity['quantity'],
                            'unit': factor['unit']
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
    
    def _find_emission_factor(self, text: str, category: str) -> Dict:
        """Find matching emission factor for activity"""
        try:
            text = text.lower()
            
            # Get all factors for the category
            category_factors = self.emission_factors[self.emission_factors['category'] == category]
            
            if category_factors.empty:
                logger.warning(f"No emission factors found for category: {category}")
                return None
            
            for _, row in category_factors.iterrows():
                # Check if any word from the activity is in the emission factor
                activity_words = set(text.split())
                factor_words = set(row['activity'].lower().split())
                
                if activity_words.intersection(factor_words):
                    return row.to_dict()
            
            return None
        except Exception as e:
            logger.error(f"Error in _find_emission_factor: {str(e)}")
            return None
    
    def get_sustainability_suggestions(self, activities: List[Dict]) -> List[str]:
        """Generate sustainability suggestions based on activities"""
        suggestions = []
        
        try:
            for activity in activities:
                try:
                    category = activity['category']
                    co2e = activity['co2e']
                    
                    if category == 'Food' and co2e > 1.0:
                        suggestions.append("Consider plant-based alternatives for high-carbon foods")
                    elif category == 'Transport' and co2e > 0.5:
                        suggestions.append("Try using public transit or carpooling for your commute")
                    elif category == 'Energy' and co2e > 0.3:
                        suggestions.append("Consider using energy-efficient appliances and turning off devices when not in use")
                    elif category == 'Shopping' and co2e > 0.1:
                        suggestions.append("Consider buying second-hand or sustainable products")
                except Exception as e:
                    logger.error(f"Error generating suggestion for activity {activity}: {str(e)}")
                    continue
            
            return suggestions
        except Exception as e:
            logger.error(f"Error in get_sustainability_suggestions: {str(e)}")
            return [] 