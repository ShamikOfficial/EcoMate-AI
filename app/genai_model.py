import google.generativeai as genai
from typing import Dict, Any, Optional, Union, List
import os
import json

class GenAIModel:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash-latest"):
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
        """
        Generate content based on the prompt and schema.
        
        Args:
            prompt (str): The input prompt for the model
            schema (Dict[str, Any]): JSON schema for the output format
            context_files (Optional[List[str]]): List of file paths to provide as context
            temperature (float): Controls randomness in the output (0.0 to 1.0)
            
        Returns:
            Dict[str, Any]: Structured response based on the schema
        """
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
            
            # Parse and return the response
            return json.loads(response.text)
            
        except Exception as e:
            raise Exception(f"Error in content generation: {str(e)}")
            
    def extract_tasks(self, text: str, task_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract tasks from text using a custom schema.
        
        Args:
            text (str): Input text to analyze
            task_schema (Dict[str, Any]): Schema for task extraction
            
        Returns:
            Dict[str, Any]: Extracted tasks based on the schema
        """
        prompt = f'''Extract tasks and relevant information from the following text.
        Return the information in a structured format according to the provided schema.

        Text: {text}
        '''
        return self.generate_content(prompt, task_schema)
        
    def generate_suggestions(self, text: str, suggestion_schema: Dict[str, Any]) -> Dict[str, Any]:

        prompt = f'''Analyze the following text and provide relevant suggestions.
                Return the suggestions in a structured format according to the provided schema. Also only give suggestion if necessary. If task is already an optimal carbon emission compliant task, no need suggestion unnecessary.
                Make sure each suggestion is not more than 10-20 words.

                Text: {text}
                '''
        return self.generate_content(prompt, suggestion_schema)
        
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