# app.py - nowa, w pełni interaktywna wersja
import streamlit as st
from config import SITES
from generator import run_generation_process, run_news_process, fetch_categories, find_pexels_images_list

st.set_page_config(page_title="Generator Treści AI", layout="wide")

st.title("🤖 Generator Treści AI")
st.write("Narzędzie do tworzenia i publikacji artykułów na wybranych portalach.")

# --- Inicjalizacja Pamięci Sesji ---
if 'manual_topic_data' not in st.session_state:
    st.session_state.manual_topic_data = {}
if 'pexels_results' not in st.session_state:
    st.session_state.pexels_results = []
if 'selected_image_url' not in st.session_state:
    st.session_state.selected_image_url = None
if 'image_search_query' not in st.session_state:
    st.session_state.image_search_query = ""

# --- KROK 1: Wybór portalu ---
st.header("Krok 1: Wybierz portal")
friendly_names = {key: SITES[key]['friendly_name'] for key in SITES}
chosen_friendly_name = st.selectbox("Portal docelowy:", options=list(friendly_names.values()))
site_key = [k for k, v in friendly_names.items() if v == chosen_friendly_name][0]

# --- KROK 2: Wybór tematu i obrazka ---
st.header("Krok 2: Wybierz temat i obrazek")

# --- Zakładki do wyboru źródła tematu ---
source_tab, image_tab = st.tabs(["Źródło Tematu", "Obrazek Wyróżniający"])

with source_tab:
    topic_source = st.radio("Źródło tematu:", ('Automatycznie (z Event Registry)', 'Ręcznie'), horizontal=True, key="topic_source")
    if topic_source == 'Ręcznie':
        st.subheader("Wprowadź dane ręcznie")
        with st.form("manual_topic_form"):
            title = st.text_input("Tytuł / główna myśl artykułu (wymagane):", value=st.session_state.manual_topic_data.get('title', ''))
            url = st.text_input("Opcjonalny URL do artykułu źródłowego:", value=st.session_state.manual_topic_data.get('url', ''))
            body_snippet = st.text_area("Opcjonalny dodatkowy kontekst / fragment:", value=st.session_state.manual_topic_data.get('body_snippet', ''))
            
            submitted = st.form_submit_button("Zatwierdź temat")
            if submitted:
                st.session_state.manual_topic_data = { "title": title, "url": url, "body_snippet": body_snippet, "source_name": "Dane ręczne" }
                st.session_state.image_search_query = title # Automatycznie ustaw zapytanie do wyszukiwania obrazka
                st.success("Temat został zatwierdzony!")

with image_tab:
    st.subheader("Wybierz obrazek wyróżniający")
    image_mode = st.radio("Wybierz metodę dodania obrazka:", ["Wgraj ręcznie", "Znajdź w Pexels (darmowe zdjęcia)"], key="image_mode", horizontal=True)

    # Opcja 1: Ręczne wgranie
    if image_mode == "Wgraj ręcznie":
        uploaded_image = st.file_uploader("Wgraj plik:", type=['jpg', 'jpeg', 'png', 'webp'])
        if uploaded_image:
            st.session_state.manual_topic_data['image_url'] = uploaded_image
            st.session_state.selected_image_url = None # Czyścimy wybór z Pexels
            st.success("Obrazek został wgrany.")

    # Opcja 2: Interaktywne wyszukiwanie w Pexels
    elif image_mode == "Znajdź w Pexels (darmowe zdjęcia)":
        st.session_state.manual_topic_data['image_url'] = None # Czyścimy wgrany plik

        query = st.text_input("Wpisz słowa kluczowe do wyszukania obrazka:", value=st.session_state.image_search_query)
        
        if st.button("Szukaj zdjęć w Pexels"):
            st.session_state.selected_image_url = None # Czyścimy poprzedni wybór
            with st.spinner("Szukanie propozycji..."):
                st.session_state.pexels_results = find_pexels_images_list(query)

        if st.session_state.pexels_results:
            st.write("Wybierz jedno ze zdjęć klikając przycisk:")
            cols = st.columns(3)
            for i, photo in enumerate(st.session_state.pexels_results):
                with cols[i % 3]:
                    st.image(photo['preview_url'], caption=f"Autor: {photo['photographer']}")
                    if st.button("✅ Wybierz to zdjęcie", key=f"select_{photo['id']}"):
                        st.session_state.selected_image_url = photo['original_url']
                        st.session_state.pexels_results = [] # Czyścimy wyniki po wyborze
                        st.rerun() # Odświeżamy widok, by pokazać potwierdzenie

    # Potwierdzenie wyboru
    if st.session_state.get('selected_image_url'):
        st.success(f"Wybrano obrazek do artykułu!")
        st.image(st.session_state.selected_image_url, width=300)

# --- KROK 3: Wybór typu artykułu i kategorii ---
st.header("Krok 3: Doprecyzuj artykuł")
col1, col2 = st.columns(2)
with col1:
    article_type = st.radio("Typ artykułu:", ("Premium (długi)", "Newsowy (krótki)"), horizontal=True)
with col2:
    category_mode = st.radio("Kategoria:", ("Automatycznie", "Ręcznie"), horizontal=True)

chosen_category_id = None
if category_mode == "Ręcznie":
    with st.spinner("Pobieranie kategorii..."):
        category_options = fetch_categories(SITES[site_key])
    if category_options:
        category_names = [name for (_, name) in category_options]
        selected_name = st.selectbox("Wybierz kategorię:", options=category_names)
        chosen_category_id = [cat_id for cat_id, cat_name in category_options if cat_name == selected_name][0]
    else:
        st.warning("Nie udało się pobrać kategorii.")

# --- KROK 4: Generowanie ---
st.header("Krok 4: Generuj!")
if st.button("🚀 Uruchom proces generowania"):
    if topic_source == 'Ręcznie' and not st.session_state.manual_topic_data.get('title'):
        st.error("Przy ręcznym wprowadzaniu temat jest wymagany! Wypełnij i zatwierdź formularz w Kroku 2.")
    else:
        # Finalizujemy dane o obrazku przed wysłaniem
        if st.session_state.get('selected_image_url'):
            st.session_state.manual_topic_data['image_url'] = st.session_state.selected_image_url
        
        with st.spinner("Trwa proces generowania... To może zająć od 1 do 3 minut."):
            topic_src_simple = topic_source.split(' ')[0]
            
            if article_type.startswith("Premium"):
                result = run_generation_process(site_key, topic_src_simple, st.session_state.manual_topic_data, category_id=chosen_category_id)
            else:
                result = run_news_process(site_key, topic_src_simple, st.session_state.manual_topic_data, category_id=chosen_category_id)

            if not result or "BŁĄD" in result:
                st.error(f"BŁĄD: {result}")
            else:
                st.success("Gotowe!")
                st.info(result)
                st.balloons()
