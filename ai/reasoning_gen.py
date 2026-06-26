import requests
from config.gemini_config import GEMINI_API_KEY

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def generate_reasoning_questions(topic, question, student_answer, learning_memory):

    user_prompt = f"""
    Topic: {topic}

    Question:
    {question}

    Student Answer:
    {student_answer}

    Learner Memory:
    {learning_memory}

    Generate exactly 3 reasoning questions.

    The questions should:
    - Adapt strongly to the student's answer and learner memory.
    - Explore the most important reasoning gaps, strengths, or patterns visible in the submission.
    - Help uncover how the student thinks.

    Possible areas include:
    - Optimization
    - Complexity
    - Design choices
    - Alternatives
    - Edge cases
    - Scalability
    - Correctness
    - Problem understanding

    Rules:
    - Do not generate generic questions.
    - Tailor questions specifically to this student.
    - Keep each question under 20 words.
    - Output only the 3 questions.
    - One question per line.
    """

    payload = {
        "contents": [
            {"parts": [{"text": user_prompt}]}
        ]
    }

    url_with_key = f"{GEMINI_BASE_URL}?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            url_with_key,
            json=payload,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        text_output = data["candidates"][0]["content"]["parts"][0]["text"]

        questions = [
            line.strip()
            for line in text_output.split("\n")
            if line.strip()
        ]

        return questions[:3]

    except Exception:
        return [
            "Why did you choose this approach?",
            "What alternative approach could be used?",
            "How would your solution behave for large inputs?"
        ]