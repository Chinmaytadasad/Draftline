import json
import uuid
from typing import List, Dict, Any, Tuple
from doc_generator import generate_document
from llm_client import call_llm

async def execute_plan(plan: List[Dict[str, Any]], assumptions: List[str]) -> Tuple[List[Dict[str, Any]], str]:
    """
    Executes the given plan step by step dynamically.
    Returns the execution log and the document path.
    """
    execution_log = []
    content_blocks = []
    
    for step in plan:
        step_id = step.get("step")
        action = step.get("action")
        tool = step.get("tool")
        
        # Simulate execution logging
        log_entry = {
            "step": step_id,
            "status": "in_progress",
            "details": f"Executing action: {action}"
        }
        
        try:
            if tool == "llm":
                if "timeline" in action.lower() or "milestone" in action.lower():
                    prompt = f"Based on this action: {action}\nConsider these assumptions: {assumptions}\nGenerate a project timeline as JSON with this exact structure: {{\"phases\": [{{\"phase\": \"...\", \"milestone\": \"...\", \"duration\": \"...\"}}]}}. Return ONLY valid JSON, no markdown."
                    result = await call_llm(prompt=prompt, system_prompt="You are a senior technical project manager. Output realistic, industry-standard timelines that are easy to read.", json_mode=True)
                    content_blocks.append({"type": "heading", "content": f"Step: {action}", "level": 2})
                    try:
                        data = json.loads(result)
                        table_content = [["Phase", "Milestone", "Duration"]]
                        for p in data.get("phases", []):
                            table_content.append([str(p.get("phase", "")), str(p.get("milestone", "")), str(p.get("duration", ""))])
                        # Guard: if no data rows were added (empty/missing "phases"), fall back to paragraph
                        if len(table_content) <= 1:
                            content_blocks.append({"type": "paragraph", "content": result})
                        else:
                            content_blocks.append({"type": "table", "content": table_content})
                    except (json.JSONDecodeError, Exception):
                        content_blocks.append({"type": "paragraph", "content": result})
                else:
                    prompt = f"Perform this action: {action}\nConsider these assumptions: {assumptions}\nEnsure the output is concise, highly readable, and uses professional, industry-ready language. Avoid fluff and unnecessarily long paragraphs."
                    result = await call_llm(prompt=prompt, system_prompt="You are an expert technical writer and business consultant. Generate concise, industry-ready document content. Use clear, accessible language understandable by any stakeholder. Do not include markdown formatting wrappers like ```, just the plain text.")
                    content_blocks.append({"type": "heading", "content": f"Step: {action}", "level": 2})
                    content_blocks.append({"type": "paragraph", "content": result})
            elif tool == "static":
                content_blocks.append({"type": "heading", "content": f"Static Step: {action}", "level": 2})
                if step_id == 1:
                    content_blocks.append({"type": "paragraph", "content": "This is a statically generated requirements section due to a fallback. Project scope includes launching the MVP within 3 months."})
                elif step_id == 2:
                    content_blocks.append({"type": "paragraph", "content": "Static timeline details below:"})
                    content_blocks.append({
                        "type": "table",
                        "content": [
                            ["Phase", "Milestone", "Duration"],
                            ["Phase 1", "Requirements Gathering", "2 Weeks"],
                            ["Phase 2", "Development & MVP", "8 Weeks"],
                            ["Phase 3", "Testing & Launch", "2 Weeks"]
                        ]
                    })
                else:
                    content_blocks.append({"type": "paragraph", "content": "Generic static content for fallback step."})
            elif tool == "docx":
                content_blocks.append({"type": "paragraph", "content": f"Document formatting step: {action}"})
            else:
                content_blocks.append({"type": "paragraph", "content": f"Unknown tool step: {action}"})
            
            log_entry["status"] = "completed"
        except Exception as e:
            log_entry["status"] = "failed"
            log_entry["details"] += f" - Error: {str(e)}"
            
        execution_log.append(log_entry)

    unique_id = uuid.uuid4().hex[:8]
    filename = f"project_plan_{unique_id}.docx"
    document_path = generate_document(content_blocks, assumptions, filename)
    
    return execution_log, document_path