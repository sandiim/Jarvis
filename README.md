# Jarvis Email Assistant

Jarvis Email Assistant is a production-grade tool designed for Gmail retrieval, parsing, and structured inbox intelligence. It leverages LLMs (via Groq/LangChain) to analyze emails, categorize them, determine priority, and extract actionable items.

## Features

- Gmail Integration: Secure retrieval of emails using Google OAuth2.
- AI-Powered Analysis: Structured analysis of email content including:
  - Priority detection (High, Medium, Low).
  - Category classification.
  - Concise summaries.
  - Automatic extraction of action items.
- Inbox Intelligence: Ability to summarize the overall state of the inbox.
- FastAPI Interface: A modern REST API for integrating email intelligence into other workflows.
- CLI Mode: A quick-start script for immediate inbox summaries.

## Architecture

The project follows a modular architecture:
- `api/`: FastAPI routers and endpoints for external access.
- `ai/`: Prompt templates and LLM analysis logic.
- `gmail/`: Core email retrieval and cleaning services.
- `services/`: Business logic for inbox management and sorting.
- `models/`: Pydantic models for strict data validation (API, Email, and Inbox models).

## Getting Started

### Prerequisites

- Python 3.10+
- A Google Cloud Project with the Gmail API enabled.
- A Groq API key for LLM analysis.

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Jarvis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Setup Credentials:
   - Place your `credentials.json` (from Google Cloud Console) in the root directory.
   - Create a `.env` file with your API keys:
     ```env
     GROQ_API_KEY=your_groq_api_key_here
     ```

### Usage

#### Run the CLI Tool
To get a quick summary of your latest emails:
```bash
python main.py
```

#### Run the API Server
To start the FastAPI server:
```bash
uvicorn app:app --reload
```
The API documentation will be available at `http://127.0.0.1:8000/docs`.

## API Endpoints

- `GET /health`: Check system status.
- `GET /api/v1/emails`: Retrieve and list emails.
- `GET /api/v1/analysis`: Get structured AI analysis of specific emails.

## Testing

The project includes a comprehensive test suite:
```bash
pytest
```
