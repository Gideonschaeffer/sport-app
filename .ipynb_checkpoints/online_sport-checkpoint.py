import pandas as pd
import streamlit as st
import os

# ---------------- PAGINA ----------------
st.set_page_config(page_title="Sport App", layout="centered")

# ---------------- BESTANDEN ----------------
USERS_FILE = "users.csv"
PROGRESS_FILE = "progress.csv"
TRAJECT_MAP = "trajecten"

# ---------------- TRAJECTEN ----------------
traject_bestanden = {
    "sport 1": "sport_schema.xlsx",
    "sport 2": "sport_schema_2.xlsx",
}

# ---------------- USERS ----------------
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["naam", "password"]).to_csv(USERS_FILE, index=False)

users_df = pd.read_csv(USERS_FILE)

# ---------------- PROGRESS ----------------
if not os.path.exists(PROGRESS_FILE):
    pd.DataFrame(columns=["username", "traject", "dag", "cardio", "kracht"]).to_csv(PROGRESS_FILE, index=False)

progress_df = pd.read_csv(PROGRESS_FILE)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.traject = "sport_schema"

# ---------------- REGISTRATIE ----------------
with st.expander("➕ Account aanmaken"):
    new_name = st.text_input("Naam")
    new_pass = st.text_input("Wachtwoord", type="password")

    if st.button("Registreren"):
        if new_name in users_df["naam"].values:
            st.error("Naam bestaat al")
        else:
            users_df.loc[len(users_df)] = [new_name, new_pass]
            users_df.to_csv(USERS_FILE, index=False)
            st.success("Account aangemaakt!")

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.subheader("Inloggen")
    naam = st.text_input("Naam", key="login_name")
    wachtwoord = st.text_input("Wachtwoord", type="password")

    if st.button("Login"):
        if naam in users_df["naam"].values:
            correct = users_df.loc[users_df["naam"] == naam, "password"].iloc[0]
            if wachtwoord == correct:
                st.session_state.logged_in = True
                st.session_state.username = naam
            else:
                st.error("Fout wachtwoord")
        else:
            st.error("Onbekende gebruiker")

# ---------------- APP ----------------
if st.session_state.logged_in:

    username = st.session_state.username

    # --------- SIDEBAR ---------
    st.sidebar.subheader("🏁 Sporttraject")
    st.session_state.traject = st.sidebar.selectbox(
        "Kies traject",
        list(traject_bestanden.keys())
    )

    cardio_color = st.sidebar.color_picker("Cardio kleur", "#FF5733")
    kracht_color = st.sidebar.color_picker("Kracht kleur", "#337BFF")

    # --------- TRAJECT LADEN ---------
    traject_file = os.path.join(TRAJECT_MAP, traject_bestanden[st.session_state.traject])
    df = pd.read_excel(traject_file)

    # --------- PROGRESS INIT ---------
    if not ((progress_df["username"] == username) & (progress_df["traject"] == st.session_state.traject)).any():
        rows = [
            {"username": username, "traject": st.session_state.traject, "dag": d, "cardio": 0, "kracht": 0}
            for d in df["dag"]
        ]
        progress_df = pd.concat([progress_df, pd.DataFrame(rows)])
        progress_df.to_csv(PROGRESS_FILE, index=False)

    user_df = progress_df[
        (progress_df["username"] == username) &
        (progress_df["traject"] == st.session_state.traject)
    ]

    # --------- STREAK ---------
    streak = 0
    prev_ok = False

    for _, row in user_df.sort_values("dag").iterrows():
        oef = df[df["dag"] == row["dag"]].iloc[0]
        is_rust = str(oef["wat te doen"]).lower() == "rust"
        done = row["cardio"] == 1 or row["kracht"] == 1

        if done or is_rust:
            streak = streak + 1 if prev_ok else 1
            prev_ok = True
        else:
            prev_ok = False

    st.metric("🔥 Streak", f"{streak} dagen")

    # --------- BADGES ---------
    if streak >= 10:
        st.success("🥇 Gouden streak!")
    elif streak >= 7:
        st.info("🥈 Zilveren streak!")
    elif streak >= 5:
        st.warning("🥉 Bronzen streak!")

    # --------- MOTIVATIE ---------
    if streak >= 10:
        st.success("👑 Jij bent niet te stoppen.")
    elif streak >= 5:
        st.info("🔥 Discipline level hoog!")
    elif streak >= 3:
        st.write("💪 Lekker bezig!")
    else:
        st.write("🚀 Begin je streak!")

    # --------- DAG ---------
    dag = st.selectbox("Selecteer dag", df["dag"])
    oef = df[df["dag"] == dag].iloc[0]

    st.write(f"**Wat te doen:** {oef['wat te doen']}")

    row_idx = user_df[user_df["dag"] == dag].index[0]

    # --------- CARDIO ---------
    if isinstance(oef["cardio"], str) and oef["cardio"].startswith("http"):
        st.subheader("🏃‍♂️ Cardio")
        if st.button("Cardio gedaan"):
            progress_df.loc[row_idx, "cardio"] = 1
            progress_df.to_csv(PROGRESS_FILE, index=False)
        st.link_button("Open cardio video", oef["cardio"])
        st.video(oef["cardio"])

    # --------- KRACHT ---------
    if isinstance(oef["kracht"], str) and oef["kracht"].startswith("http"):
        st.subheader("🏋️‍♂️ Kracht")
        if st.button("Kracht gedaan"):
            progress_df.loc[row_idx, "kracht"] = 1
            progress_df.to_csv(PROGRESS_FILE, index=False)
        st.link_button("Open kracht video", oef["kracht"])
        st.video(oef["kracht"])
