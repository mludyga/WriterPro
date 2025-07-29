# app.py (poprawiona wersja z użyciem st.session_state)
import streamlit as st
from config import SITES
from generator import run_generation_process

st.set_page_config(page_title="Generator Treści AI", layout="wide")

st.title("🤖 Generator Treści Premium")
st.write("Narzędzie do tworzenia i publikacji artykułów na wybranych portalach, oparte o model agentowy (Research -> Plan -> Pisanie).")

# --- Inicjalizacja Pamięci Sesji ---
# To sprawi, że Streamlit będzie pamiętał dane tematu między kliknięciami
if 'manual_topic_data' not in st.session_state:
    st.session_state.manual_topic_data = {}

# --- KROK 1: Wybór portalu ---
st.header("Krok 1: Wybierz portal")
friendly_names = {key: SITES[key]['friendly_name'] for key in SITES}
chosen_friendly_name = st.selectbox("Portal docelowy:", options=friendly_names.values())
site_key = [key for key, name in friendly_names.items() if name == chosen_friendly_name][0]


# --- KROK 2: Wybór źródła tematu ---
st.header("Krok 2: Wybierz temat")
topic_source = st.radio("Źródło tematu:", ('Automatycznie (z Event Registry)', 'Ręcznie'), horizontal=True)

if topic_source == 'Ręcznie':
    st.subheader("Wprowadź dane ręcznie")
    with st.form("manual_topic_form"):
        title = st.text_input("Tytuł / główna myśl artykułu (wymagane):", value=st.session_state.manual_topic_data.get('title', ''))
        url = st.text_input("Opcjonalny URL do artykułu źródłowego:", value=st.session_state.manual_topic_data.get('url', ''))
        body_snippet = st.text_area("Opcjonalny dodatkowy kontekst / fragment:", value=st.session_state.manual_topic_data.get('body_snippet', ''))
        uploaded_image = st.file_uploader("Wgraj obrazek (opcjonalnie)", type=['jpg', 'jpeg', 'png', 'webp'])
        
        submitted = st.form_submit_button("Zatwierdź temat")
        
        if submitted:
            # Zapisujemy dane do pamięci sesji, a nie do tymczasowej zmiennej
            st.session_state.manual_topic_data = {
                "title": title, "url": url, "body_snippet": body_snippet,
                "source_name": "Dane ręczne", "image_url": uploaded_image
            }
            st.success("Temat został zatwierdzony! Możesz teraz uruchomić generowanie.")


# --- KROK 3: Generowanie ---
st.header("Krok 3: Generuj!")
if st.button("🚀 Uruchom proces generowania"):
    # Od teraz sprawdzamy dane w pamięci sesji
    if topic_source == 'Ręcznie' and not st.session_state.manual_topic_data.get('title'):
        st.error("Przy ręcznym wprowadzaniu temat jest wymagany! Wypełnij formularz powyżej i kliknij 'Zatwierdź temat'.")
    else:
        with st.spinner("Trwa proces generowania... To może zająć od 3 do 5 minut. Nie zamykaj tej karty."):
            # Przekazujemy dane z pamięci sesji do funkcji generującej
            result_message = run_generation_process(site_key, topic_source.split(' ')[0], st.session_state.manual_topic_data)
            
            if "BŁĄD" in result_message:
                st.error(result_message)
            else:
                st.success(result_message)
                st.balloons()
