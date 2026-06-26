from email.mime import text
from tracemalloc import start
from turtle import heading

import requests
from config.gemini_config import GEMINI_API_KEY

# 1. FIXED: Changed model to gemini-2.5-flash and added the '?key=' placeholder
# Note: We append the actual key dynamically inside the function below
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def analyze_reasoning(topic, question, answer, reasoning_responses, prev_state=None):
    """
    Send reasoning data to Gemini API and return learner state.
    """

    # Build prompt for Gemini
    user_prompt = f"""
    Topic: {topic}
    Question: {question}
    Student Answer: {answer}
    Reasoning Questions and Answers: {reasoning_responses}
    Previous Learner Memory: {prev_state.get("Learner Memory") if prev_state else ""}

    Analyze the student's reasoning. Output EXACTLY in this format:

    Strengths:
    3 bullet points 

    Weaknesses:
    3 bullet points

    Confidence Level:
    X/10 - short explanation

    Overall Performance Summary:
    6-8 sentences. Summarize performance and next focus area.

    Learner Memory:
    4-5 sentences (40-50 words overall), capturing persistent learner traits, reasoning tendencies, improvement areas, and confidence patterns for future AI reference.


    Rules:
    - Plain text only
    - Use '-' for bullet points
    - No asterisks, no escape characters
    - Follow the headings and other format very strictly(Case sensitive)
    """


    payload = {
        "contents": [
            {"parts": [{"text": user_prompt}]}
        ]
    }

    # 2. FIXED: Appending the API key directly to the URL string
    url_with_key = f"{GEMINI_BASE_URL}?key={GEMINI_API_KEY}"

    # 3. FIXED: Removed the "Authorization: Bearer" header which was causing the 401 error
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Pass the url_with_key here instead of the static GEMINI_API_URL
        response = requests.post(url_with_key, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract text from Gemini response
        text_output = data["candidates"][0]["content"]["parts"][0]["text"]

        
        def extract_section(text, heading):
            start = text.find(heading)
            if start == -1:
                return ""
            start += len(heading)
            # find next heading
            next_headings = ["Strengths:", "Weaknesses:", "Confidence Level:", "Overall Performance Summary:", "Learner Memory:"]
            next_positions = [text.find(h, start) for h in next_headings if text.find(h, start) != -1]
            end = min(next_positions) if next_positions else len(text)
            return text[start:end].strip()

        learner_state = {
            "Strengths": extract_section(text_output, "Strengths:"),
            "Weaknesses": extract_section(text_output, "Weaknesses:"),
            "Confidence Level": extract_section(text_output, "Confidence Level:"),
            "Overall Performance Summary": extract_section(text_output, "Overall Performance Summary:"),
            "Learner Memory": extract_section(text_output, "Learner Memory:")
        }


        return learner_state

    except Exception as e:
        import traceback
        print("Gemini API error:", e)
        traceback.print_exc()
        return None