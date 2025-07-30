# app.py (z obsługą trybu Premium i Newsowego)
import streamlit as st
from config import SITES
from generator import run_generation_process, run_news_process
from generator import fetch_categories


st.set_page_config(page_title="Generator Treści AI", layout="wide")

st.title("🤖 Generator Treści AI")
st.write("Narzędzie do tworzenia i publikacji artykułów na wybranych portalach: tryb Premium (długi) lub Newsowy (krótki komentarz).")

# --- Inicjalizacja Pamięci Sesji ---
if 'manual_topic_data' not in st.session_state:
    st.session_state.manual_topic_data = {}

# --- KROK 1: Wybór portalu ---
st.header("Krok 1: Wybierz portal")
friendly_names = {key: SITES[key]['friendly_name'] for key in SITES}
chosen_friendly_name = st.selectbox("Portal docelowy:", options=friendly_names.values())
site_key = [k for k, v in friendly_names.items() if v == chosen_friendly_name][0]

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
            st.session_state.manual_topic_data = {
                "title": title,
                "url": url,
                "body_snippet": body_snippet,
                "source_name": "Dane ręczne",
                "image_url": uploaded_image
            }
            st.success("Temat został zatwierdzony! Możesz teraz uruchomić generowanie.")

# --- KROK 2a: Wybór typu artykułu ---
st.header("Krok 2a: Wybierz typ artykułu")
article_type = st.radio(
    "Jakiego rodzaju artykuł chcesz wygenerować?",
    ("Premium (długi, z planem)", "Newsowy (krótki komentarz)"),
    horizontal=True
)

# --- KROK 2b: Wybór kategorii ---
st.header("Krok 2b: Wybierz kategorię")

category_mode = st.radio(
    "Jak dobrać kategorię artykułu?",
    ("Automatycznie", "Wybierz ręcznie"),
    horizontal=True
)

chosen_category = None
category_options = []

if category_mode == "Wybierz ręcznie":
    with st.spinner("Pobieranie kategorii z portalu..."):
        site_config = SITES[site_key]
        category_options = fetch_categories(site_config)

    if category_options:
        category_names = [name for (_, name) in category_options]
        selected_name = st.selectbox("Wybierz kategorię:", options=category_names)
        
        # Pobieramy ID kategorii
        for cat_id, cat_name in category_options:
            if cat_name == selected_name:
                chosen_category = cat_id
                break

        # 🔐 Zapisujemy do session_state
        if chosen_category:
            st.session_state["chosen_category_id"] = chosen_category

    else:
        st.warning("Nie udało się pobrać kategorii z portalu. Wybór ręczny niemożliwy.")

# --- KROK 3: Generowanie ---
st.header("Krok 3: Generuj!")
if st.button("🚀 Uruchom proces generowania"):
    # Walidacja tematu
    if topic_source == 'Ręcznie' and not st.session_state.manual_topic_data.get('title'):
        st.error("Przy ręcznym wprowadzaniu temat jest wymagany! Wypełnij formularz powyżej i kliknij 'Zatwierdź temat'.")
    else:
        with st.spinner("Trwa proces generowania... To może zająć od 1 do 3 minut. Nie zamykaj tej karty."):
            if article_type.startswith("Premium"):
                result = run_generation_process(site_key, topic_source.split(' ')[0], st.session_state.manual_topic_data)
            else:
                result = run_news_process(site_key, topic_source.split(' ')[0], st.session_state.manual_topic_data)

            if not result:
                st.error("BŁĄD: Proces generowania nie powiódł się.")
            elif "BŁĄD" in result:
                st.error(result)
            else:
                st.success("Gotowe! Oto wygenerowany artykuł:")
                st.write(result)
                st.balloons()
