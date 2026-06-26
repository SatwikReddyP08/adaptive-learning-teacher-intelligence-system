import streamlit as st
import json
import os

st.set_page_config(initial_sidebar_state="expanded", page_title="Adaptive Learning System", layout="centered")
USER_FILE = "data/users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def signup(role):
    st.subheader(f"{role.capitalize()} Signup")
    username = st.text_input("Username", key=f"{role}_signup_username")
    email = st.text_input("Email", key=f"{role}_signup_email")
    password = st.text_input("Password", type="password", key=f"{role}_signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key=f"{role}_signup_confirm")

    col1, col2 = st.columns(2)
    if col1.button("Signup", key=f"{role}_signup_button"):
        if not username or not email or not password or not confirm_password:
            st.error("All fields are required.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            users = load_users()
            if any(u["username"] == username for u in users):
                st.error("Username already exists.")
            else:
                users.append({"username": username, "email": email, "password": password, "role": role})
                save_users(users)
                st.success("Signup successful! Please login.")

def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    col1, col2 = st.columns(2)
    if col1.button("Login", key="login_button"):
        if not username or not password:
            st.error("Both fields are required.")
        else:
            users = load_users()
            for u in users:
                if u["username"] == username and u["password"] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = u["role"]
                    st.session_state["username"] = username
                    st.success(f"Welcome {username}!")

                    # ✅ Redirect immediately
                    if u["role"] == "student":
                        st.switch_page("pages/student_dashboard.py")
                    elif u["role"] == "teacher":
                        st.switch_page("pages/teacher_dashboard.py")
                    return
            st.error("Invalid credentials")


def main():
    # Sidebar: show session details + logout
    if st.session_state.get("logged_in", False):
        st.sidebar.markdown("### Session Info")
        st.sidebar.write(f"Role: {st.session_state['role'].capitalize()}")
        st.sidebar.write(f"User: {st.session_state['username']}")

        if st.sidebar.button("Logout", key="logout_button"):
            st.session_state.clear()
            st.success("You have logged out successfully.")
            st.switch_page("app.py")
    else:
        st.sidebar.markdown("### Not Logged In")
        st.sidebar.write("Please log in or sign up.")

 
    st.title("Adaptive Learning & Teacher Intelligence System (Prototype V1)")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "mode" not in st.session_state:
        st.session_state["mode"] = None  # can be "signup" or "login"

    if not st.session_state["logged_in"]:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.subheader("Welcome! Please Sign Up or Login")

        # Role selection always visible
        role = st.radio("Select Role", ["Student", "Teacher"], horizontal=True)

        # Two buttons side by side
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign Up"):
                st.session_state["mode"] = "signup"
        with col2:
            if st.button("Login"):
                st.session_state["mode"] = "login"

        # Show the correct form in the center
        if st.session_state["mode"] == "signup":
            signup(role.lower())
        elif st.session_state["mode"] == "login":
            login()

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        if st.session_state["role"] == "student":
            st.switch_page("pages/student_dashboard.py")
        elif st.session_state["role"] == "teacher":
            st.switch_page("pages/teacher_dashboard.py")


if __name__ == "__main__":
    main()
