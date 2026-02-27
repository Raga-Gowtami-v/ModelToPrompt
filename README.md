🚀 Project R
Privacy-First AI Gateway for Secure Data & Prompt-Driven Model Building and Pickling

Upload data. Protect sensitive information. Describe what you want to predict.
Get a production-ready ML model — instantly.

🌍 The Problem

Organizations want to use AI — but face two major barriers:

🔒 Data Privacy Risks
Sensitive information (PII) is often embedded in documents and datasets, making AI adoption risky.

🧠 ML Complexity
Building machine learning models requires expertise in preprocessing, feature engineering, model selection, and evaluation.

Most tools solve one of these problems.
Project R solves both — in one unified gateway.

💡 The Solution

Project R is a privacy-first AI gateway that combines:

Automated PII detection and masking

Prompt-driven ML model orchestration

All behind a simple, developer-friendly interface.

✨ Core Features
🔐 1. Intelligent PII Detection & Masking

Upload:

📄 CSV

📄 PDF

📄 DOCX

🖼 PNG / JPG

📝 Plain text

Project R automatically:

Detects PII using:

Regex-based pattern matching

Named Entity Recognition (spaCy)

Masks sensitive data (emails, phone numbers, Aadhaar-like IDs, names, etc.)

Returns sanitized output ready for safe ML processing

This enables:

Compliance-ready AI workflows

Secure preprocessing pipelines

Responsible AI usage

🤖 2. Prompt-to-Model Training Engine

Upload:

📊 CSV dataset

💬 Natural-language prompt

Example prompts:

“Predict customer churn”

“Estimate house prices”

“Classify loan approvals”

Project R will automatically:

Interpret user intent

Detect target column

Infer task type (classification or regression)

Build preprocessing pipelines

Train a scikit-learn model

Evaluate performance

Export a production-ready .pkl model

No manual feature engineering.
No model selection confusion.
No code required.

🧠 Under the Hood
🔎 PII Engine

Regex pattern library

spaCy NER (en_core_web_sm)

Structured + unstructured document handling

Extensible detection modules

🏗 ML Orchestration Engine

Automatic target detection

Task inference (classification / regression)

ColumnTransformer preprocessing

RandomForest-based training

Evaluation metrics:

Classification → Accuracy, F1

Regression → RMSE, R²

Model serialization via joblib

🏛 Architecture Overview
User
 │
 ├── Upload Document → PII Engine → Masked Output
 │
 └── Upload CSV + Prompt
        ↓
    Intent Parser
        ↓
    Preprocessing Builder
        ↓
    Model Trainer
        ↓
    Evaluator
        ↓
    Downloadable .pkl Model

Two independent but integrated AI pipelines.

⚡ Quick Start
🖥 Backend Setup
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload
🐍 Python Version (Important)

Recommended: Python 3.10 – 3.12

Python 3.13+ may fail while building spaCy dependencies (e.g., blis) on Windows.

If using 3.13+, switch to 3.11/3.12 virtual environment.

🌐 Frontend Setup
cd frontend
npm install
npm start
🐳 Docker Deployment
docker-compose up --build
🔌 API Endpoints
Core Routes
Method	Endpoint	Description
GET	/	Landing page
POST	/sanitize	Upload file for PII detection
POST	/automated-ml	Upload CSV + prompt to train model
REST API
🔐 PII

POST /api/scan/upload → Scan uploaded file

POST /api/scan/text → Scan raw text

🤖 ML

POST /api/prompt/train → Train model from CSV + prompt

GET /api/model/download/{model_id} → Download trained model

GET /api/model/list → List trained models

🛡 Why Project R Is Different

Unlike traditional AutoML tools:

It prioritizes data privacy first

It supports both structured and unstructured inputs

It integrates security + ML in a single workflow

It enables responsible AI adoption

Project R isn’t just a model trainer.
It’s a secure AI gateway.

🎯 Use Cases

Startups wanting quick ML prototypes

Students building ML projects safely

Enterprises needing PII sanitization before AI workflows

Analysts with datasets but no ML expertise

🚀 Vision

To become the secure bridge between raw data and intelligent systems.

AI should be powerful.
It should also be responsible.

Project R ensures both.
