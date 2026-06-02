# 🌾 Kissan AI

AI-powered crop disease detection and virtual botanist for Pakistani farmers.

Upload a leaf photo → get instant disease diagnosis, treatment (chemical & organic), and Urdu recommendations.

## Features

- **Disease Scan** — Upload a crop leaf image, get AI-powered disease detection using a ResNet-18 CNN
- **Virtual Botanist** — LLM chatbot (Groq / Gemini) for farming advice in English & Urdu
- **Crop Guide** — Browse 52+ Pakistani crop profiles with fertilizer & cultivation info

## Tech Stack

- **Frontend:** React 19, Vite, Framer Motion
- **Backend:** Python, FastAPI
- **ML:** PyTorch, ResNet-18 (fine-tuned on PlantVillage)
- **LLMs:** Groq (Llama 3.3 70B), Google Gemini 2.5 Flash

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:
```
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```
> Get a free Groq key at [console.groq.com/keys](https://console.groq.com/keys)

Start the server:
```bash
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

## Project Structure

```
kissan AI/
├── backend/          # FastAPI server + ML model
├── frontend/         # React + Vite UI
├── ml/               # Model training notebook
├── crop fertilizers ds/   # Crop dataset (52+ crops)
└── plant disease ds/      # PlantVillage images
```
