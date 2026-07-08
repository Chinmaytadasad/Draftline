import sys
import json
import urllib.request
import urllib.error

def run_test(prompt: str, description: str):
    print(f"\n{'='*50}\nTesting: {description}\nPrompt: '{prompt}'\n{'-'*50}")
    url = "http://localhost:8000/agent"
    data = json.dumps({"request": prompt}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"Plan Source: {result.get('plan_source')}")
            print(f"Assumptions: {result.get('assumptions')}")
            print(f"Document Path: {result.get('document_path')}")
            print("Plan:")
            for step in result.get('plan', []):
                print(f"  - Step {step.get('step')}: {step.get('action')} (tool: {step.get('tool')})")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(e.read().decode())
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")

STANDARD = ("Create a project plan for launching a mobile banking app MVP in 3 months", "Standard Test Case")
COMPLEX = ("We need some kind of document for the client meeting next week, probably about the API integration, not sure what format the client prefers", "Complex/Ambiguous Test Case")

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "both"
    if arg in ("standard", "both"):
        run_test(*STANDARD)
    if arg in ("complex", "both"):
        run_test(*COMPLEX)