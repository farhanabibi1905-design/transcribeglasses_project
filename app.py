import streamlit as st
import json
import streamlit_authenticator as stauth
from utils.stt_whisper import transcribe_audio
from utils.sound_detection import detect_sound
from utils.emotion_detection import detect_emotion
from utils.name_alert import check_name

USER_FILE = "data/users.json"

# ---------- Load or Initialize Users ----------
def load_users():
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

users = load_users()

# ---------- Sidebar for Auth ----------
st.sidebar.title("🔐 User Authentication")
auth_choice = st.sidebar.radio("Choose an option:", ["Login", "Sign Up"])

if auth_choice == "Sign Up":
    st.subheader("📝 Create an Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    full_name = st.text_input("Full Name")
    nickname = st.text_input("Nickname (for name alerts)")

    if st.button("Sign Up"):
        if username in users:
            st.error("Username already exists!")
        else:
            users[username] = {
                "password": password,
                "full_name": full_name,
                "nickname": nickname
            }
            save_users(users)
            st.success("Signup successful! Please login.")
elif auth_choice == "Login":
    st.subheader("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["name"] = users[username]["full_name"]
            st.session_state["nickname"] = users[username]["nickname"]
            st.success(f"Welcome, {users[username]['full_name']}!")
        else:
            st.error("Invalid credentials")

# ---------- Main App ----------
if st.session_state.get("logged_in", False):
    st.title("🎧 Smart Audio Detection & Emotion App")
    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])

    if uploaded_file:
        with open("temp_audio.wav", "wb") as f:
            f.write(uploaded_file.read())
        st.audio("temp_audio.wav")

        st.subheader("🔍 Sound Detection")
        sound_result = detect_sound("temp_audio.wav")
        st.write(sound_result)

        st.subheader("🗣️ Speech-to-Text")
        text = transcribe_audio("temp_audio.wav")
        st.text_area("Transcribed Text", text)

        st.subheader("😊 Emotion Detection")
        emotion = detect_emotion(text)
        st.write(emotion)

        st.subheader("📣 Name Alert")
        full_name = st.session_state["name"]
        nickname = st.session_state["nickname"]
        alert = check_name(text, [full_name, nickname])
        st.write(alert)
else:
    st.warning("Please login to use the app.")
