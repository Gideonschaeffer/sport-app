import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import yaml

# ---------- PAGINA ----------
st.set_page_config(page_title="Sport App", layout="centered")

# ---------- KLEUREN ----------
cardio_color = "#FF5733"
kracht_color = "#337BFF"

# ---------- DATA ----------
df = pd.read_excel("sport_schema.xlsx")

# ---------- LOGIN ----------
with open("users.yaml") as file:
    users_config = yaml.safe_load(file)

authenticator = stauth.Authenticate(
    users_config['credentials'],
    users_config['cookie']['name'],
    users_config['cookie']['key'],
    users_config['cookie']['expiry_days']
)

name, auth_status, username = authenticator.login("Login")


# ---------- NA LOGIN ----------
if auth_status:

    st.title(f"Welkom, {name} 🏋️‍♂️")

    # ---------- PROGRESS CSV ----------
    try:
        progress_df = pd.read_csv("progress.csv")
    except FileNotFoundError:
        progress_df = pd.DataFrame(columns=["username", "dag", "cardio_done", "kracht_done"])

    # ---------- NIEUWE GEBRUIKER → 12 DAGEN AANMAKEN ----------
    if username not in progress_df["username"].unique():
        new_rows = pd.DataFrame([
            {"username": username, "dag": d, "cardio_done": 0, "kracht_done": 0}
            for d in df["dag"]
        ])
        progress_df = pd.concat([progress_df, new_rows], ignore_index=True)
        progress_df.to_csv("progress.csv", index=False)

    # ---------- VOORTGANGSBALK ----------
    completed_days = progress_df[
        (progress_df["username"] == username) &
        ((progress_df["cardio_done"] == 1) | (progress_df["kracht_done"] == 1))
    ]["dag"].nunique()

    total_days = len(df["dag"].unique())
    st.progress(completed_days / total_days)
    st.write(f"✅ {completed_days} van {total_days} dagen voltooid")

    # ---------- DAG SELECTEREN ----------
    dag = st.selectbox("Selecteer een dag:", df["dag"])
    oef = df[df["dag"] == dag].iloc[0]

    st.write(f"**Wat te doen:** {oef['wat te doen']}")

    # ---------- HUIDIGE DAG VOORTGANG ----------
    row_index = progress_df[
        (progress_df["username"] == username) & (progress_df["dag"] == dag)
    ].index[0]

    # ---------- RUSTDAG ----------
    if oef["wat te doen"].lower() == "rust":
        st.info("Vandaag is een rustdag 😴")

    else:
        cardio_link = oef["cardio"] if pd.notna(oef["cardio"]) and oef["cardio"].strip() else None
        kracht_link = oef["kracht"] if pd.notna(oef["kracht"]) and oef["kracht"].strip() else None

        # ---------- CSS ----------
        st.markdown("""
        <style>
        .btn {
            display: inline-block;
            padding: 12px 30px;
            font-size: 16px;
            color: white !important;
            text-decoration: none;
            border-radius: 10px;
            margin: 6px;
            transition: 0.2s ease-in-out;
        }
        .btn:hover {
            transform: scale(1.05);
            opacity: 0.85;
        }
        .btn-container {
            text-align: center;
            margin-top: 12px;
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
                f'<div class="btn-container"><a class="btn" style="background-color:{cardio_color}" href="{cardio_link}" target="_blank">{cardio_text}</a></div>',
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
                f'<div class="btn-container"><a class="btn" style="background-color:{kracht_color}" href="{kracht_link}" target="_blank">{kracht_text}</a></div>',
                unsafe_allow_html=True
            )

    authenticator.logout("Uitloggen")

elif auth_status == False:
    st.error("❌ Verkeerde gebruikersnaam of wachtwoord")

elif auth_status is None:
    st.warning("Voer je login in")
