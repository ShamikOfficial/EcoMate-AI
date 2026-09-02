# EcoMate-AI

[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)]()

> AI-powered carbon footprint decoder that transforms receipts, bills, and daily activities into actionable environmental impact reports.

**[Portfolio](https://shamik-basu.com)** · **[GitHub Pages](https://shamikofficial.github.io)**

---

## Problem

People lack visibility into the carbon impact of everyday purchases and activities. Manual carbon accounting is tedious and generic tips don't reflect actual behavior.

## Solution

Upload a receipt image or describe your day in plain text. EcoMate-AI extracts activities via OCR/NLP, maps them to verified global emission factors, and generates personalized sustainability recommendations with interactive visualizations.

## Key Results

| Capability | Detail |
|------------|--------|
| Input modes | Receipt images + free-form text |
| Emission mapping | Verified global CO₂e factors (`data/emission_factor.csv`) |
| Output | Category breakdowns, global comparisons, ranked green tips |
| Stack | Streamlit + FastAPI + GPT-4o Vision |

## Features

- **Multimodal input** — upload receipt images or enter free-form text
- **OCR extraction** — reads items, quantities, and services from scanned receipts
- **CO₂ estimation** — maps activities to verified global emission factors
- **Personalized tips** — AI-generated suggestions ranked by impact
- **Global comparison** — contextualizes your footprint against regional averages
- **Interactive visualizations** — category breakdowns and trend charts

## Tech Stack

| Layer | Tools |
|-------|-------|
| Frontend | Streamlit |
| Backend | FastAPI |
| AI / OCR | OpenAI GPT-4o, Vision API |
| Data | pandas, NumPy |
| Visualization | Plotly, Matplotlib |

## Quick Start

```bash
git clone https://github.com/ShamikOfficial/EcoMate-AI.git
cd EcoMate-AI
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add your OpenAI API key
streamlit run app/main.py
```

## Project Structure

```
EcoMate-AI/
├── app/
│   ├── main.py             # Streamlit frontend
│   ├── api.py              # FastAPI backend
│   ├── genai_model.py      # GenAI inference layer
│   └── services/           # Carbon calculation logic
├── data/                   # Emission factor datasets
├── docs/architecture.md    # System design
└── requirements.txt
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full pipeline diagram.

## License

MIT — see [LICENSE](LICENSE).
