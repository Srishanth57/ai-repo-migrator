import google.generativeai as genai
import os
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def get_migration_patch(code: str, instruction: str, error_feedback: str = "") -> str:
    prompt = f"""You are a code migration assistant.
Task: {instruction}
Return ONLY a unified diff patch, no explanation, no markdown fences.

Code:
{code}

{f"Previous attempt failed with error: {error_feedback}. Fix it." if error_feedback else ""}
"""
    return model.generate_content(prompt).text