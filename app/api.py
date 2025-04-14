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

# Activity patterns for regex matching
ACTIVITY_PATTERNS = {
    'Food': [
        r'(?:ate|had|consumed|bought)\s+(\d+)?\s*(?:beef|meat|burger|steak|chicken|fish|vegetarian|vegan)',
        r'(?:drank|had)\s+(\d+)?\s*(?:coffee|tea|milk|soda)'
    ],
    'Transport': [
        r'(?:took|used|drove)\s+(\d+)?\s*(?:km|miles)?\s*(?:uber|taxi|car|bus|train|bike|walk)',
        r'(?:flew|traveled)\s+(\d+)?\s*(?:km|miles)?\s*(?:plane|flight)'
    ],
    'Energy': [
        r'(?:used|ran)\s+(\d+)?\s*(?:hours?|hrs?)?\s*(?:AC|heater|light|appliance)',
        r'(?:consumed|used)\s+(\d+)?\s*(?:kWh|watts?)?\s*(?:electricity|power)'
    ],
    'Shopping': [
        r'(?:bought|purchased)\s+(\d+)?\s*(?:plastic|reusable|bag|item)',
        r'(?:shopped|bought)\s+(\d+)?\s*(?:clothes|electronics|furniture)'
    ]
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
        activities = extract_activities(text)
        
        return {"activities": activities}
    except Exception as e:
        logger.error(f"Error processing receipt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/text")
async def analyze_text(text: str):
    """Process text input and extract activities"""
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text input cannot be empty")
        
        activities = extract_activities(text)
        return {"activities": activities}
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def extract_activities(text: str) -> List[Dict]:
    """Extract activities from text using regex patterns"""
    activities = []
    text = text.lower()
    print("Extracting activities from text:")
    try:
        for category, patterns in ACTIVITY_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    try:
                        quantity = match.group(1) if match.group(1) else "1"
                        activity_text = match.group(0)
                        
                        activities.append({
                            "text": activity_text,
                            "category": category,
                            "quantity": float(quantity),
                            "co2e": 0.0  # Will be calculated by carbon service
                        })
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error processing match: {str(e)}")
                        continue
        
        if not activities:
            logger.warning("No activities found in text")
        
        return activities
    except Exception as e:
        logger.error(f"Error in extract_activities: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 