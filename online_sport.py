import streamlit as st
import pandas as pd
import os
import random

# ================== PAGINA ==================
st.set_page_config(
    page_title="Sport App",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================== BESTANDEN ==================
USERS_FILE = "users.csv"
PROGRESS_FILE = "progress.csv"
SPORT_FILE = "sport_schema.xlsx"

# ================== DATA ==================
df = pd.read_excel(SPORT_FILE)

# ================== USERS ==================
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["naam", "password"]).to_csv(USERS_FILE, index=False)

users_df = pd.read_csv(USERS_FILE)

# ================== PROGRESS ==================
if not os.path.exists(PROGRESS_FILE):
    pd.DataFrame(columns=["username", "dag", "done"]).to_csv(PROGRESS_FILE, index=False)

progress_df = pd.read_csv(PROGRESS_FILE)

# ================== SESSION ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# ================== MOTIVATIE ==================
MOTIVATION = [
    "🔥 Jij bent sterker dan je denkt",
    "💪 Elke dag telt",
    "🏆 Discipline > motivatie",
    "🚀 Blijf doorgaan!",
    "👊 Vandaag weer een stap vooruit"
]

# ================== LOGIN / REGISTRATIE ==================
st.title("🏋️‍♂️ Sport App")

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Inloggen", "🆕 Registreren"])

    with tab1:
        name = st.text_input("Naam")
        password = st.text_input("Wachtwoord", type="password")

        if st.button("Inloggen"):
            if name in users_df["naam"].values:
                correct = users_df.loc[users_df["naam"] == name, "password"].iloc[0]
                if password == correct:
                    st.session_state.logged_in = True
                    st.session_state.username = name
                    st.rerun()
                else:
                    st.error("❌ Verkeerd wachtwoord")
            else:
                st.error("❌ Gebruiker bestaat niet")

    with tab2:
        new_name = st.text_input("Nieuwe naam")
        new_pass = st.text_input("Nieuw wachtwoord", type="password")

        if st.button("Account aanmaken"):
            if new_name in users_df["naam"].values:
                st.error("❌ Naam bestaat al")
            else:
                users_df.loc[len(users_df)] = [new_name, new_pass]
                users_df.to_csv(USERS_FILE, index=False)
                st.success("✅ Account aangemaakt")

    st.stop()

# ================== GEBRUIKER ==================
username = st.session_state.username

# Nieuwe gebruiker → schema aanmaken
if username not in progress_df["username"].values:
    rows = [{"username": username, "dag": d, "done": 0} for d in df["dag"]]
    progress_df = pd.concat([progress_df, pd.DataFrame(rows)], ignore_index=True)
    progress_df.to_csv(PROGRESS_FILE, index=False)

user_progress = progress_df[progress_df["username"] == username]

# ================== KLEUREN ==================
st.sidebar.subheader("🎨 Jouw stijl")
main_color = st.sidebar.color_picker("Hoofdkleur", "#ff4b4b")

# ================== STATISTIEKEN ==================
completed = user_progress[user_progress["done"] == 1]["dag"].nunique()
total = df["dag"].nunique()

st.progress(completed / total)
st.caption(f"✅ {completed} van {total} dagen voltooid")

# ================== STREAK ==================
sorted_days = user_progress.sort_values("dag")
streak = 0
for _, row in sorted_days.iterrows():
    if row["done"] == 1:
        streak += 1
    else:
        break

st.metric("🔥 Streak", f"{streak} dagen")

# ================== BADGES ==================
st.subheader("🏅 Badges")
badges = completed // 5
if badges == 0:
    st.info("Nog geen badges – blijf gaan 💪")
else:
    st.success(" ".join(["🏆"] * badges))

# ================== MOTIVATIE ==================
st.info(random.choice(MOTIVATION))

# ================== DAG SELECTIE ==================
st.subheader("📅 Kies je dag")
dag = st.selectbox("Dag", df["dag"])
oef = df[df["dag"] == dag].iloc[0]

done = user_progress[user_progress["dag"] == dag]["done"].iloc[0]

# ================== DAG KAART ==================
st.markdown(
    f"""
    <div style="
        padding:20px;
        border-radius:15px;
        background:{main_color};
        color:white;
        text-align:center;
    ">
        <h3>Dag {dag}</h3>
        <p><b>{oef['wat te doen']}</b></p>
    </div>
    """,
    unsafe_allow_html=True
)

# ================== DAG AFRONDEN ==================
if not done:
    if st.button("✅ Dag afronden"):
        progress_df.loc[
            (progress_df["username"] == username) &
            (progress_df["dag"] == dag),
            "done"
        ] = 1
        progress_df.to_csv(PROGRESS_FILE, index=False)
        st.rerun()
else:
    st.success("🎉 Deze dag is voltooid!")

st.divider()

# ================= CARDIO =================
st.subheader("🏃‍♂️ Cardio")

if isinstance(oef["cardio"], str) and oef["cardio"].startswith("http"):
    st.link_button(
        "▶️ Open cardio video",
        oef["cardio"]
    )
    st.video(oef["cardio"])
else:
    st.info("Geen cardio video voor deze dag")

# ================= KRACHT =================
st.subheader("🏋️‍♂️ Kracht")

if isinstance(oef["kracht"], str) and oef["kracht"].startswith("http"):
    st.link_button(
        "▶️ Open kracht video",
        oef["kracht"]
    )
    st.video(oef["kracht"])
else:
    st.info("Geen kracht video voor deze dag")


# ================== FOOTER ==================
st.caption("📱 Mobielvriendelijk • Streaks • Motivatie • Professioneel")
