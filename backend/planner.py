import json
from typing import Tuple, List, Dict, Any
from llm_client import call_llm

PLANNER_SYSTEM_PROMPT = """
You are an expert project manager and autonomous AI agent planner.
Your goal is to parse the user's request and output a concise JSON task list to build a professional, industry-standard document.
If the request is ambiguous, you MUST make explicit assumptions and list them.

CRITICAL RULES:
1. Keep the document structure concise and impactful. Do not overcomplicate the plan.
2. Use standard industry formats (e.g., Executive Summary, Objectives, Timeline).
3. The final step must always be the 'docx' tool step.

You MUST output ONLY a valid JSON object with exactly these two keys:
{
    "plan": [
        {"step": 1, "action": "Write a concise Executive Summary...", "tool": "llm"},
        {"step": 2, "action": "Generate project timeline table...", "tool": "llm"},
        {"step": 3, "action": "Format and assemble the .docx document", "tool": "docx"}
    ],
    "assumptions": ["Assuming a 3-month timeline", "Assuming standard agile methodology"]
}
"""

async def generate_plan(request_text: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Calls the LLM to generate a plan and assumptions based on the request.
    """
    response_content = await call_llm(
        prompt=f"User request: {request_text}",
        system_prompt=PLANNER_SYSTEM_PROMPT,
        json_mode=True
    )
    
    try:
        data = json.loads(response_content)
        plan = data.get("plan", [])
        assumptions = data.get("assumptions", [])
        return plan, assumptions
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON.")
