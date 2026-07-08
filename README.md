# Draftline AI Engine

A full-stack autonomous AI agent system that generates professional, industry-standard documents (`.docx`) based on natural language requests. 

The system features a **FastAPI backend** powered by the Groq API (`llama-3.3-70b-versatile`) with robust retry and deterministic fallback mechanisms, paired with a **Vite + React frontend** offering a premium, aesthetic, and highly interactive user experience.

## Features
- **Intelligent Planning & Execution**: The AI breaks down complex tasks into a structured JSON plan before executing them step-by-step.
- **Industry-Ready Outputs**: Prompts are engineered to generate concise, professional, and accessible content (e.g., Executive Summaries, Timelines).
- **Resilient Architecture**: Uses `tenacity` for exponential backoff on LLM calls. If the LLM is entirely unavailable, the system gracefully degrades to a deterministic, static fallback plan without failing the user.
- **Modern UI**: A beautifully crafted frontend built with Vite, React, and Vanilla CSS, featuring dynamic execution logs and real-time plan viewing.

---

## Setup Instructions

### Prerequisites
- **Python 3.10+** (for the backend)
- **Node.js 18+** (for the frontend)

### 1. Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Obtain a Groq API Key:**
   - Go to the [Groq Console](https://console.groq.com/).
   - Create an account, generate an API key, and set it in your environment:
     - **Windows PowerShell:** `$env:GROQ_API_KEY="your_api_key_here"`
     - **Linux/macOS:** `export GROQ_API_KEY="your_api_key_here"`

### 2. Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```
2. **Install dependencies:**
   ```bash
   npm install
   ```

---

## Running the System

You will need two terminal windows to run the frontend and backend simultaneously.

### Start the Backend
In your first terminal (with the Python virtual environment activated inside the `backend/` directory):
```bash
uvicorn main:app --port 8000
```
*The API will run at `http://localhost:8000`. API docs are available at `http://localhost:8000/docs`.*

### Start the Frontend
In your second terminal (inside the `frontend/` directory):
```bash
npm run dev
```
*The web interface will be available at `http://localhost:5173`. Open this in your browser to interact with the system.*

---

## Architecture Overview

- **`main.py`**: FastAPI app exposing `POST /agent`. Configured with CORS for the frontend and mounts a `/output` static route for `.docx` downloads.
- **`planner.py`**: Uses specialized prompting to force the LLM into returning a concise, industry-standard JSON task list. Falls back via `main.py` on complete failure.
- **`executor.py`**: Iterates through the plan. Steps tagged `tool: "llm"` dynamically generate content, while timeline steps render structured data tables. The prompt engineering enforces crisp, professional writing.
- **`doc_generator.py`**: Assembles the `.docx` using `python-docx`.
- **`frontend/`**: A Vite React SPA that communicates with the backend, displaying live execution statuses, assumptions, and providing the final document download link.

## Testing the Forced-Timeout (Fallback) Mode

To demonstrate the deterministic fallback mechanism, you can force the LLM to time out:

1. Set the force timeout flag:
   - **Windows PowerShell:** `$env:FORCE_LLM_TIMEOUT="1"`
   - **Linux/macOS:** `export FORCE_LLM_TIMEOUT="1"`
2. Start the backend server.
3. Submit a request via the frontend. The system will log retry attempts and eventually fall back gracefully, returning a complete static document with `plan_source: "fallback"`.