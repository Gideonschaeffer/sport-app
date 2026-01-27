import pandas as pd
import streamlit as st
import webbrowser

# --- Instellingen voor kleuren ---
cardio_color = "#FF5733"  # Oranje/rood voor cardio
kracht_color = "#337BFF"  # Blauw voor kracht

# Excel-bestand inladen
df = pd.read_excel("sport_schema.xlsx")

st.title("🏋️‍♂️ Sport App")
st.write("Kies een dag om te zien welke oefeningen je moet doen en bekijk de YouTube-video's.")

# Dag selecteren
dag = st.selectbox("Selecteer een dag:", df['dag'])

# Oefeningen van de gekozen dag ophalen
oef = df[df['dag'] == dag].iloc[0]

st.write(f"**Wat te doen:** {oef['wat te doen']}")

# Rustdag check
if oef['wat te doen'].lower() == 'rust':
    st.info("Vandaag is een rustdag! 😴")
else:
    # Links ophalen en checken of ze bestaan
    cardio_link = oef['cardio'] if pd.notna(oef['cardio']) and oef['cardio'].strip() != "" else None
    kracht_link = oef['kracht'] if pd.notna(oef['kracht']) and oef['kracht'].strip() != "" else None

    # Alleen cardio
    if cardio_link and not kracht_link:
        st.markdown(f"""
            <div style="text-align:center">
                <button style="background-color:{cardio_color}; color:white; padding:10px 30px; border:none; border-radius:8px; font-size:16px" 
                        onclick="window.open('{cardio_link}', '_blank')">
                    Start Cardio
                </button>
            </div>
        """, unsafe_allow_html=True)

    # Alleen kracht
    elif kracht_link and not cardio_link:
        st.markdown(f"""
            <div style="text-align:center">
                <button style="background-color:{kracht_color}; color:white; padding:10px 30px; border:none; border-radius:8px; font-size:16px" 
                        onclick="window.open('{kracht_link}', '_blank')">
                    Start Kracht
                </button>
            </div>
        """, unsafe_allow_html=True)

    # Beide oefeningen
    elif cardio_link and kracht_link:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div style="text-align:center">
                    <button style="background-color:{cardio_color}; color:white; padding:10px 30px; border:none; border-radius:8px; font-size:16px" 
                            onclick="window.open('{cardio_link}', '_blank')">
                        Start Cardio
                    </button>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div style="text-align:center">
                    <button style="background-color:{kracht_color}; color:white; padding:10px 30px; border:none; border-radius:8px; font-size:16px" 
                            onclick="window.open('{kracht_link}', '_blank')">
                        Start Kracht
                    </button>
                </div>
            """, unsafe_allow_html=True)