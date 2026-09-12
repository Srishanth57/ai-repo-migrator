from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", "dummy-key"))

def get_migration_patch(code: str, instruction: str, error_feedback: str = "") -> str:
    prompt = f"""You are a code migration assistant.
Task: {instruction}
Return ONLY the full rewritten file, no explanation, no markdown fences.

Code:
{code}

{f"Previous attempt failed with error: {error_feedback}. Fix it." if error_feedback else ""}
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text