import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import yaml

# ---------------- PAGINA ----------------
st.set_page_config(
    page_title="Sport App",
    layout="centered"
)

# ---------------- KLEUREN ----------------
CARDIO_COLOR = "#FF5733"
KRACHT_COLOR = "#337BFF"

# ---------------- DATA ----------------
df = pd.read_excel("sport_schema.xlsx")

# ---------------- LOGIN CONFIG ----------------
with open("users.yaml") as file:
    users_config = yaml.safe_load(file)

authenticator = stauth.Authenticate(
    users_config["credentials"],
    users_config["cookie"]["name"],
    users_config["cookie"]["key"],
    users_config["cookie"]["expiry_days"]
)

# 🔴 DIT IS DE JUISTE LOGIN-CALL VOOR JOUW VERSIE
name, auth_status, username = authenticator.login("Login", "main")

# ---------------- NA LOGIN ----------------
if auth_status:

    st.title(f"Welkom, {name} 🏋️‍♂️")

    # ---------- PROGRESS BESTAND ----------
    try:
        progress_df = pd.read_csv("progress.csv")
    except FileNotFoundError:
        progress_df = pd.DataFrame(
            columns=["username", "dag", "cardio_done", "kracht_done"]
        )

    # ---------- NIEUWE GEBRUIKER → 12 DAGEN ----------
    if username not in progress_df["username"].unique():
        new_rows = pd.DataFrame([
            {
                "username": username,
                "dag": dag,
                "cardio_done": 0,
                "kracht_done": 0
            }
            for dag in df["dag"].unique()
        ])
        progress_df = pd.concat([progress_df, new_rows], ignore_index=True)
        progress_df.to_csv("progress.csv", index=False)

    # ---------- VOORTGANG ----------
    completed_days = progress_df[
        (progress_df["username"] == username) &
        ((progress_df["cardio_done"] == 1) | (progress_df["kracht_done"] == 1))
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
            cardio_done = progress_df.loc[row_index, "cardio_done"]
            cardio_text = "Cardio ✅" if cardio_done else "Start Cardio"

            if st.button(cardio_text):
                progress_df.loc[row_index, "cardio_done"] = 1
                progress_df.to_csv("progress.csv", index=False)
                st.experimental_rerun()

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
            kracht_done = progress_df.loc[row_index, "kracht_done"]
            kracht_text = "Kracht ✅" if kracht_done else "Start Kracht"

            if st.button(kracht_text):
                progress_df.loc[row_index, "kracht_done"] = 1
                progress_df.to_csv("progress.csv", index=False)
                st.experimental_rerun()

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

    authenticator.logout("Uitloggen", "main")

elif auth_status is False:
    st.error("❌ Verkeerde gebruikersnaam of wachtwoord")

elif auth_status is None:
    st.warning("👤 Voer je gebruikersnaam en wachtwoord in")
