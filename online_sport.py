import pandas as pd
import streamlit as st
import os

# ---------------- PAGINA ----------------
st.set_page_config(page_title="Sport App", layout="centered")

# ---------------- BESTANDEN ----------------
USERS_FILE = "users.csv"
PROGRESS_FILE = "progress.csv"
SPORT_FILE = "sport_schema.xlsx"  # 12-dagen schema

# ---------------- DATA ----------------
df = pd.read_excel(SPORT_FILE)

# ---------------- USERS ----------------
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["naam", "password"]).to_csv(USERS_FILE, index=False)
users_df = pd.read_csv(USERS_FILE)
users_df.columns = [col.strip() for col in users_df.columns]

# ---------------- PROGRESS ----------------
if not os.path.exists(PROGRESS_FILE):
    pd.DataFrame(columns=["username", "dag", "cardio", "kracht"]).to_csv(PROGRESS_FILE, index=False)
progress_df = pd.read_csv(PROGRESS_FILE)
progress_df.columns = [col.strip() for col in progress_df.columns]

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# ---------------- FUNCTIES ----------------
def register_user(name, password):
    """Voeg een nieuwe gebruiker toe."""
    global users_df
    if not name or not password:
        st.warning("⚠️ Vul zowel naam als wachtwoord in")
        return
    if name in users_df["naam"].values:
        st.error("❌ Naam al in gebruik")
        return
    new_user = pd.DataFrame([{"naam": name, "password": password}])
    users_df = pd.concat([users_df, new_user], ignore_index=True)
    users_df.to_csv(USERS_FILE, index=False)
    st.success(f"✅ Account aangemaakt voor {name}!")

def login_user(name, password):
    """Log een bestaande gebruiker in."""
    if name not in users_df["naam"].values:
        st.error("❌ Onbekende gebruiker")
        return False
    correct_password = users_df.loc[users_df["naam"] == name, "password"].iloc[0]
    if password != correct_password:
        st.error("❌ Onjuist wachtwoord")
        return False
    st.session_state.logged_in = True
    st.session_state.username = name
    st.success(f"Welkom, {name} 🏋️‍♂️")
    st.experimental_rerun()
    return True

def initialize_progress(username):
    """Maak progressie aan voor een nieuwe gebruiker."""
    global progress_df
    if username not in progress_df["username"].values:
        new_rows = pd.DataFrame([{"username": username, "dag": dag, "cardio": 0, "kracht": 0} for dag in df["dag"].unique()])
        progress_df = pd.concat([progress_df, new_rows], ignore_index=True)
        progress_df.to_csv(PROGRESS_FILE, index=False)

def mark_done(username, dag, oefening):
    """Markeer Cardio of Kracht als voltooid."""
    global progress_df
    col = "cardio" if oefening == "cardio" else "kracht"
    idx = progress_df[(progress_df["username"] == username) & (progress_df["dag"] == dag)].index[0]
    progress_df.loc[idx, col] = 1
    progress_df.to_csv(PROGRESS_FILE, index=False)

def get_completed_days(username):
    """Tel het aantal dagen met minstens één oefening voltooid."""
    done = progress_df[
        (progress_df["username"] == username) &
        ((progress_df["cardio"] == 1) | (progress_df["kracht"] == 1))
    ]["dag"].nunique()
    return done

# ---------------- REGISTRATIE ----------------
with st.expander("Nieuwe gebruiker registreren"):
    new_name = st.text_input("Naam:", key="reg_name")
    new_password = st.text_input("Wachtwoord:", type="password", key="reg_pass")
    if st.button("Registreren"):
        register_user(new_name, new_password)

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.subheader("Inloggen")
    login_name = st.text_input("Naam:", key="login_name")
    login_pass = st.text_input("Wachtwoord:", type="password", key="login_pass")
    if st.button("Inloggen"):
        login_user(login_name, login_pass)

# ---------------- HOOFDAPP ----------------
if st.session_state.logged_in:
    username = st.session_state.username

    # UITLOGGEN
    if st.button("Uitloggen"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

    # INITIALISEER PROGRESSIE
    initialize_progress(username)

    # GEBRUIKER KLEUREN
    st.sidebar.subheader("Kies je kleuren:")
    cardio_color = st.sidebar.color_picker("Cardio kleur", "#FF5733")
    kracht_color = st.sidebar.color_picker("Kracht kleur", "#337BFF")

    # VOORTGANG & BADGES
    completed_days = get_completed_days(username)
    total_days = df["dag"].nunique()
    st.progress(completed_days / total_days)
    st.write(f"✅ {completed_days} van {total_days} dagen voltooid")
    badges = completed_days // 5
    if badges > 0:
        st.success("🏅 " + " ".join(["🎉" for _ in range(badges)]) + f" {badges} badge(s) verdiend!")

    # DAG SELECTEREN
    dag = st.selectbox("Selecteer een dag:", df["dag"].unique())
    oef = df[df["dag"] == dag].iloc[0]
    st.write(f"**Wat te doen:** {oef['wat te doen']}")

    # RUSTDAG
    if str(oef["wat te doen"]).lower() == "rust":
        st.info("Vandaag is een rustdag 😴")
    else:
        cardio_link = oef["cardio"] if pd.notna(oef["cardio"]) and str(oef["cardio"]).strip() else None
        kracht_link = oef["kracht"] if pd.notna(oef["kracht"]) and str(oef["kracht"]).strip() else None
        video_link = oef["video"] if "video" in oef and pd.notna(oef["video"]) else None

        # CSS
        st.markdown("""
        <style>
        .btn {display: inline-block; padding: 12px 28px; font-size:16px; color:white !important; text-decoration:none; border-radius:10px; margin:6px 0; transition:0.2s ease-in-out;}
        .btn:hover {transform: scale(1.05); opacity:0.85;}
        .btn-container {text-align:center; margin-top:10px;}
        </style>
        """, unsafe_allow_html=True)

        # CARDIO
        if cardio_link:
            done = progress_df.loc[(progress_df["username"]==username) & (progress_df["dag"]==dag), "cardio"].values[0]
            btn_text = "🏃‍♂️ Cardio ✅" if done else "🏃‍♂️ Start Cardio"
            if st.button(f"Cardio-{dag}", key=f"cardio_{dag}") and not done:
                mark_done(username, dag, "cardio")
                st.success("✅ Cardio voltooid!")
            st.markdown(f'<div class="btn-container"><a class="btn" style="background-color:{cardio_color}" href="{cardio_link}" target="_blank">{btn_text}</a></div>', unsafe_allow_html=True)

        # KRACHT
        if kracht_link:
            done = progress_df.loc[(progress_df["username"]==username) & (progress_df["dag"]==dag), "kracht"].values[0]
            btn_text = "🏋️‍♂️ Kracht ✅" if done else "🏋️‍♂️ Start Kracht"
            if st.button(f"Kracht-{dag}", key=f"kracht_{dag}") and not done:
                mark_done(username, dag, "kracht")
                st.success("✅ Kracht voltooid!")
            st.markdown(f'<div class="btn-container"><a class="btn" style="background-color:{kracht_color}" href="{kracht_link}" target="_blank">{btn_text}</a></div>', unsafe_allow_html=True)

        # VIDEO IN DE APP
        if video_link:
            st.subheader("Bekijk video:")
            st.video(video_link)
