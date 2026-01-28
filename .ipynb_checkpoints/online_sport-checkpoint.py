import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Sport App", layout="centered")

USERS_FILE = "users.csv"
PROGRESS_FILE = "progress.csv"

TRAJECTEN = {
    "Schema 1": "sport_schema.xlsx",
    "Schema 2": "sport_schema_2.xlsx"
}

# ---------------- HELPERS ----------------
def load_csv(path, columns):
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_csv(path, index=False)
    return pd.read_csv(path)

def save_csv(df, path):
    df.to_csv(path, index=False)

# ---------------- LOAD DATA ----------------
users_df = load_csv(USERS_FILE, ["naam", "password"])
progress_df = load_csv(PROGRESS_FILE, ["username", "traject", "dag", "done", "date"])

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "traject" not in st.session_state:
    st.session_state.traject = list(TRAJECTEN.keys())[0]

# ---------------- LOGIN / REGISTER ----------------
if not st.session_state.logged_in:
    st.title("🏋️ Sport App")

    tab1, tab2 = st.tabs(["Inloggen", "Account maken"])

    with tab1:
        naam = st.text_input("Naam")
        pw = st.text_input("Wachtwoord", type="password")

        if st.button("Inloggen"):
            match = users_df[
                (users_df["naam"] == naam) &
                (users_df["password"] == pw)
            ]
            if not match.empty:
                st.session_state.logged_in = True
                st.session_state.user = naam
                st.success("Welkom terug! 💪")
            else:
                st.error("Onjuiste gegevens")

    with tab2:
        new_name = st.text_input("Nieuwe naam")
        new_pw = st.text_input("Nieuw wachtwoord", type="password")

        if st.button("Account maken"):
            if new_name in users_df["naam"].values:
                st.error("Naam bestaat al")
            else:
                users_df.loc[len(users_df)] = [new_name, new_pw]
                save_csv(users_df, USERS_FILE)
                st.success("Account aangemaakt 🎉")

    st.stop()

# ---------------- APP ----------------
username = st.session_state.user
st.sidebar.title(f"👋 {username}")

st.sidebar.subheader("🏁 Sport traject")
st.session_state.traject = st.sidebar.selectbox(
    "Kies schema",
    list(TRAJECTEN.keys())
)

# ---------------- LOAD SCHEMA ----------------
schema_file = TRAJECTEN[st.session_state.traject]
df = pd.read_excel(schema_file)

# ---------------- INIT PROGRESS ----------------
if not (
    (progress_df["username"] == username) &
    (progress_df["traject"] == st.session_state.traject)
).any():

    new_rows = pd.DataFrame([
        {
            "username": username,
            "traject": st.session_state.traject,
            "dag": dag,
            "done": 0,
            "date": ""
        }
        for dag in df["dag"]
    ])

    progress_df = pd.concat([progress_df, new_rows], ignore_index=True)
    save_csv(progress_df, PROGRESS_FILE)

# ---------------- STREAK ----------------
user_prog = progress_df[
    (progress_df["username"] == username) &
    (progress_df["traject"] == st.session_state.traject)
]

dates = sorted([
    datetime.strptime(d, "%Y-%m-%d")
    for d in user_prog["date"]
    if d
])

streak = 0
if dates:
    streak = 1
    for i in range(len(dates)-1, 0, -1):
        if (dates[i] - dates[i-1]).days <= 1:
            streak += 1
        else:
            break

# ---------------- BADGES ----------------
badges = []
if streak >= 5:
    badges.append("🥉 5-dagen streak")
if streak >= 10:
    badges.append("🥈 10-dagen streak")
if streak >= 20:
    badges.append("🥇 20-dagen streak")

# ---------------- HEADER ----------------
st.title("🔥 Jouw sportdag")
st.metric("🔥 Streak", f"{streak} dagen")

if badges:
    st.success("🏆 Badges: " + " | ".join(badges))

# ---------------- DAG SELECT ----------------
dag = st.selectbox("Selecteer dag", df["dag"])
oef = df[df["dag"] == dag].iloc[0]

row_idx = progress_df[
    (progress_df["username"] == username) &
    (progress_df["traject"] == st.session_state.traject) &
    (progress_df["dag"] == dag)
].index[0]

# ---------------- CONTENT ----------------
st.subheader(oef["wat te doen"])

# VIDEO EMBEDS
if pd.notna(oef.get("cardio")) and oef["cardio"]:
    st.markdown("### 🏃 Cardio")
    st.video(oef["cardio"])

if pd.notna(oef.get("kracht")) and oef["kracht"]:
    st.markdown("### 💪 Kracht")
    st.video(oef["kracht"])

# ---------------- RUSTDAG ----------------
if oef.get("rust", False):
    st.info("😴 Rustdag — telt mee voor je streak!")

# ---------------- AFVINKEN ----------------
if progress_df.loc[row_idx, "done"] == 0:
    if st.button("✅ Dag afronden"):
        progress_df.loc[row_idx, "done"] = 1
        progress_df.loc[row_idx, "date"] = datetime.now().strftime("%Y-%m-%d")
        save_csv(progress_df, PROGRESS_FILE)
        st.success("Goed bezig! 🔥")
else:
    st.success("Deze dag is afgerond 🎉")

# ---------------- STATISTIEKEN ----------------
st.divider()
completed = user_prog["done"].sum()
total = len(user_prog)

st.progress(completed / total)
st.write(f"📊 {completed} van {total} dagen voltooid")

# ---------------- MOTIVATIE ----------------
quotes = [
    "Elke dag telt 💪",
    "Rust is ook training 😴",
    "Je bent verder dan gisteren 🔥",
    "Consistency beats motivation 🏆"
]
st.info(quotes[streak % len(quotes)])
