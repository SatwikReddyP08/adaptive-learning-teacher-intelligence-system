import streamlit as st
import json
import re
import os
import random
import datetime
from ai.analysis import analyze_reasoning
from ai.question_gen import generate_next_question
from ai.reasoning_gen import generate_reasoning_questions

if (
    "username" not in st.session_state
    or "role" not in st.session_state
):
    st.warning("Your session has expired. Please log in again.")
    st.switch_page("app.py")
    st.stop()

st.sidebar.markdown("### Session")

st.sidebar.write(
    f"User: {st.session_state['username']}"
)

st.sidebar.write(
    f"Role: {st.session_state['role'].capitalize()}"
)

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.switch_page("app.py")

QUESTION_FILE = "data/question_bank.json"
STUDENT_DIR = "data/students/"

def load_questions():
    with open(QUESTION_FILE, "r") as f:
        return json.load(f)


def save_progress(username, data):
    os.makedirs(STUDENT_DIR, exist_ok=True)
    filepath = os.path.join(STUDENT_DIR, f"{username}.json")

    # Add timestamp to this interaction
    data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Load existing history (list of interactions)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            history = json.load(f)
    else:
        history = []

    # Append new interaction
    history.append(data)

    # Save back full history
    with open(filepath, "w") as f:
        json.dump(history, f, indent=4)


def load_progress(username):
    filepath = os.path.join(STUDENT_DIR, f"{username}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)  # returns list of interactions
    return []


def show_learning_history(username):
    history = load_progress(username)
    st.title("📚 Learning History")

    if not history:
        st.info("No learning history available yet.")
        if st.button("← Back to Learning"):
            st.session_state["view_history"] = False
            st.rerun()
        return

    # For now, progress is a single interaction.
    # Later you can extend to multiple interactions stored in a list.
    interactions = history  # already a list of interactions

    for i, interaction in enumerate(interactions):
        st.markdown(f"### Interaction {i+1}")
        st.write("**Date/Time:**", interaction.get("timestamp", "N/A"))
        st.write("**Topic:**", interaction.get("topic", ""))
        st.write("**Question:**", interaction.get("question", ""))
        st.markdown("**Student Answer:**")
        st.code(interaction.get("answer", ""))


        reasoning_questions = interaction.get("reasoning_questions", [])

        reasoning_answers = interaction.get("reasoning_answers", [])
        if reasoning_questions:
            for idx, question in enumerate(reasoning_questions):
                clean_question = re.sub(r'^\d+\.\s*', '', question)
                st.write(
                    f"**Reasoning Question {idx+1}:**",
                    clean_question
                )

                if idx < len(reasoning_answers):
                    st.write(
                        "**Answer:**",
                        reasoning_answers[idx]
                    )

        learner_state = interaction.get("learner_state", {})
        st.write("**Strengths:**")
        st.markdown(learner_state["Strengths"])

        st.write("**Areas for Improvement:**")
        st.markdown(learner_state["Weaknesses"])

        st.write("**Confidence Level:**")
        st.write(learner_state["Confidence Level"])

        st.write("**Overall Performance Summary:**")
        st.write(learner_state["Overall Performance Summary"])

        st.markdown("---")

    if st.button("← Back to Learning"):
        st.session_state["view_history"] = False
        st.rerun()


def student_dashboard():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("You must log in first.")
        st.switch_page("app.py")
    elif st.session_state["role"] != "student":
        st.error("Access denied. Students only.")
        st.switch_page("app.py")

    username = st.session_state["username"]
    progress = load_progress(username)
    st.title(f"Welcome, {username} (Student Dashboard)")

    if st.button("📚 Learning History"):
        st.session_state["view_history"] = True
    
    if st.session_state.get("view_history", False):
        show_learning_history(username)
        return




    # Topic selection-
    questions = load_questions()
    topic = st.selectbox("Select a DSA Topic", list(questions.keys()))
    
    if st.button("Generate Question"):
        # Load previous learner state (for LEARNING_MEMORY)
        latest_state = (
            progress[-1]["learner_state"]
            if progress else None
        )

        learning_memory = (
            latest_state.get("Learner Memory", "")
            if latest_state else ""
        )


        st.session_state.pop("student_answer", None)
        st.session_state["answer_input"] = ""
        st.session_state.pop("analysis_complete", None)
        st.session_state.pop("question_reason", None)
        st.session_state.pop("reasoning_questions", None)
        st.session_state.pop("reason_q1", None)
        st.session_state.pop("reason_q2", None)
        st.session_state.pop("reason_q3", None)
        
        question_data = generate_next_question(
            topic,
            learning_memory,
            questions
        )

        st.session_state["current_question"] = question_data["question"]
        st.session_state["question_reason"] = question_data["reason"]

        st.session_state["current_topic"] = topic

    if "current_question" in st.session_state:
        st.subheader("Question")
        st.write(st.session_state["current_question"])

        if st.session_state.get("question_reason"):
            st.info(
                f"Why this question?\n\n"
                f"{st.session_state['question_reason']}"
            )

        if st.button("Skip Question"):
            st.session_state.pop("current_question", None)
            st.session_state.pop("student_answer", None)
            st.session_state.pop("question_reason", None)
            st.session_state.pop("analysis_complete", None)
            st.session_state.pop("reasoning_questions", None)
            st.session_state["answer_input"] = ""
            st.session_state.pop("reason_q1", None)
            st.session_state.pop("reason_q2", None)
            st.session_state.pop("reason_q3", None)

            st.info("Question skipped. Generate another question.")
            st.rerun()

        # Answer submission
        answer = st.text_area("Your Answer / Code", height=200, key="answer_input")
        if st.button("Submit Answer"):
            if not answer.strip():
                st.error("Please enter an answer before submitting.")
            else:
                st.session_state["student_answer"] = answer

                latest_state = (
                    progress[-1]["learner_state"]
                    if progress else None
                )

                learning_memory = (
                    latest_state.get("Learner Memory", "")
                    if latest_state else ""
                )

                st.session_state["reasoning_questions"] = (
                    generate_reasoning_questions(
                        st.session_state["current_topic"],
                        st.session_state["current_question"],
                        answer,
                        learning_memory
                    )
                )

        if ("student_answer" in st.session_state and not st.session_state.get("analysis_complete", False)):
            st.subheader("Reasoning Exploration")

            questions = st.session_state.get("reasoning_questions", [])

            q1 = st.text_area(
                questions[0] if len(questions) > 0 else "Question 1", key="reason_q1"
            )

            q2 = st.text_area(
                questions[1] if len(questions) > 1 else "Question 2", key="reason_q2"
            )

            q3 = st.text_area(
                questions[2] if len(questions) > 2 else "Question 3", key="reason_q3"
            )


            if st.button("Submit Reasoning"):

                if not q1.strip() or not q2.strip() or not q3.strip():
                    st.error("Please answer all reasoning questions.")
                    return
                
                prev_state = (
                    progress[-1]["learner_state"]
                    if progress else None
                )

                reasoning_data = {
                    "questions": st.session_state.get(
                        "reasoning_questions",
                        []
                    ),
                    "answers": [q1, q2, q3]
                }

                learner_state = analyze_reasoning(
                    st.session_state["current_topic"],
                    st.session_state["current_question"],
                    st.session_state["student_answer"],
                    reasoning_data,
                    prev_state
                )
                if learner_state is None:
                    st.error(
                        "AI analysis service is temporarily unavailable. "
                        "Please try again."
                    )
                    return

                data = {
                    "topic": st.session_state["current_topic"],
                    "question": st.session_state["current_question"],
                    "answer": st.session_state["student_answer"],
                    "reasoning_questions": st.session_state.get("reasoning_questions", []),
                    "reasoning_answers": [q1, q2, q3],
                    "learner_state": learner_state
                }

                save_progress(username, data)
                st.session_state["analysis_complete"] = True
                st.success("Progress saved with AI analysis!")
                st.session_state.pop("current_question", None)

                # Show ALL details immediately after submission
                st.subheader("Analysis Results")

                st.write("Strengths:")
                st.markdown(learner_state["Strengths"])

                st.write("Areas for Improvement:")
                st.markdown(learner_state["Weaknesses"])

                st.write("Confidence Level:")
                st.write(learner_state["Confidence Level"])

                st.write("Overall Performance Summary:")
                st.write(learner_state["Overall Performance Summary"])

    

if __name__ == "__main__":
    student_dashboard()
