import pandas as pd
import streamlit as st

# --- Kleuren instellen ---
cardio_color = "#d40bd3"  # Paars voor cardio
kracht_color = "#337BFF"  # Blauw voor kracht

# --- Excel-bestand inladen ---
# Zorg dat 'sport_schema.xlsx' in dezelfde map staat als app.py
df = pd.read_excel("sport_schema.xlsx")

# --- Titel en uitleg ---
st.set_page_config(page_title="Sport App", layout="centered")
st.title("🏋️‍♂️ Sport App 🏋️‍♂️")
st.write("Kies een dag om te zien welke oefeningen je moet doen.")

# --- Dag selecteren ---
dag = st.selectbox("Selecteer een dag:", df['dag'])
oef = df[df['dag'] == dag].iloc[0]

st.write(f"**Wat te doen:** {oef['wat te doen']}")

# --- Rustdag check ---
if oef['wat te doen'].lower() == 'rust':
    st.info("Vandaag is een rustdag! 😴")
else:
    # Links ophalen
    cardio_link = oef['cardio'] if pd.notna(oef['cardio']) and oef['cardio'].strip() != "" else None
    kracht_link = oef['kracht'] if pd.notna(oef['kracht']) and oef['kracht'].strip() != "" else None

    # --- CSS voor knoppen ---
    st.markdown("""
    <style>
    .btn-link {
        display: inline-block;
        padding: 12px 30px;
        font-size: 16px;
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        margin: 5px;
        transition: 0.3s;
    }
    .btn-link:hover {
        opacity: 0.8;
    }
    .btn-container {
        text-align: center;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- Knoppen tonen ---
    if cardio_link and not kracht_link:
        st.markdown(f'<div class="btn-container"><a class="btn-link" style="background-color:{cardio_color}" href="{cardio_link}" target="_blank">Start Cardio</a></div>', unsafe_allow_html=True)

    elif kracht_link and not cardio_link:
        st.markdown(f'<div class="btn-container"><a class="btn-link" style="background-color:{kracht_color}" href="{kracht_link}" target="_blank">Start Kracht</a></div>', unsafe_allow_html=True)

    elif cardio_link and kracht_link:
        st.markdown(f'''
        <div class="btn-container">
            <a class="btn-link" style="background-color:{cardio_color}" href="{cardio_link}" target="_blank">Start Cardio</a>
            <a class="btn-link" style="background-color:{kracht_color}" href="{kracht_link}" target="_blank">Start Kracht</a>
        </div>
        ''', unsafe_allow_html=True)
