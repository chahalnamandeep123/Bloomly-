

import pandas as pd
import joblib
import streamlit as st

# -------------------------------
# LOAD MODELS
# -------------------------------
cycle_model = joblib.load("next_period_model.pkl")
phase_model = joblib.load("cycle_phase_model.pkl")

# -------------------------------
# LOAD RECOMMENDATIONS
# -------------------------------
# Fixed encoding issue
recommendations_df = pd.read_csv("Recommendations.csv", encoding="ISO-8859-1", engine="python")

# -------------------------------
# Custom CSS for cute feminine UI
# -------------------------------
st.markdown("""
<style>
/* Page background */
body, .stApp {
    background-color: #fff0f5;  /* soft lavender */
    color: #4b004b;
    font-family: 'Comic Sans MS', cursive, sans-serif;
}

/* Logo and titles */
.logo-fade img {
    border-radius: 50%;
    box-shadow: 0px 4px 10px rgba(255, 182, 193, 0.5);
}
.title-fade {
    font-size: 48px;
    font-weight: bold;
    color: #d63384;
}
.slogan-fade {
    font-size: 22px;
    color: #ff66b2;
    font-style: italic;
}

/* Input boxes */
.css-1aumxhk, .stTextInput>div>input {
    border-radius: 15px;
    padding: 10px;
    border: 2px solid #ffb6c1;
    background-color: #fff0f5;
}

/* Buttons */
.stButton>button {
    background-color: #ff99cc;
    color: white;
    border-radius: 15px;
    padding: 8px 20px;
    font-weight: bold;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #ff66b2;
}

/* Community feed */
.community-msg {
    background-color: #ffe6f2;
    padding: 10px;
    border-radius: 15px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Splash / Logo with Fade-in
# -------------------------------
st.markdown('<div class="logo-fade" style="text-align:center;"><img src="Logo.png" width="150"></div>', unsafe_allow_html=True)
st.markdown('<div class="title-fade" style="text-align:center;">BLOOMLY</div>', unsafe_allow_html=True)
st.markdown('<div class="slogan-fade" style="text-align:center;">Grow with Confidence</div>', unsafe_allow_html=True)
st.markdown("---")

# -------------------------------
# Login (mock)
# -------------------------------
st.subheader("Login")
login_option = st.radio("Continue with:", ["Google", "Microsoft", "Email"])
email = ""
if login_option == "Email":
    email = st.text_input("Enter your email:")

st.markdown("---")

# -------------------------------
# User period inputs
# -------------------------------
st.subheader("Enter your previous period dates")
period_dates = st.text_area("Enter dates separated by commas (YYYY-MM-DD)", placeholder="2025-12-01,2025-12-28,...")
period_dates = [d.strip() for d in period_dates.split(",") if d.strip()]
st.subheader("PMS Symptoms")
pms_symptoms = st.text_input("Enter current PMS symptoms (or 'None'):")

# -------------------------------
# Mood Survey
# -------------------------------
st.subheader("How are you feeling today?")
mood = st.radio("Select your mood:", ["Great", "Good", "Okay", "Bad", "Not Great"])

# -------------------------------
# Predictions
# -------------------------------
if st.button("Get Predictions"):
    if len(period_dates) < 1:
        st.error("Please enter at least one previous period date.")
    else:
        # Prepare input features
        prev_cycle_length = None
        if len(period_dates) > 1:
            prev_cycle_length = (datetime.strptime(period_dates[-1], "%Y-%m-%d") -
                                 datetime.strptime(period_dates[-2], "%Y-%m-%d")).days
        else:
            prev_cycle_length = 28  # default if only one period

        pms_label = 0 if pms_symptoms.lower() in ["none", ""] else 1
        X_input = [[prev_cycle_length, pms_label]]

        # Predictions
        next_period = cycle_model.predict(X_input)[0]
        cycle_phase_encoded = phase_model.predict(X_input)[0]
        # Decode phase
        phase_classes = phase_model.classes_
        current_phase = phase_classes[cycle_phase_encoded]

        st.success(f"Your next period is expected in {round(next_period)} days.")
        st.info(f"Current cycle phase: {current_phase}")

        # Recommendations from CSV
        recs = recommendations_df[recommendations_df['Phase'] == current_phase]
        if len(recs) > 0:
            st.subheader("Recommendations for you:")
            for idx, row in recs.iterrows():
                st.markdown(f"- **{row['Category']}**: {row['Recommendation']}")
        else:
            st.info("No recommendations available for this phase.")

# -------------------------------
# Gamification / Community feed
# -------------------------------
st.markdown("---")
st.subheader("Your Bloomly Progress")
st.write("🌸 Total Streak: 12 days | 💎 Coins: 35 | 🌿 Gardens Grown: 5")

st.subheader("Community Feed")
community_messages = [
    {"name": "Loki", "msg": "Just completed my streak! Feeling amazing 🌸"},
    {"name": "Mia", "msg": "Loving these recommendations, thanks Bloomly! 💖"},
    {"name": "Sofia", "msg": "Can't wait to try the new meditation tip."},
    {"name": "Rina", "msg": "My garden just grew another flower! 🌷"},
    {"name": "Arya", "msg": "This app is so calming and helpful."},
    {"name": "Leila", "msg": "Feeling great today, thanks to the mood tips! 🌼"}
]
for m in community_messages:
    st.markdown(f'<div class="community-msg"><b>{m["name"]}</b>: {m["msg"]}</div>', unsafe_allow_html=True)

