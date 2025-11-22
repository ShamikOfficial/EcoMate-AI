import google.generativeai as genai
from typing import Dict, Any, Optional, Union, List
import os
import json

class GenAIModel:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        """
        Initialize the GenAI model with Google's Generative AI.
        
        Args:
            api_key (str): Google API key
            model_name (str): Name of the model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name=self.model_name)
        
    def generate_content(
        self,
        prompt: str,
        schema: Dict[str, Any],
        context_files: Optional[List[str]] = None,
        temperature: float = 0.0
    ) -> Dict[str, Any]:

        try:
            # Prepare the content list with prompt
            content = [prompt]
            
            # Add context files if provided
            if context_files:
                for file_path in context_files:
                    if os.path.exists(file_path):
                        file_name = os.path.basename(file_path)
                        file_content = genai.upload_file(path=file_path, display_name=file_name)
                        content.append(file_content)
            
            # Generate response
            response = self.model.generate_content(
                content,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    response_mime_type="application/json",
                    response_schema=schema
                )
            )
            print(json.loads(response.text))
            # Parse and return the response
            return json.loads(response.text)
            
        except Exception as e:
            raise Exception(f"Error in content generation: {str(e)}")
            
    def extract_tasks(self, text: str, schema: Dict[str, Any],context_files: Optional[List[str]] = None) -> Dict[str, Any]:
        prompt = f'''
        You are a smart carbon emission expert who will give the below details from the daily task of a person.
        Extract tasks and relevant information from the following text. 
        If you are provided any image or doc other than emission_factor.pdf, use it to extract text from it and use that as your input source text.
        
        Return the information in a structured format according to the provided schema and below description.
        category,type,activity as best match from emission pdf file provided. If not found give closest result for these attributes.
        quantity: Amount or quantity of activity extracted. If not found, then give normalized quantity by default.
        unit: S.I. unit of the task
        co2e_per_unit: Extract co2e_per_unit basis pdf emission file provided. If not in file, give best estimate.
        co2e_impact_level: strictly categorize into the following 4 category: (LOW),(MEDIUM),(HIGH),(VERY HIGH) based on category. If not able to identify, then give LOW by default.
        suggestion: according to the co2e_impact_level, give a suggestion for an alternative task with low co2 impact.
        
        InputText: {text}
        '''
        return self.generate_content(prompt, schema,context_files=context_files)
        

    def analyze_emissions(self, text: str, emission_schema: Dict[str, Any], context_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze emissions from activities described in the text.
        
        Args:
            text (str): Input text describing activities
            emission_schema (Dict[str, Any]): Schema for emission analysis
            context_files (Optional[List[str]]): List of emission factor files
            
        Returns:
            Dict[str, Any]: Emission analysis results based on the schema
        """
        prompt = f'''You are a smart assistant helping calculate carbon emissions from user activities.

Given a natural language input describing someone's day, extract all relevant real-world activities that produce carbon emissions — such as food consumption, travel, and energy usage.
Your goal is to extract at least one activity per applicable category (Food, Transport, Energy), if mentioned.
Return a list of structured JSON objects according to the provided schema.

Be strict:
Only include activities directly related to carbon-emitting actions
If the text mentions more than one activity, include each, even from different categories
The category,activity,type must be closest from the emission files provided to you below. Give best estimate of the fields if you are not able to find it in the pdf emission file provided.

Input source_text: {text}
'''
        return self.generate_content(prompt, emission_schema, context_files) 