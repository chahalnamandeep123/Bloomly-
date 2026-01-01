import streamlit as st
import pandas as pd
import joblib
from datetime import datetime

# -------------------------------
# Load Models & Recommendations
# -------------------------------
cycle_model = joblib.load("next_period_model.pkl")
phase_model = joblib.load("cycle_phase_model.pkl")
recommendations_df = pd.read_csv("Recommendations.csv", encoding="ISO-8859-1", engine="python")

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Bloomly", layout="centered")

# -------------------------------
# Session State for Multi-Step Flow
# -------------------------------
if "step" not in st.session_state:
    st.session_state.step = "splash"
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "period_dates" not in st.session_state:
    st.session_state.period_dates = []
if "typical_length" not in st.session_state:
    st.session_state.typical_length = 5
if "avg_cycle" not in st.session_state:
    st.session_state.avg_cycle = 28
if "pms_symptoms" not in st.session_state:
    st.session_state.pms_symptoms = []
if "mood" not in st.session_state:
    st.session_state.mood = "Good"
if "prediction_done" not in st.session_state:
    st.session_state.prediction_done = False
if "next_period_days" not in st.session_state:
    st.session_state.next_period_days = None
if "current_phase" not in st.session_state:
    st.session_state.current_phase = None

# -------------------------------
# Custom CSS for Feminine UI
# -------------------------------
st.markdown("""
<style>
body, .stApp {
    background-color: #fff0f5;
    color: #4b004b;
    font-family: 'Segoe UI', sans-serif;
}

.logo-wrapper {
    background-color: #fff0f5;
    display: inline-block;
    padding: 14px;
    border-radius: 50%;
    box-shadow: 0px 6px 12px rgba(255, 182, 193, 0.3);
    margin-bottom: 10px;
}

.logo-wrapper img {
    display: block;
    border-radius: 50%;
}

.title-fade {
    font-size: 50px;
    font-weight: bold;
    color: #d63384;
    margin-bottom: 0px;
}

.slogan-fade {
    font-size: 22px;
    color: #ff66b2;
    font-style: italic;
    margin-top: 0px;
}

.stButton>button {
    background-color: #ff99cc;
    color: white;
    border-radius: 20px;
    padding: 12px 28px;
    font-weight: 700;
    font-size: 16px;
    transition: all 0.3s ease;
    box-shadow: 0px 4px 10px rgba(255, 182, 193, 0.3);
}
.stButton>button:hover {
    background-color: #ff66b2;
    transform: scale(1.05);
}

.community-msg {
    background-color: #ffe6f2;
    padding: 10px;
    border-radius: 12px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# SPLASH SCREEN
# -------------------------------
if st.session_state.step == "splash":
    st.markdown(
        '<div style="text-align:center;">'
        '<div class="logo-wrapper">'
        '<img src="logo.png" width="180">'
        '</div></div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="title-fade" style="text-align:center;">Bloomly</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan-fade" style="text-align:center;">Grow with Confidence</div>', unsafe_allow_html=True)
    
    if st.button("Continue"):
        st.session_state.step = "login"
    st.stop()

# -------------------------------
# LOGIN SCREEN
# -------------------------------
if st.session_state.step == "login":
    st.subheader("Login / Sign Up")
    login_option = st.radio("Continue with:", ["Google", "Microsoft", "Email"], index=0)

    if login_option == "Email":
        email = st.text_input("Enter your email:")
        password = st.text_input("Enter your password:", type="password")
        if st.button("Sign In / Sign Up"):
            if email:
                st.session_state.user_email = email
                st.session_state.step = "cycle_input"
            else:
                st.error("Please enter your email.")
    else:
        if st.button(f"Continue with {login_option}"):
            st.session_state.user_email = f"{login_option}_user"
            st.session_state.step = "cycle_input"
    st.stop()

# -------------------------------
# CYCLE INPUT SCREEN
# -------------------------------
if st.session_state.step == "cycle_input":
    st.subheader("Your Cycle Information")

    # Calendar input for previous periods
    period_dates = st.date_input(
        "Select your previous period start dates",
        [],
        help="Select multiple dates corresponding to the start of your periods"
    )
    st.session_state.period_dates = [d.strftime("%Y-%m-%d") for d in period_dates]

    # Typical period length
    st.session_state.typical_length = st.number_input(
        "How long are your periods typically? (days)",
        min_value=1, max_value=10, value=st.session_state.typical_length
    )

    # Average cycle length
    st.session_state.avg_cycle = st.number_input(
        "Average cycle length (days)",
        min_value=20, max_value=40, value=st.session_state.avg_cycle
    )

    if st.button("Next"):
        if len(st.session_state.period_dates) == 0:
            st.error("Please select at least one period date.")
        else:
            st.session_state.step = "pms_mood"
    st.stop()

# -------------------------------
# PMS SYMPTOMS + MOOD SCREEN
# -------------------------------
if st.session_state.step == "pms_mood":
    st.subheader("PMS Symptoms")
    st.session_state.pms_symptoms = st.multiselect(
        "Select current PMS symptoms (or 'None')",
        ["Cramps", "Bloating", "Fatigue", "Anxiety", "Cravings", "None"]
    )

    # Mood survey with circular face emojis
    st.subheader("How are you feeling today?")
    mood_options = {
        "😄 Great": "Great",        # grinning face
        "🙂 Good": "Good",          # slightly smiling face
        "😐 Okay": "Okay",          # neutral face
        "😕 Not Great": "Not Great", # confused/slightly frowning
        "☹️ Bad": "Bad"             # frowning face
    }
    selected_mood = st.radio(
        "Select your mood:",
        list(mood_options.keys()),
        index=1
    )
    st.session_state.mood = mood_options[selected_mood]

    if st.button("Get Predictions"):
        st.session_state.step = "results"
    st.stop()

# -------------------------------
# RESULTS + RECOMMENDATIONS
# -------------------------------
if st.session_state.step == "results":
    try:
        if len(st.session_state.period_dates) > 1:
            prev_cycle_length = (datetime.strptime(st.session_state.period_dates[-1], "%Y-%m-%d") -
                                 datetime.strptime(st.session_state.period_dates[-2], "%Y-%m-%d")).days
        else:
            prev_cycle_length = st.session_state.avg_cycle

        pms_label = 0 if "None" in st.session_state.pms_symptoms or len(st.session_state.pms_symptoms) == 0 else 1
        X_input = [[prev_cycle_length, pms_label]]

        # Model predictions
        st.session_state.next_period_days = cycle_model.predict(X_input)[0]
        st.session_state.current_phase = phase_model.predict(X_input)[0]

        st.success(f"Your next period is expected in ~{round(st.session_state.next_period_days)} days.")
        st.info(f"Current cycle phase: **{st.session_state.current_phase}**")

        # Recommendations from CSV
        recs = recommendations_df[
            (recommendations_df["Phase"] == st.session_state.current_phase) &
            (recommendations_df["Mood"] == st.session_state.mood)
        ]
        if not recs.empty:
            st.subheader("Personalized Recommendations")
            for _, row in recs.iterrows():
                st.markdown(f"- **{row['Category']}**: {row['Recommendation']}")
        else:
            st.info("No specific recommendations available for this combination.")

    except Exception as e:
        st.error("Prediction failed. Please check your inputs.")
        st.caption(str(e))

    # -------------------------------
    # Gamification & Community Feed
    # -------------------------------
    st.markdown("---")
    st.subheader("Your Bloomly Progress")
    st.write("🌸 Streak: 12 days  |  💎 Coins: 35  |  🌿 Gardens Grown: 5")

    st.subheader("Community Feed")
    community_messages = [
        {"name": "Loki", "msg": "Completed my streak today 😄"},
        {"name": "Mia", "msg": "These recommendations really help 💖"},
        {"name": "Sofia", "msg": "Feeling calmer already 🙂"},
        {"name": "Rina", "msg": "My garden just grew another flower 🌷"},
        {"name": "Arya", "msg": "Bloomly makes tracking feel gentle 🌸"}
    ]
    for msg in community_messages:
        st.markdown(f'<div class="community-msg"><b>{msg["name"]}</b>: {msg["msg"]}</div>', unsafe_allow_html=True)

