from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from models import AgentRequest, AgentResponse
from planner import generate_plan
from executor import execute_plan

os.makedirs("output", exist_ok=True)

app = FastAPI(title="Autonomous AI Agent System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/output", StaticFiles(directory="output"), name="output")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with a clear 422 message."""
    return JSONResponse(
        status_code=422,
        content={"detail": "Request validation failed. Ensure 'request' is a non-empty string under 2000 characters.", "errors": exc.errors()}
    )

@app.post("/agent", response_model=AgentResponse)
async def run_agent(agent_request: AgentRequest):
    """
    Endpoint to process an agent request using Groq LLM Planner,
    falling back to a deterministic hardcoded plan on failure.
    """
    plan_source = "llm"
    assumptions = []
    
    try:
        plan, assumptions = await generate_plan(agent_request.request)
    except Exception as e:
        # Fallback on exhausted retries or fatal errors
        plan_source = "fallback"
        plan = [
            {"step": 1, "action": "Extract requirements from the request", "tool": "static"},
            {"step": 2, "action": "Generate project timeline and milestones", "tool": "static"},
            {"step": 3, "action": "Format the document with headings and a table", "tool": "docx"}
        ]
        assumptions = [
            f"Fallback triggered due to planner failure: {type(e).__name__}", 
            "Assuming standard 12-week MVP timeline for project plan.",
            f"Original Request: {agent_request.request}"
        ]
    
    # Execute the plan (which will also use LLM or fallback if it fails individually)
    execution_log, document_path = await execute_plan(plan=plan, assumptions=assumptions)
    
    return AgentResponse(
        plan=plan,
        execution_log=execution_log,
        document_path=document_path,
        plan_source=plan_source,
        assumptions=assumptions
    )
