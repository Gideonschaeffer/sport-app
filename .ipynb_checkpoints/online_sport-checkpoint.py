import pandas as pd
import streamlit as st

# --- Kleuren ---
cardio_color = "#FF5733"  # Oranje/rood
kracht_color = "#337BFF"  # Blauw

# Excel-bestand inladen
df = pd.read_excel("sport_schema.xlsx")

st.title("🏋️‍♂️ Sport App")
st.write("Kies een dag om te zien welke oefeningen je moet doen en bekijk de YouTube-video's.")

dag = st.selectbox("Selecteer een dag:", df['dag'])
oef = df[df['dag'] == dag].iloc[0]

st.write(f"**Wat te doen:** {oef['wat te doen']}")

if oef['wat te doen'].lower() == 'rust':
    st.info("Vandaag is een rustdag! 😴")
else:
    cardio_link = oef['cardio'] if pd.notna(oef['cardio']) and oef['cardio'].strip() != "" else None
    kracht_link = oef['kracht'] if pd.notna(oef['kracht']) and oef['kracht'].strip() != "" else None

    # CSS voor link-knoppen
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

    # Alleen cardio
    if cardio_link and not kracht_link:
        st.markdown(f'<div class="btn-container"><a class="btn-link" style="background-color:{cardio_color}" href="{cardio_link}" target="_blank">Start Cardio</a></div>', unsafe_allow_html=True)

    # Alleen kracht
    elif kracht_link and not cardio_link:
        st.markdown(f'<div class="btn-container"><a class="btn-link" style="background-color:{kracht_color}" href="{kracht_link}" target="_blank">Start Kracht</a></div>', unsafe_allow_html=True)

    # Beide oefeningen
    elif cardio_link and kracht_link:
        st.markdown(f'''
        <div class="btn-container">
            <a class="btn-link" style="background-color:{cardio_color}" href="{cardio_link}" target="_blank">Start Cardio</a>
            <a class="btn-link" style="background-color:{kracht_color}" href="{kracht_link}" target="_blank">Start Kracht</a>
        </div>
        ''', unsafe_allow_html=True)
