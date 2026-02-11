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
def load_or_create_csv(path, required_columns):
    if not os.path.exists(path):
        df = pd.DataFrame(columns=required_columns)
        df.to_csv(path, index=False)
        return df

    df = pd.read_csv(path)

    # 🔧 MIGRATIE: voeg ontbrekende kolommen toe
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    df = df[required_columns]
    df.to_csv(path, index=False)
    return df

# ---------------- LOAD DATA ----------------
users_df = load_or_create_csv(
    USERS_FILE,
    ["naam", "password"]
)

progress_df = load_or_create_csv(
    PROGRESS_FILE,
    ["username", "traject", "dag", "done", "date"]
)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""
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
                st.success("Welkom terug 💪")
                st.stop()
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
                users_df.to_csv(USERS_FILE, index=False)
                st.success("Account aangemaakt 🎉")

    st.stop()

# ---------------- APP ----------------
username = st.session_state.user
st.sidebar.title(f"👋 {username}")

st.sidebar.subheader("🏁 Sporttraject")
st.session_state.traject = st.sidebar.selectbox(
    "Kies schema",
    list(TRAJECTEN.keys())
)

# ---------------- LOAD SCHEMA ----------------
schema_file = TRAJECTEN[st.session_state.traject]
schema_df = pd.read_excel(schema_file)

# ---------------- INIT PROGRESS ----------------
mask = (
    (progress_df["username"] == username) &
    (progress_df["traject"] == st.session_state.traject)
)

if not mask.any():
    new_rows = pd.DataFrame({
        "username": username,
        "traject": st.session_state.traject,
        "dag": schema_df["dag"],
        "done": 0,
        "date": ""
    })
    progress_df = pd.concat([progress_df, new_rows], ignore_index=True)
    progress_df.to_csv(PROGRESS_FILE, index=False)

user_prog = progress_df[
    (progress_df["username"] == username) &
    (progress_df["traject"] == st.session_state.traject)
]

# ---------------- STREAK ----------------
dates = sorted([
    datetime.strptime(d, "%Y-%m-%d")
    for d in user_prog["date"]
    if isinstance(d, str) and d
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
if streak >= 5: badges.append("🥉 5 dagen")
if streak >= 10: badges.append("🥈 10 dagen")
if streak >= 20: badges.append("🥇 20 dagen")

# ---------------- UI ----------------
st.title("🔥 Vandaag")
st.metric("🔥 Streak", f"{streak} dagen")

if badges:
    st.success("🏆 Badges: " + " | ".join(badges))

dag = st.selectbox("Selecteer dag", schema_df["dag"])
oef = schema_df[schema_df["dag"] == dag].iloc[0]

row_idx = progress_df[
    (progress_df["username"] == username) &
    (progress_df["traject"] == st.session_state.traject) &
    (progress_df["dag"] == dag)
].index[0]

st.subheader(oef["wat te doen"])

# ---------------- VIDEO'S ----------------
if pd.notna(oef.get("cardio")) and oef["cardio"]:
    st.markdown("### 🏃 Cardio")
    st.video(oef["cardio"])

if pd.notna(oef.get("kracht")) and oef["kracht"]:
    st.markdown("### 💪 Kracht")
    st.video(oef["kracht"])

# ---------------- RUSTDAG ----------------
if oef.get("rust", False):
    st.info("😴 Rustdag — telt mee voor je streak")

# ---------------- AFVINKEN ----------------
if progress_df.loc[row_idx, "done"] == 0:
    if st.button("✅ Dag afronden"):
        progress_df.loc[row_idx, "done"] = 1
        progress_df.loc[row_idx, "date"] = datetime.now().strftime("%Y-%m-%d")
        progress_df.to_csv(PROGRESS_FILE, index=False)
        st.success("Top gedaan 🔥")
else:
    st.success("Dag voltooid 🎉")

# ---------------- STATISTIEKEN ----------------
st.divider()
completed = user_prog["done"].sum()
total = len(user_prog)

st.progress(completed / total)
st.write(f"📊 {completed} van {total} dagen afgerond")

# ---------------- MOTIVATIE ----------------
quotes = [
    "Consistency beats motivation 💪",
    "Rust is ook progress 😴",
    "Je bent sterker dan gisteren 🔥",
    "Gewoon doorgaan 🏆"
]
st.info(quotes[streak % len(quotes)])
