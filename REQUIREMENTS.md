# Secure Data & Automated ML Pipeline - Requirements Document

## 1. Purpose
Define product and engineering requirements for a privacy-first gateway that:
1. Detects and masks personally identifiable information (PII) in uploaded content.
2. Trains downloadable ML models from CSV data using a natural-language prompt.

## 2. Scope
### In Scope
- Backend APIs for PII scanning/sanitization and prompt-driven model training.
- Frontend flows for upload, scan results, model training, and model download/listing.
- Local and Docker-based deployment.

### Out of Scope (current release)
- Authentication/authorization.
- Multi-tenant isolation.
- Model inference/serving endpoint after training.
- Fine-grained data retention policies beyond local file storage.

## 3. User Roles
- **Data Analyst**: uploads files to sanitize PII and train models.
- **ML Engineer**: downloads trained `.pkl` models and tracks model artifacts.
- **Privacy Reviewer**: reviews detected entities and risk score.

## 4. Functional Requirements

### 4.1 PII Detection and Sanitization
- **FR-PII-001**: System shall accept uploaded files for PII scanning via API and UI.
- **FR-PII-002**: System shall support file types: `.csv`, `.txt`, `.pdf`, `.docx`, `.png`, `.jpg`, `.jpeg`.
- **FR-PII-003**: System shall extract text from images using OCR.
- **FR-PII-004**: System shall extract text from PDF and DOCX files.
- **FR-PII-005**: System shall detect PII using regex patterns.
- **FR-PII-006**: System shall detect PII entities using spaCy NER.
- **FR-PII-007**: System shall merge overlapping detections and keep the higher-confidence hit.
- **FR-PII-008**: System shall mask detected PII in output text using type placeholders (for example `[EMAIL]`).
- **FR-PII-009**: System shall return structured detection metadata (`type`, `value`, `start`, `end`, `confidence`, `detector`).
- **FR-PII-010**: System shall compute and return risk score, risk level, and detection breakdown.
- **FR-PII-011**: System shall allow direct text scanning (without file upload).

### 4.2 Prompt-Driven Model Training
- **FR-ML-001**: System shall accept CSV file + natural-language prompt for training.
- **FR-ML-002**: System shall reject non-CSV uploads for training endpoints.
- **FR-ML-003**: System shall infer task type (`classification` or `regression`) from prompt keywords.
- **FR-ML-004**: System shall infer target column from prompt text; if not found, default to the last CSV column.
- **FR-ML-005**: System shall encode categorical columns using label encoding.
- **FR-ML-006**: System shall impute missing numeric values using median.
- **FR-ML-007**: System shall split data into train/test with 80/20 ratio.
- **FR-ML-008**: System shall train `RandomForestClassifier` for classification tasks.
- **FR-ML-009**: System shall train `RandomForestRegressor` for regression tasks.
- **FR-ML-010**: System shall compute task-appropriate evaluation metrics.
- **FR-ML-011**: System shall save trained model artifacts as `.pkl` files in configured model directory.
- **FR-ML-012**: System shall provide model ID, dataset summary, and sample predictions in response.

### 4.3 Model Artifact Management
- **FR-MOD-001**: System shall list available trained models with id, filename, and size.
- **FR-MOD-002**: System shall support download of model artifacts by model ID.
- **FR-MOD-003**: System shall return `404` when requested model file does not exist.

### 4.4 Frontend Experience
- **FR-UI-001**: System shall provide navigation to Landing, Sanitize, Train, and Dashboard pages.
- **FR-UI-002**: Sanitize page shall support drag-and-drop and file picker upload.
- **FR-UI-003**: Sanitize page shall display risk meter and masked output after scan.
- **FR-UI-004**: Sanitize page shall display PII detections table with confidence and detector type.
- **FR-UI-005**: Train page shall require both CSV file and prompt before invoking training.
- **FR-UI-006**: Train page shall show training result and download link for model artifact.
- **FR-UI-007**: Dashboard page shall list existing trained models and provide download actions.

## 5. API Requirements

### 5.1 Public Endpoints
- `GET /` - Render landing HTML page.
- `POST /sanitize` - Upload file and return sanitized content + PII report + risk summary.
- `POST /automated-ml` - Upload CSV + prompt and return model summary + metrics + predictions.

### 5.2 Namespaced API Endpoints
- `POST /api/scan/upload` - File-based PII scan.
- `POST /api/scan/text` - Raw text PII scan.
- `POST /api/prompt/train` - Prompt-driven model training.
- `GET /api/model/list` - List all `.pkl` models.
- `GET /api/model/download/{model_id}` - Download specific model artifact.

### 5.3 Error Handling
- Return `400` for invalid/unsupported file types and invalid training input.
- Return `500` for unhandled processing failures.
- Return `404` for missing model artifact on download.

## 6. Non-Functional Requirements
- **NFR-001 (Deployability)**: System shall run via local Python/Node setup and via Docker Compose.
- **NFR-002 (Configurability)**: Upload and model directories shall be environment-configurable.
- **NFR-003 (Interoperability)**: Frontend API base URL shall be configurable via environment variable.
- **NFR-004 (Maintainability)**: Backend shall use modular services for privacy and model workflows.
- **NFR-005 (Observability)**: Backend shall log major training milestones (CSV load, training completion).
- **NFR-006 (Performance - baseline)**: System should process typical small-to-medium files interactively for UI use.

## 7. Security and Privacy Requirements (Current Baseline)
- **SEC-001**: System shall mask detected PII in sanitized output.
- **SEC-002**: Uploaded/trained artifacts shall be stored on server volumes/directories.
- **SEC-003**: CORS policy currently allows all origins for development compatibility.

## 8. Constraints and Dependencies
- Backend: FastAPI, spaCy (`en_core_web_sm`), scikit-learn, pandas, PyMuPDF, python-docx, pytesseract, Pillow.
- Frontend: React 18, react-router-dom, fetch API.
- OCR runtime requires Tesseract installed and available to `pytesseract`.

## 9. Assumptions and Known Gaps
- `MAX_FILE_SIZE_MB` exists in config but is not currently enforced in request handling.
- Authentication and role-based access are not currently implemented.
- Data persistence is filesystem-based (no DB metadata/history).
- Train page currently displays a generic score field, while backend returns metric dictionaries.

## 10. Acceptance Criteria (MVP)
1. User can upload a supported file and receive masked text + detections + risk score.
2. User can paste/submit raw text and receive equivalent scan output.
3. User can upload CSV + prompt and receive model ID, metrics, and downloadable artifact.
4. Dashboard shows newly trained models and allows download.
5. Unsupported file types and invalid training payloads produce clear `400` errors.
6. Missing model ID download requests produce `404`.
