import pandas as pd
import streamlit as st
import os

# ---------------- PAGINA ----------------
st.set_page_config(page_title="Sport App", layout="centered")

# ---------------- BESTANDEN ----------------
users_file = "users.csv"
progress_file = "progress.csv"
sport_file = "sport_schema.xlsx"  # 12-dagen schema

# ---------------- DATA ----------------
df = pd.read_excel(sport_file)

# ---------------- USERS ----------------
if not os.path.exists(users_file):
    pd.DataFrame(columns=["naam", "password"]).to_csv(users_file, index=False)
users_df = pd.read_csv(users_file)
users_df.columns = [col.strip() for col in users_df.columns]

# ---------------- PROGRESS ----------------
if not os.path.exists(progress_file):
    pd.DataFrame(columns=["username", "dag", "cardio", "kracht"]).to_csv(progress_file, index=False)
progress_df = pd.read_csv(progress_file)
progress_df.columns = [col.strip() for col in progress_df.columns]

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# ---------------- REGISTRATIE ----------------
with st.expander("Nieuwe gebruiker registreren"):
    new_name = st.text_input("Naam:", key="reg_name")
    new_password = st.text_input("Wachtwoord:", type="password", key="reg_pass")

    if st.button("Registreren"):
        if not new_name or not new_password:
            st.warning("⚠️ Vul zowel naam als wachtwoord in")
        elif new_name in users_df["naam"].values:
            st.error("❌ Deze naam is al in gebruik")
        else:
            new_user = pd.DataFrame([{"naam": new_name, "password": new_password}])
            users_df = pd.concat([users_df, new_user], ignore_index=True)
            users_df.to_csv(users_file, index=False)
            st.success(f"✅ Account aangemaakt voor {new_name}!")

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.subheader("Inloggen")
    naam = st.text_input("Naam:", key="login_name")
    password = st.text_input("Wachtwoord:", type="password", key="login_pass")

    if st.button("Inloggen"):
        if naam not in users_df["naam"].values:
            st.error("❌ Onbekende gebruiker")
        else:
            correct_password = users_df.loc[users_df["naam"] == naam, "password"].iloc[0]
            if password != correct_password:
                st.error("❌ Onjuist wachtwoord")
            else:
                st.session_state.logged_in = True
                st.session_state.username = naam
                st.success(f"Welkom, {naam} 🏋️‍♂️")
                st.experimental_rerun()

# ---------------- HOOFDAPP ----------------
if st.session_state.logged_in:
    username = st.session_state.username

    # ---------------- UITLOGGEN ----------------
    if st.button("Uitloggen"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

    st.title(f"Welkom, {username} 🏋️‍♂️")

    # ---------------- NIEUWE GEBRUIKER → 12 DAGEN ----------------
    if username not in progress_df["username"].values:
        new_rows = pd.DataFrame([
            {"username": username, "dag": dag, "cardio": 0, "kracht": 0}
            for dag in df["dag"].unique()
        ])
        progress_df = pd.concat([progress_df, new_rows], ignore_index=True)
        progress_df.to_csv(progress_file, index=False)

    # ---------------- GEBRUIKER KLEUREN ----------------
    st.sidebar.subheader("Kies je kleuren:")
    cardio_color = st.sidebar.color_picker("Cardio kleur", "#FF5733")
    kracht_color = st.sidebar.color_picker("Kracht kleur", "#337BFF")

    # ---------------- VOORTGANG & BADGES ----------------
    completed_days = progress_df[
        (progress_df["username"] == username) &
        ((progress_df["cardio"] == 1) | (progress_df["kracht"] == 1))
    ]["dag"].nunique()
    total_days = df["dag"].nunique()
    st.progress(completed_days / total_days)
    st.write(f"✅ {completed_days} van {total_days} dagen voltooid")

    # Badges per 5 dagen
    badges = completed_days // 5
    if badges > 0:
        st.success("🏅 " + " ".join(["🎉" for _ in range(badges)]) + f" {badges} badge(s) verdiend!")

    # ---------------- DAG SELECTEREN ----------------
    dag = st.selectbox("Selecteer een dag:", df["dag"].unique())
    oef = df[df["dag"] == dag].iloc[0]
    st.write(f"**Wat te doen:** {oef['wat te doen']}")

    row_index = progress_df[
        (progress_df["username"] == username) &
        (progress_df["dag"] == dag)
    ].index[0]

    # ---------------- RESET DAG KNOP ----------------
    if st.button("Reset dag"):
        progress_df.loc[row_index, ["cardio", "kracht"]] = 0
        progress_df.to_csv(progress_file, index=False)
        st.success("♻️ Dag reset!")
        st.experimental_rerun()

    # ---------------- RUSTDAG ----------------
    if str(oef["wat te doen"]).lower() == "rust":
        st.info("Vandaag is een rustdag 😴")
    else:
        cardio_link = oef["cardio"] if pd.notna(oef["cardio"]) and str(oef["cardio"]).strip() else None
        kracht_link = oef["kracht"] if pd.notna(oef["kracht"]) and str(oef["kracht"]).strip() else None
        video_link = oef["video"] if "video" in oef and pd.notna(oef["video"]) else None

        # ---------------- CSS ----------------
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

        # ---------------- CARDIO ----------------
        if cardio_link:
            cardio_done = progress_df.loc[row_index, "cardio"]
            btn_text = "🏃‍♂️ Cardio ✅" if cardio_done else "🏃‍♂️ Start Cardio"
            if not cardio_done and st.button("Start Cardio"):
                progress_df.loc[row_index, "cardio"] = 1
                progress_df.to_csv(progress_file, index=False)
                st.success("✅ Cardio gemarkeerd als voltooid!")

            st.markdown(
                f'<div class="btn-container"><a class="btn" style="background-color:{cardio_color}" href="{cardio_link}" target="_blank">{btn_text}</a></div>',
                unsafe_allow_html=True
            )

        # ---------------- KRACHT ----------------
        if kracht_link:
            kracht_done = progress_df.loc[row_index, "kracht"]
            btn_text = "🏋️‍♂️ Kracht ✅" if kracht_done else "🏋️‍♂️ Start Kracht"
            if not kracht_done and st.button("Start Kracht"):
                progress_df.loc[row_index, "kracht"] = 1
                progress_df.to_csv(progress_file, index=False)
                st.success("✅ Kracht gemarkeerd als voltooid!")

            st.markdown(
                f'<div class="btn-container"><a class="btn" style="background-color:{kracht_color}" href="{kracht_link}" target="_blank">{btn_text}</a></div>',
                unsafe_allow_html=True
            )

        # ---------------- VIDEO IN DE APP ----------------
        if video_link:
            st.subheader("Bekijk video:")
            st.video(video_link)
