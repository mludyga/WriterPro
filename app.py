# app.py
import streamlit as st
from config import SITES
# Importujemy naszą główną, zmodyfikowaną funkcję
from generator import run_generation_process

st.set_page_config(page_title="Generator Treści AI", layout="wide")

st.title("🤖 Generator Treści Premium")
st.write("Narzędzie do tworzenia i publikacji artykułów na wybranych portalach, oparte o model agentowy (Research -> Plan -> Pisanie).")

# --- KROK 1: Wybór portalu ---
st.header("Krok 1: Wybierz portal")
# Tworzymy listę przyjaznych nazw do wyświetlenia
friendly_names = {key: SITES[key]['friendly_name'] for key in SITES}
chosen_friendly_name = st.selectbox("Portal docelowy:", options=friendly_names.values())
# Znajdujemy klucz systemowy na podstawie wybranej nazwy
site_key = [key for key, name in friendly_names.items() if name == chosen_friendly_name][0]


# --- KROK 2: Wybór źródła tematu ---
st.header("Krok 2: Wybierz temat")
topic_source = st.radio("Źródło tematu:", ('Automatycznie (z Event Registry)', 'Ręcznie'), horizontal=True)

manual_topic_data = {}
uploaded_image = None

if topic_source == 'Ręcznie':
    st.subheader("Wprowadź dane ręcznie")
    with st.form("manual_topic_form"):
        title = st.text_input("Tytuł / główna myśl artykułu (wymagane):")
        url = st.text_input("Opcjonalny URL do artykułu źródłowego:")
        body_snippet = st.text_area("Opcjonalny dodatkowy kontekst / fragment:")
        # Nowy element do wgrywania obrazka!
        uploaded_image = st.file_uploader("Wgraj obrazek (opcjonalnie)", type=['jpg', 'jpeg', 'png', 'webp'])
        
        submitted = st.form_submit_button("Zatwierdź temat")
        
        if submitted:
            manual_topic_data = {
                "title": title, "url": url, "body_snippet": body_snippet,
                "source_name": "Dane ręczne", "image_url": uploaded_image
            }


# --- KROK 3: Generowanie ---
st.header("Krok 3: Generuj!")
if st.button("🚀 Uruchom proces generowania"):
    # Sprawdzamy, czy przy ręcznym trybie podano tytuł
    if topic_source == 'Ręcznie' and not manual_topic_data.get('title'):
        st.error("Przy ręcznym wprowadzaniu temat jest wymagany! Wypełnij formularz powyżej i kliknij 'Zatwierdź temat'.")
    else:
        # Uruchamiamy proces w tle i pokazujemy "spinner"
        with st.spinner("Trwa proces generowania... To może zająć od 3 do 5 minut. Nie zamykaj tej karty."):
            # Wywołujemy naszą główną funkcję z generator.py
            result_message = run_generation_process(site_key, topic_source.split(' ')[0], manual_topic_data)
            
            # Wyświetlamy wynik
            if "BŁĄD" in result_message:
                st.error(result_message)
            else:
                st.success(result_message)
                st.balloons()