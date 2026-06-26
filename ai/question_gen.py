import random
import requests
from config.gemini_config import GEMINI_API_KEY

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def generate_next_question(topic, learning_memory, fallback_bank):
    """
    Generate the next adaptive question using Gemini.
    Falls back to local bank if Gemini is unavailable.
    """

    user_prompt = f"""
    Topic: {topic}
    Student Analysis (LEARNING_MEMORY): {learning_memory}

    Generate:

    Question:
    A new question strictly within the given topic. Adapt difficulty and focus based on the student analysis.

    Reason:
    A short explanation (2-3 sentences) describing why this question was selected based on the learner memory.

    Rules:
    - Follow the format exactly (case sensitive).
    - The Question must be a coding/problem-solving question only. Do not ask for explanations, reasoning, or comparisons etc.
    - Keep the reason concise.
    - Plain text only.
    
    """

    payload = {
        "contents": [
            {"parts": [{"text": user_prompt}]}
        ]
    }

    url_with_key = f"{GEMINI_BASE_URL}?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url_with_key, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        text_output = data["candidates"][0]["content"]["parts"][0]["text"]

        question = ""
        reason = ""

        if "Question:" in text_output:
            question_start = text_output.find("Question:") + len("Question:")
            
            if "Reason:" in text_output:
                reason_start = text_output.find("Reason:")
                question = text_output[question_start:reason_start].strip()
                reason = text_output[reason_start + len("Reason:"):].strip()
            else:
                question = text_output[question_start:].strip()

        return {
            "question": question,
            "reason": reason
        }


    except Exception:
        # Fallback to local bank
        return {
            "question": random.choice(fallback_bank[topic]),
            "reason": "Generated from the local question bank because AI generation was unavailable."
        }
