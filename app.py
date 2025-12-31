import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from dateutil.parser import parse

# -----------------------------
# Load models and data
# -----------------------------
cycle_model = joblib.load("next_period_model.pkl")
phase_model = joblib.load("cycle_phase_model.pkl")
recommendations_df = pd.read_csv("Recommendations.csv")  # Your recommendations table

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="BLOOMLY", page_icon="🌸", layout="centered")

# -----------------------------
# Splash screen
# -----------------------------
st.markdown(
    """
    <div style="text-align:center; background-color:#FFE4E1; padding:40px; border-radius:20px;">
        <img src='logo.png' width='150' style="background-color:#FFE4E1; border-radius:15px;">
        <h1 style="font-family:sans-serif; color:#C71585;">BLOOMLY</h1>
        <h3 style="font-family:sans-serif; color:#FF69B4;">Grow with Confidence</h3>
    </div>
    """, unsafe_allow_html=True
)

st.markdown("---")

# -----------------------------
# Login section (mock)
# -----------------------------
st.subheader("Login")
login_method = st.radio("Continue with", ["Google", "Microsoft", "Email"])
if login_method == "Email":
    email = st.text_input("Enter your email")
    password = st.text_input("Enter your password", type="password")

st.markdown("---")

# -----------------------------
# Period tracking inputs
# -----------------------------
st.subheader("Period Tracker")
st.markdown("Enter your previous period start dates (YYYY-MM-DD). You can enter multiple dates:")

period_dates_input = st.text_area("Previous Period Dates (one per line)")
period_dates = []
for date_str in period_dates_input.split("\n"):
    try:
        period_dates.append(parse(date_str.strip()))
    except:
        continue

pms_symptoms = st.text_input("Current PMS symptoms (comma separated, or 'None')")

# -----------------------------
# Mood survey
# -----------------------------
st.subheader("How are you feeling today?")
mood = st.radio("Select your mood:", ["Great", "Good", "Okay", "Bad", "Not great"])

st.markdown("---")

# -----------------------------
# Predict next period & phase
# -----------------------------
if st.button("Predict My Cycle"):

    if len(period_dates) < 1:
        st.warning("Please enter at least one previous period date.")
    else:
        # Prepare input for model
        prev_cycle_length = [(period_dates[i] - period_dates[i-1]).days for i in range(1, len(period_dates))]
        if len(prev_cycle_length) == 0:
            prev_cycle_length = [28]  # default if only one date
        last_cycle_length = prev_cycle_length[-1]

        pms_label = 0 if pms_symptoms.strip().lower() in ["none", ""] else 1

        X_input = [[last_cycle_length, pms_label]]

        next_period_days = int(cycle_model.predict(X_input)[0])
        cycle_phase_encoded = int(phase_model.predict(X_input)[0])
        # Decode phase
        phase_classes = phase_model.classes_
        current_phase = phase_classes[cycle_phase_encoded]

        # Display results
        st.success(f"Next period expected in {next_period_days} days.")
        st.info(f"Current cycle phase: {current_phase}")

        # Show recommendations
        recs = recommendations_df[
            (recommendations_df['phase'] == current_phase) &
            (recommendations_df['mood'] == mood)
        ]
        if not recs.empty:
            st.subheader("Recommendations")
            for i, row in recs.iterrows():
                st.write(f"- {row['recommendation']}")
        else:
            st.info("No specific recommendations found for your phase and mood.")

st.markdown("---")

# -----------------------------
# Gamification
# -----------------------------
st.subheader("My Bloomly Stats 🌸")
st.write("Streak days: 12")
st.write("Coins earned: 45")
st.write("Gardens grown: 3")

st.markdown("---")

# -----------------------------
# Community feed
# -----------------------------
st.subheader("Community Feed 💬")
community_messages = [
    ("Aanya S.", "Does anyone else feel super tired a few days before their period even if they sleep enough?"),
    ("Riya K.", "I started tracking my cycle properly this month and wow… it actually explains so much 😭"),
    ("Mehak J.", "Low mood today for no reason. Glad this space exists honestly."),
    ("Sara M.", "Is bloating before periods normal every single month? I feel like it’s getting worse."),
    ("Ishita P.", "Anyone else get random cravings + mood swings at the same time??"),
    ("Naina P.", "Just wanted to say this app makes me feel less alone. Thank you 🩷"),
]

for name, msg in community_messages:
    st.write(f"**{name}**: {msg}")
