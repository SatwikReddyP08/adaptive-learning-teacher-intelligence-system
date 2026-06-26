import streamlit as st
import json
import os
import re
from ai.class_analysis import generate_class_analytics

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

STUDENT_DIR = "data/students"


# ==========================
# ACCESS CONTROL
# ==========================

if (
    "logged_in" not in st.session_state
    or not st.session_state["logged_in"]
):
    st.warning("You must log in first.")
    st.switch_page("app.py")

elif st.session_state["role"] != "teacher":
    st.error("Access denied. Teachers only.")
    st.switch_page("app.py")


# ==========================
# HELPERS
# ==========================

def load_all_students():

    students = []

    if not os.path.exists(STUDENT_DIR):
        return students

    for filename in os.listdir(STUDENT_DIR):

        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(
            STUDENT_DIR,
            filename
        )

        try:

            with open(filepath, "r") as f:
                history = json.load(f)

            if history:

                students.append(
                    {
                        "username":
                        filename.replace(".json", ""),

                        "history":
                        history,

                        "latest":
                        history[-1]
                    }
                )

        except Exception:
            pass

    return students

def extract_confidence(confidence_text):

    try:
        return float(
            confidence_text.split("/")[0].strip()
        )
    except Exception:
        return 0

def show_student_history(student):

    history = student["history"]

    st.subheader("📚 Learning History")

    for i, interaction in enumerate(history):

        st.markdown(
            f"### Interaction {i+1}"
        )

        st.write(
            "**Date/Time:**",
            interaction.get(
                "timestamp",
                "N/A"
            )
        )

        st.write(
            "**Topic:**",
            interaction.get(
                "topic",
                ""
            )
        )

        st.write(
            "**Question:**",
            interaction.get(
                "question",
                ""
            )
        )

        st.markdown(
            "**Student Answer:**"
        )

        st.code(
            interaction.get(
                "answer",
                ""
            )
        )

        reasoning_questions = (
            interaction.get(
                "reasoning_questions",
                []
            )
        )

        reasoning_answers = (
            interaction.get(
                "reasoning_answers",
                []
            )
        )

        if reasoning_questions:

            for idx, question in enumerate(
                reasoning_questions
            ):
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

        learner_state = (
            interaction.get(
                "learner_state",
                {}
            )
        )

        st.write("**Strengths:**")
        st.markdown(
            learner_state.get(
                "Strengths",
                ""
            )
        )

        st.write(
            "**Areas for Improvement:**"
        )

        st.markdown(
            learner_state.get(
                "Weaknesses",
                ""
            )
        )


        st.write(
            "**Confidence Level:**"
        )

        st.write(
            learner_state.get(
                "Confidence Level",
                ""
            )
        )

        st.write(
            "**Overall Performance Summary:**"
        )

        st.write(
            learner_state.get(
                "Overall Performance Summary",
                ""
            )
        )

        st.markdown("---")


# ==========================
# PAGE
# ==========================

st.title("👩‍🏫 Teacher Dashboard")

students = load_all_students()

if not students:

    st.info(
        "No student learning data available yet."
    )

    st.stop()


tab1, tab2 = st.tabs(
    [
        "Class Overview",
        "Student Profiles"
    ]
)


# ==========================
# TAB 1
# ==========================

with tab1:

    confidence_scores = []

    attention_count = 0

    for student in students:

        learner_state = (
            student["latest"]
            .get("learner_state", {})
        )

        confidence = extract_confidence(
            learner_state.get(
                "Confidence Level",
                "0"
            )
        )

        confidence_scores.append(
            confidence
        )

        if confidence < 5:
            attention_count += 1

    avg_confidence = (
        round(
            sum(confidence_scores)
            / len(confidence_scores),
            1
        )
        if confidence_scores
        else 0
    )

    st.subheader("Class Overview")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Students",
        len(students)
    )

    c2.metric(
        "Average Confidence",
        f"{avg_confidence}/10"
    )

    c3.metric(
        "Students Requiring Attention",
        attention_count
    )

    st.divider()

    if st.button(
        "Generate Class Analytics",
        type="primary"
    ):

        memories = []

        for idx, student in enumerate(students):

            learner_state = (
                student["latest"]
                .get("learner_state", {})
            )

            learner_memory = (
                learner_state.get(
                    "Learner Memory",
                    ""
                )
            )

            if learner_memory:

                memories.append(
                    f"""
Learner {idx+1}:

{learner_memory}
"""
                )

        if not memories:

            st.warning(
                "No learner memories available."
            )

        else:

            with st.spinner(
                "Generating class analytics..."
            ):

                analytics = (
                    generate_class_analytics(
                        "\n\n".join(memories)
                    )
                )

            if analytics:

                st.subheader(
                    "AI Class Analytics"
                )

                st.write(
                    analytics
                )

            else:

                st.error(
                    "Unable to generate class analytics. Please try again."
                )


# ==========================
# TAB 2
# ==========================

with tab2:

    student_names = [
        s["username"]
        for s in students
    ]

    selected_name = st.selectbox(
        "Select Student",
        student_names
    )

    selected_student = next(
        s
        for s in students
        if s["username"] == selected_name
    )

    latest = selected_student["latest"]

    learner_state = (
        latest.get(
            "learner_state",
            {}
        )
    )

    st.subheader(
        "Current Learner Profile"
    )

    st.write(
        "**Confidence Level:**"
    )

    st.write(
        learner_state.get(
            "Confidence Level",
            "N/A"
        )
    )

    st.write(
        "**Strengths:**"
    )

    st.markdown(
        learner_state.get(
            "Strengths",
            "N/A"
        )
    )

    st.write(
        "**Areas for Improvement:**"
    )

    st.markdown(
        learner_state.get(
            "Weaknesses",
            "N/A"
        )
    )


    st.write(
        "**Overall Performance Summary:**"
    )

    st.write(
        learner_state.get(
            "Overall Performance Summary",
            "N/A"
        )
    )

    st.divider()

    if st.button(
        "📚 View Full Learning History"
    ):

        st.session_state[
            "show_teacher_history"
        ] = True

    if st.session_state.get(
        "show_teacher_history",
        False
    ):

        show_student_history(
            selected_student
        )