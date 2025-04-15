from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
import io
import re
from typing import List, Dict
import json
import os
import logging
from .genai_model import GenAIModel
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Carbonlyzer-AI API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv("env1.env")
# Initialize GenAI Model
API_KEY = os.getenv("GOOGLE_API_KEY")
genai_model = GenAIModel(api_key=API_KEY)

# Default schemas
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

TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "priority": {"type": "string"},
                    "category": {"type": "string"},
                    "estimated_time": {"type": "string"}
                },
                "required": ["description", "priority"]
            }
        }
    },
    "required": ["tasks"]
}

SUGGESTION_SCHEMA_extra = {
    "type": "object",
    "properties": {
        "suggestions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "category": {"type": "string"},
                    "impact": {"type": "string"}
                },
                "required": ["title", "description"]
            }
        }
    },
    "required": ["suggestions"]
}

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

@app.post("/analyze/receipt")
async def analyze_receipt(file: UploadFile = File(...)):
    """Process receipt image and extract activities"""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Perform OCR
        try:
            text = pytesseract.image_to_string(image)
            logger.info(f"OCR extracted text: {text}")
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            raise HTTPException(status_code=500, detail="OCR processing failed")
        
        # Process text with regex
        activities = analyze_text(text)
        
        return activities
    except Exception as e:
        logger.error(f"Error processing receipt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/text")
async def analyze_text(text: str):
    """Process text input and extract activities using AI model"""
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text input cannot be empty")
        
        # Use the genai model to analyze emissions
        result = genai_model.analyze_emissions(
            text=text,
            emission_schema=EMISSION_SCHEMA,
            context_files=[os.path.join("data", "emission_factor.pdf")]
        )
        
        return {"activities": result['emission_record']}
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract/tasks")
async def extract_tasks(text: str):
    """Extract tasks from text using AI model"""
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text input cannot be empty")
        
        result = genai_model.extract_tasks(
            text=text,
            task_schema=TASK_SCHEMA
        )
        
        return result
    except Exception as e:
        logger.error(f"Error extracting tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/suggestions")
async def generate_suggestions(text: str):
    """Generate suggestions based on text using AI model"""
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text input cannot be empty")
        
        result = genai_model.generate_suggestions(
            text=text,
            suggestion_schema=SUGGESTION_SCHEMA
        )
        return result
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 