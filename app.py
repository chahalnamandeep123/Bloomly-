import pandas as pd
import joblib
import streamlit as st
from datetime import datetime

# -------------------------------
# LOAD MODELS
# -------------------------------
cycle_model = joblib.load("next_period_model.pkl")
phase_model = joblib.load("cycle_phase_model.pkl")

# -------------------------------
# LOAD RECOMMENDATIONS
# -------------------------------
recommendations_df = pd.read_csv(
    "Recommendations.csv",
    encoding="ISO-8859-1",
    engine="python"
)

# -------------------------------
# Custom CSS for feminine UI
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
    padding: 12px;
    border-radius: 24px;
}

.logo-wrapper img {
    display: block;
    border-radius: 50%;
}

.title-fade {
    font-size: 42px;
    font-weight: bold;
    color: #d63384;
}

.slogan-fade {
    font-size: 20px;
    color: #ff66b2;
    font-style: italic;
}

.stButton>button {
    background-color: #ff99cc;
    color: white;
    border-radius: 12px;
    padding: 8px 18px;
    font-weight: 600;
}

.stButton>button:hover {
    background-color: #ff66b2;
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
# Branding / Logo
# -------------------------------
st.markdown(
    '<div style="text-align:center;">'
    '<div class="logo-wrapper">'
    '<img src="logo.png" width="140">'
    '</div></div>',
    unsafe_allow_html=True
)
st.markdown('<div class="title-fade" style="text-align:center;">Bloomly</div>', unsafe_allow_html=True)
st.markdown('<div class="slogan-fade" style="text-align:center;">Grow with Confidence</div>', unsafe_allow_html=True)
st.caption("Demo prototype · No personal data is stored")
st.markdown("---")

# -------------------------------
# Login (Mock)
# -------------------------------
st.subheader("Login")
login_option = st.radio("Continue with:", ["Google", "Microsoft", "Email"])

if login_option == "Email":
    st.text_input("Email")
    st.text_input("Password", type="password")

st.markdown("---")

# -------------------------------
# User Inputs
# -------------------------------
st.subheader("Cycle History")
period_text = st.text_area(
    "Enter previous period start dates (comma-separated, YYYY-MM-DD)",
    placeholder="2025-12-01, 2025-12-28"
)

period_dates = [d.strip() for d in period_text.split(",") if d.strip()]

st.subheader("PMS Symptoms")
pms_symptoms = st.multiselect(
    "Select symptoms (or choose none)",
    ["Cramps", "Bloating", "Fatigue", "Anxiety", "Cravings", "None"]
)

# -------------------------------
# Mood Survey
# -------------------------------
st.subheader("How are you feeling today?")
mood = st.radio("Select your mood:", ["Great", "Good", "Okay", "Not Great", "Bad"])

# -------------------------------
# Predictions
# -------------------------------
if st.button("Get Predictions"):
    if len(period_dates) == 0:
        st.error("Please enter at least one previous period date.")
    else:
        try:
            # Calculate previous cycle length
            if len(period_dates) > 1:
                prev_cycle_length = (
                    datetime.strptime(period_dates[-1], "%Y-%m-%d")
                    - datetime.strptime(period_dates[-2], "%Y-%m-%d")
                ).days
            else:
                prev_cycle_length = 28

            # PMS label
            pms_label = 0 if "None" in pms_symptoms or len(pms_symptoms) == 0 else 1
            X_input = [[prev_cycle_length, pms_label]]

            # Predict next period and current phase
            next_period_days = cycle_model.predict(X_input)[0]
            current_phase = phase_model.predict(X_input)[0]

            st.success(f"Your next period is expected in ~{round(next_period_days)} days.")
            st.info(f"Current cycle phase: **{current_phase}**")

            # -------------------------------
            # Recommendations (Phase + Mood)
            # -------------------------------
            recs = recommendations_df[
                (recommendations_df["Phase"] == current_phase) &
                (recommendations_df["Mood"] == mood)
            ]

            if not recs.empty:
                st.subheader("Personalized Recommendations")
                for _, row in recs.iterrows():
                    st.markdown(f"- **{row['Category']}**: {row['Recommendation']}")
            else:
                st.info("No specific recommendations available for this combination.")

        except Exception as e:
            st.error("Something went wrong. Please check your inputs.")
            st.caption(str(e))

# -------------------------------
# Gamification & Community
# -------------------------------
st.markdown("---")
st.subheader("Your Bloomly Progress")
st.write("🌸 Streak: 12 days | 💎 Coins: 35 | 🌿 Gardens Grown: 5")

st.subheader("Community Feed")
community_messages = [
    {"name": "Loki", "msg": "Completed my streak today 🌸"},
    {"name": "Mia", "msg": "These recommendations really help 💖"},
    {"name": "Sofia", "msg": "Feeling calmer already."},
    {"name": "Rina", "msg": "My garden just grew another flower 🌷"},
    {"name": "Arya", "msg": "Bloomly makes tracking feel gentle."}
]

for msg in community_messages:
    st.markdown(
        f'<div class="community-msg"><b>{msg["name"]}</b>: {msg["msg"]}</div>',
        unsafe_allow_html=True
    )


