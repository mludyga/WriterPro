import json
import time
import logging
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import openai
import base64
import textwrap
import argparse
import random

# --- ZMIANA: Importujemy konfigurację z nowego pliku ---
try:
    from config_ai_topics import SITES, COMMON_KEYS
except ImportError:
    print("BŁĄD: Nie znaleziono pliku config_ai_topics.py.")
    exit()

# --- Konfiguracja logowania (bez zmian) ---
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("generator_ai.log", encoding='utf-8'), logging.StreamHandler()]
)

# --- Inicjalizacja Klientów API (bez zmian) ---
try:
    openai_client = openai.OpenAI(api_key=COMMON_KEYS["OPENAI_API_KEY"])
except Exception as e:
    logging.error(f"Nie udało się zainicjować klienta OpenAI: {e}")
    exit()

# --- Główna funkcja do wywoływania Perplexity (bez zmian) ---
def _call_perplexity_api(prompt):
    """Pomocnicza funkcja do wywoływania API Perplexity."""
    headers = {"Authorization": f"Bearer {COMMON_KEYS['PERPLEXITY_API_KEY']}", "Content-Type": "application/json"}
    payload = {"model": "sonar-pro", "messages": [{"role": "user", "content": prompt}]}
    try:
        response = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, data=json.dumps(payload), timeout=400)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Błąd API Perplexity: {e}")
        return None

# --- NOWA FUNKCJA: Generowanie tematu przez AI ---
def get_ai_generated_topic(site_config):
    """
    Prosi sonar-pro o wygenerowanie listy tematów i losowo wybiera jeden.
    """
    logging.info("Generowanie tematu przez AI (sonar-pro)...")
    
    thematic_prompt = site_config.get("ai_topic_prompt")
    if not thematic_prompt:
        logging.error("Brak 'ai_topic_prompt' w konfiguracji portalu.")
        return None

    prompt = textwrap.dedent(f"""
        Jesteś redaktorem naczelnym. Na podstawie poniższych wytycznych, zaproponuj 5 chwytliwych, aktualnych i angażujących tematów na artykuły.
        Wytyczne: "{thematic_prompt}"

        Zwróć odpowiedź jako listę w formacie JSON, wewnątrz obiektu z kluczem "topics".
        Przykład odpowiedzi:
        {{
          "topics": [
            "Temat numer jeden, który przyciągnie czytelników",
            "Drugi, równie ciekawy temat o lokalnych sprawach",
            "Trzecia propozycja dotycząca analizy rynkowej",
            "Czwarty pomysł na artykuł poradnikowy",
            "Piąty, kontrowersyjny temat do dyskusji"
          ]
        }}
    """)

    try:
        response_str = _call_perplexity_api(prompt)
        if not response_str: return None
        
        json_part = response_str[response_str.find('{'):response_str.rfind('}')+1]
        data = json.loads(json_part)
        topics = data.get("topics", [])
        
        if not topics:
            logging.warning("AI nie zwróciło żadnych tematów.")
            return None
            
        chosen_topic = random.choice(topics)
        logging.info(f"AI zaproponowało tematy. Wybrano losowo: '{chosen_topic}'")
        
        return {
            "title": chosen_topic, "url": None, "body_snippet": "Temat wygenerowany przez AI.",
            "image_url": None, "source_name": "AI Generated"
        }
    except Exception as e:
        logging.error(f"Błąd w get_ai_generated_topic: {e}")
        return None

# --- Reszta skryptu (skopiowana z generator.py) ---

# UWAGA: Poniżej znajduje się reszta funkcji z Twojego oryginalnego skryptu.
# Nie musisz ich kopiować, są już tutaj zawarte.

def step1_research(topic_data, site_config):
    """Krok 1: AI przeprowadza research i zbiera 'surowe' dane oraz elementy narracyjne."""
    logging.info("--- KROK 1: Rozpoczynam research i syntezę danych... ---")
    prompt = textwrap.dedent(f"""
        Twoim zadaniem jest przeprowadzenie dogłębnego researchu na temat z poniższych danych. Przeanalizuj podany URL i/lub tematykę i znajdź dodatkowe, wiarygodne źródła.
        **NIE PISZ ARTYKUŁU.** Twoim celem jest wyłącznie zebranie i przedstawienie kluczowych informacji.
        **TEMAT DO ANALIZY:**
        - URL: {topic_data.get('url', 'Brak')}
        - Tytuł: "{topic_data.get('title', '')}"
        - Kontekst: "{topic_data.get('body_snippet', '')}"
        **ZNAJDŹ I WYPISZ W PUNKTACH:**
        - Kluczowe fakty, liczby, statystyki.
        - Nazwiska ekspertów i ich tezy. Także cytaty.
        - Ważne daty i nazwy oficjalnych dokumentów lub raportów.
        - Główne argumenty "za" i "przeciw" (jeśli dotyczy).
        - Potencjalny materiał do tabeli porównawczej.
        - **Elementy narracyjne:** Znajdź "ludzki" kąt, interesujące anegdoty, kontrowersje lub punkty zwrotne w historii tematu, które mogą uczynić artykuł ciekawszym.
        Zwróć odpowiedź jako zwięzłą, dobrze zorganizowaną listę punktów.
    """)
    return _call_perplexity_api(prompt)

def step_news_article(research_data, site_config, topic_data):
    """Generuje krótki artykuł newsowy."""
    prompt = textwrap.dedent(f"""
        Jesteś dziennikarzem newsowym. Masz zebrać i skondensować poniższe informacje w **krótki artykuł (300–400 słów)**:
        - Najważniejsze fakty i liczby dotyczące: "{topic_data.get('title')}" ({topic_data.get('url')})
        - Opinie ekspertów (prawdziwe cytaty - jeśli są).
        - własne podsumowanie artykułu z nieformalną puentą, lub komentarzem. Obiektywnie. Nastrój w zależności od tematyki artykułu.
        Dane do analizy: {research_data}
        ---
        ZASADY PISANIA: {site_config['prompt_template']}
        Zwróć gotowy tekst w HTML, używając tylko tagów <h2>, <p>, <ul>, <li>, <strong>, <blockquote>.
    """)
    return _call_perplexity_api(prompt)

def get_auth_header(site_config):
    if site_config['auth_method'] == 'bearer':
        return {'Authorization': f"Bearer {site_config['wp_bearer_token']}"}
    else:
        credentials = f"{site_config['wp_username']}:{site_config['wp_password']}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        return {'Authorization': f"Basic {token}"}

def get_all_wp_categories(site_config):
    url = f"{site_config['wp_api_url_base']}/categories?per_page=100" 
    headers = get_auth_header(site_config)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return {cat['name']: cat['id'] for cat in response.json()}
    except requests.exceptions.RequestException as e:
        logging.error(f"Nie udało się pobrać listy kategorii: {e}")
        return None

def choose_category_ai(title, content_snippet, available_categories_names, fallback_category="Bez kategorii"):
    if not available_categories_names or len(available_categories_names) <= 1:
        return list(available_categories_names)[:1] if available_categories_names else [fallback_category]
    logging.info("Wybieranie kategorii przez AI...")
    categories_str = ", ".join(available_categories_names)
    prompt_content = (f"Wybierz JEDNĄ NAJLEPSZĄ kategorię dla artykułu z listy. Tytuł: \"{title}\". Zajawka: \"{content_snippet}\". Dostępne kategorie: [{categories_str}]. Zwróć tylko samą nazwę kategorii.")
    try:
        response = openai_client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt_content}], temperature=0.0, max_tokens=30)
        return [response.choices[0].message.content.strip()]
    except Exception as e:
        logging.error(f"Błąd podczas wyboru kategorii przez AI: {e}")
        return [fallback_category]

def generate_tags_ai(title, content):
    logging.info("Generowanie tagów AI...")
    prompt = [{"role": "system", "content": "Wygeneruj 5-7 trafnych tagów (1-2 słowa każdy, po polsku) do artykułu. Zwróć jako listę JSON, np. [\"tag1\", \"tag2\"]."}, {"role": "user", "content": f"Tytuł: {title}\nFragment:{content[:1000]}"}]
    try:
        response = openai_client.chat.completions.create(model="gpt-4o-mini", messages=prompt, temperature=0.2, max_tokens=100, response_format={"type": "json_object"})
        tags_data = json.loads(response.choices[0].message.content)
        return tags_data if isinstance(tags_data, list) else tags_data.get("tags", [])
    except Exception as e:
        logging.error(f"Błąd podczas generowania tagów AI: {e}")
        return []

def get_or_create_term_id(name, term_type, site_config):
    headers = get_auth_header(site_config)
    url = f"{site_config['wp_api_url_base']}/{term_type}"
    try:
        response = requests.get(url, headers=headers, params={'search': name})
        response.raise_for_status()
        for term in response.json():
            if term.get("name", "").lower() == name.lower(): return term["id"]
        logging.info(f"Termin '{name}' nie istnieje. Tworzenie nowego ({term_type})...")
        create_resp = requests.post(url, headers=headers, json={"name": name, "slug": name.lower().replace(' ', '-')})
        create_resp.raise_for_status()
        return create_resp.json()["id"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Błąd podczas obsługi terminu '{name}': {e}")
        return None

def find_pexels_image_url(query):
    pexels_api_key = COMMON_KEYS.get("PEXELS_API_KEY")
    if not pexels_api_key: return None
    try:
        from pexels_api import API
        api = API(pexels_api_key)
        api.search(query, page=1, results_per_page=1)
        photos = api.get_entries()
        return photos[0].large if photos else None
    except Exception as e:
        logging.error(f"Błąd podczas komunikacji z API Pexels: {e}")
        return None

def upload_image_to_wp(image_source, article_title, site_config):
    if not image_source: return None
    try:
        img_response = requests.get(image_source, stream=True, timeout=20)
        img_response.raise_for_status()
        img_content = img_response.content
        content_type = img_response.headers.get('content-type', 'image/jpeg')
        
        headers = get_auth_header(site_config)
        safe_filename = ''.join(c for c in article_title if c.isalnum() or c in " ").strip().replace(' ', '_')[:50] + ".jpg"
        headers['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
        headers['Content-Type'] = content_type
        
        wp_r = requests.post(f"{site_config['wp_api_url_base']}/media", headers=headers, data=img_content)
        wp_r.raise_for_status()
        logging.info("Obrazek przesłany pomyślnie.")
        return wp_r.json().get("id")
    except Exception as e:
        logging.error(f"Błąd podczas przesyłania obrazka do WP: {e}")
        return None

def publish_to_wp(data_to_publish, site_config):
    logging.info(f"Publikowanie na {site_config['friendly_name']}: '{data_to_publish['title']}'")
    url = f"{site_config['wp_api_url_base']}/posts"
    headers = get_auth_header(site_config)
    headers['Content-Type'] = 'application/json'
    try:
        r = requests.post(url, headers=headers, json=data_to_publish)
        r.raise_for_status()
        logging.info(f"Artykuł opublikowany pomyślnie! URL: {r.json().get('link')}")
        return r.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Błąd podczas publikacji w WordPress: {e}\nOdpowiedź serwera: {e.response.text}")
        return None

def run_news_process(site_key, topic_source, manual_topic_data, category_id=None):
    site_config = SITES[site_key]
    
    if topic_source == 'Ręcznie':
        topic_data = manual_topic_data
    else: # Automatycznie
        topic_data = get_ai_generated_topic(site_config)

    if not topic_data: return "BŁĄD: Nie udało się uzyskać tematu."

    research_data = step1_research(topic_data, site_config)
    if not research_data: return "BŁĄD: Research nie powiódł się."

    news_html = step_news_article(research_data, site_config, topic_data)
    if not news_html: return "BŁĄD: Pisanie newsowego artykułu nie powiodło się."

    soup = BeautifulSoup(news_html, 'html.parser')
    title_tag = soup.find('h2')
    post_title = title_tag.get_text(strip=True) if title_tag else topic_data.get('title', 'Brak tytułu')
    if title_tag: title_tag.decompose()
    post_content = str(soup)

    all_categories = get_all_wp_categories(site_config)
    if category_id is None and all_categories:
        chosen_cat_name = choose_category_ai(post_title, post_content, list(all_categories.keys()))[0]
        category_id = all_categories.get(chosen_cat_name, 1)
    
    tags_list = generate_tags_ai(post_title, post_content)
    tag_ids = [get_or_create_term_id(tag, 'tags', site_config) for tag in tags_list if tag]

    image_to_upload = find_pexels_image_url(post_title.split(':')[0])
    featured_media_id = upload_image_to_wp(image_to_upload, post_title, site_config)

    data_to_publish = {
        'title': post_title, 'content': post_content, 'status': 'publish',
        'categories': [category_id or 1], 'tags': [tid for tid in tag_ids if tid]
    }
    if featured_media_id: data_to_publish['featured_media'] = featured_media_id

    result = publish_to_wp(data_to_publish, site_config)
    return f"Artykuł opublikowany! Link: {result.get('link')}" if result else "BŁĄD: Publikacja nie powiodła się."

def run_from_command_line(args):
    """Uruchamia proces na podstawie argumentów z wiersza poleceń."""
    if args.type == "news":
        logging.info(f"Uruchamiam generowanie [News] dla portalu: {args.site} ze źródła: {args.source}")
        result = run_news_process(args.site, args.source, {})
    else:
        # Tutaj można dodać logikę dla typu "premium" w przyszłości
        logging.error(f"Typ 'premium' nie jest jeszcze obsługiwany w tym skrypcie.")
        return
    logging.info(result)
