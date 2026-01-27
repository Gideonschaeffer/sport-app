import pandas as pd
import streamlit as st
import os

# ---------------- PAGINA ----------------
st.set_page_config(page_title="Sport App", layout="centered")

# ---------------- KLEUREN ----------------
CARDIO_COLOR = "#FF5733"
KRACHT_COLOR = "#337BFF"

# ---------------- DATA ----------------
df = pd.read_excel("sport_schema.xlsx")

# ---------------- GEBRUIKERS ----------------
if os.path.exists("users.csv") and os.path.getsize("users.csv") > 0:
    users_df = pd.read_csv("users.csv")
    # Kolomnamen strippen om spaties te verwijderen
    users_df.columns = [col.strip() for col in users_df.columns]
else:
    st.error("❌ users.csv niet gevonden of leeg")
    st.stop()

# ---------------- GEBRUIKER INLOG ----------------
username = st.text_input("Voer je naam in:")
if not username:
    st.warning("👤 Voer je naam in om verder te gaan")
    st.stop()

if username not in users_df["username"].values:
    st.error("❌ Onbekende gebruiker")
    st.stop()

password = st.text_input("Voer je wachtwoord in:", type="password")
if not password:
    st.warning("🔒 Voer je wachtwoord in om verder te gaan")
    st.stop()

correct_password = users_df.loc[users_df["username"] == username, "password"].values[0]
if password != correct_pasword:
    st.error("❌ Onjuist password")
    st.stop()

st.title(f"Welkom, {username} 🏋️‍♂️")

# ---------------- PROGRESS BESTAND ----------------
if os.path.exists("progress.csv") and os.path.getsize("progress.csv") > 0:
    progress_df = pd.read_csv("progress.csv")
    for col in ["username", "dag", "cardio", "kracht"]:
        if col not in progress_df.columns:
            progress_df[col] = 0
else:
    progress_df = pd.DataFrame(columns=["username", "dag", "cardio", "kracht"])

# ---------- NIEUWE GEBRUIKER → 12 DAGEN ----------
if username not in progress_df["username"].values:
    new_rows = pd.DataFrame([
        {"username": username, "dag": dag, "cardio": 0, "kracht": 0}
        for dag in df["dag"].unique()
    ])
    progress_df = pd.concat([progress_df, new_rows], ignore_index=True)
    progress_df.to_csv("progress.csv", index=False)

# ---------- VOORTGANG ----------
completed_days = progress_df[
    (progress_df["username"] == username) &
    ((progress_df["cardio"] == 1) | (progress_df["kracht"] == 1))
]["dag"].nunique()

total_days = df["dag"].nunique()

st.progress(completed_days / total_days)
st.write(f"✅ {completed_days} van {total_days} dagen voltooid")

# ---------- DAG SELECTEREN ----------
dag = st.selectbox("Selecteer een dag:", df["dag"].unique())
oef = df[df["dag"] == dag].iloc[0]

st.write(f"**Wat te doen:** {oef['wat te doen']}")

row_index = progress_df[
    (progress_df["username"] == username) &
    (progress_df["dag"] == dag)
].index[0]

# ---------- RUSTDAG ----------
if str(oef["wat te doen"]).lower() == "rust":
    st.info("Vandaag is een rustdag 😴")
else:
    cardio_link = oef["cardio"] if pd.notna(oef["cardio"]) and str(oef["cardio"]).strip() else None
    kracht_link = oef["kracht"] if pd.notna(oef["kracht"]) and str(oef["kracht"]).strip() else None

    # ---------- CSS ----------
    st.markdown("""
    <style>
    .btn {
        display: inline-block;
        padding: 12px 28px;
        font-size: 16px;
        color: white !important;
        text-decoration: none;
        border-radius: 10px;
        margin: 6px 0;
        transition: 0.2s ease-in-out;
    }
    .btn:hover {
        transform: scale(1.05);
        opacity: 0.85;
    }
    .btn-container {
        text-align: center;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------- CARDIO ----------
    if cardio_link:
        cardio_done = progress_df.loc[row_index, "cardio"]
        cardio_text = "Cardio ✅" if cardio_done else "Start Cardio"

        if st.button(cardio_text):
            progress_df.loc[row_index, "cardio"] = 1
            progress_df.to_csv("progress.csv", index=False)
            st.success("✅ Cardio gemarkeerd als voltooid!")

        st.markdown(
            f"""
            <div class="btn-container">
                <a class="btn" style="background-color:{CARDIO_COLOR}"
                   href="{cardio_link}" target="_blank">
                   {cardio_text}
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------- KRACHT ----------
    if kracht_link:
        kracht_done = progress_df.loc[row_index, "kracht"]
        kracht_text = "Kracht ✅" if kracht_done else "Start Kracht"

        if st.button(kracht_text):
            progress_df.loc[row_index, "kracht"] = 1
            progress_df.to_csv("progress.csv", index=False)
            st.success("✅ Kracht gemarkeerd als voltooid!")

        st.markdown(
            f"""
            <div class="btn-container">
                <a class="btn" style="background-color:{KRACHT_COLOR}"
                   href="{kracht_link}" target="_blank">
                   {kracht_text}
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
