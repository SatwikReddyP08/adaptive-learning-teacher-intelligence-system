import requests
from config.gemini_config import GEMINI_API_KEY

GEMINI_BASE_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-2.5-flash:generateContent"
)

def generate_class_analytics(memories_text):

    prompt = f"""
You are analyzing a classroom of learners.

Each learner memory is a compressed representation of a student's learning patterns, strengths, weaknesses, confidence tendencies, and support needs.

Learner Memories:

{memories_text}

Generate the following sections:

Overall Class Performance

Common Strengths

Common Weaknesses

Learning Patterns

Learner Support Needs

Teaching Recommendations

Rules:
- Teacher-friendly language.
- Keep each section concise.
- Use the headings exactly as written above.
- Do not output JSON.
- Do not mention individual learners.
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    url = f"{GEMINI_BASE_URL}?key={GEMINI_API_KEY}"

    try:

        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        return (
            data["candidates"][0]
            ["content"]["parts"][0]["text"]
        )

    except Exception:
        return None