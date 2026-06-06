# Multimodal Respiratory AI Diagnostics (Demo)

A lightweight, multimodal deep learning prototype that predicts respiratory diseases, severity, and systemic organ risks from Chest X-rays and tabular clinical biomarkers (Age, SpO2, Creatinine, Troponin).

## Features
- **Multimodal AI Fusion**: Combines Image (ResNet18) and Tabular (MLP) pipelines.
- **Explainable AI (XAI)**: Includes simulated Grad-CAM heatmap localization and SHAP clinical feature importance visualization.
- **FastAPI Backend**: Provides a scalable `/predict` endpoint.
- **Streamlit Frontend**: A polished, responsive UI for clinical demonstrations.
- **Demo Mode**: Requires zero model training, generates realistic clinical outputs instantly.

## Architecture Structure
- `models/`: Contains the PyTorch architecture definitions (`ImageModel`, `TabularModel`, `MultimodalFusion`).
- `utils/explainability.py`: Functions for XAI generation.
- `api/main.py`: FastAPI server for inference.
- `ui/app.py`: Streamlit dashboard.
- `sample_data/`: Contains sample imagery.

## How to Run locally

### Prerequisites
Make sure you have Python 3.8+ installed.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
You can easily run both the backend and frontend simultaneously by double-clicking the `run.bat` script, or running:
```bash
run.bat
```

**Alternatively, run them separately in two terminals:**

Terminal 1 (Backend API):
```bash
uvicorn api.main:app --reload --port 8000
```

Terminal 2 (Frontend UI):
```bash
streamlit run ui/app.py
```

### 3. Usage
1. Open the provided Streamlit local URL (e.g. `http://localhost:8501`).
2. Upload a chest X-ray image (A mock sample is generated at `sample_data/sample_xray.png`).
3. Fill in the patient's biomarker readings.
4. Click "Run Multimodal AI Analysis" to get instantaneous inference results and visualizations.
