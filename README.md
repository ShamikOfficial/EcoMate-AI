# 🌱 Carbonlyzer-AI

A sustainability-focused AI application that analyzes your carbon footprint from daily activities and receipts.

## Features

- 📸 Receipt OCR analysis
- ✍️ Freeform text input for daily activities
- 📊 Carbon footprint calculation
- 🌿 AI-powered sustainability suggestions
- 📈 Interactive visualizations

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/carbonlyzer-ai.git
cd carbonlyzer-ai
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install Tesseract OCR:
- Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`

4. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key if using GPT-4
```

## Running the Application

1. Start the FastAPI backend:
```bash
uvicorn app.api:app --reload
```

2. In a new terminal, start the Streamlit frontend:
```bash
streamlit run app/main.py
```

## Usage

1. Choose input method:
   - Upload a receipt image
   - Enter text describing your daily activities

2. View your carbon footprint analysis:
   - Total CO₂e emissions
   - Category breakdown
   - Sustainability suggestions

## Project Structure

```
carbonlyzer-ai/
├── app/                    # Application code
│   ├── main.py            # Streamlit frontend
│   ├── api.py             # FastAPI backend
│   ├── services/          # Core services
│   └── utils/             # Utility functions
├── data/                  # Data files
└── tests/                 # Test files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

---

## 🔍 What It Does

- 📸 **Scan receipts or bills** (image or text)
- 🧠 **AI extracts tasks** like eating meat, using AC, or taking a cab
- ♻️ **Estimates your carbon footprint** using verified global data
- 💡 **Recommends greener choices** to reduce your emissions
- 🌍 **Shows the impact** if millions made the same change

---
