# generator.py (wersja "Agentowa")
import json
import time
import logging
from datetime import datetime, timedelta
import requests
from eventregistry import EventRegistry, QueryArticlesIter
from bs4 import BeautifulSoup
import openai
import base64
import textwrap

# --- Import konfiguracji ---
try:
    from config import SITES, COMMON_KEYS
except ImportError:
    print("BŁĄD: Nie znaleziono pliku config.py.")
    exit()

# --- Konfiguracja logowania ---
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("generator.log", encoding='utf-8'), logging.StreamHandler()]
)

# --- Inicjalizacja Klientów API ---
try:
    openai_client = openai.OpenAI(api_key=COMMON_KEYS["OPENAI_API_KEY"])
except Exception as e:
    logging.error(f"Nie udało się zainicjować klienta OpenAI: {e}")
    exit()

# --- FUNKCJE INTERFEJSU UŻYTKOWNIKA (bez zmian) ---
def select_portal():
    print("Wybierz portal, na którym chcesz opublikować artykuł:")
    sites_list = list(SITES.keys())
    for i, site_key in enumerate(sites_list):
        print(f"{i + 1}. {SITES[site_key]['friendly_name']}")
    while True:
        try:
            choice = int(input(f"Wybierz numer (1-{len(sites_list)}): ")) - 1
            if 0 <= choice < len(sites_list):
                return sites_list[choice]
            else:
                print("Niepoprawny numer.")
        except ValueError:
            print("To nie jest numer.")

def select_topic_source():
    print("\nWybierz źródło tematu:")
    print("1. Znajdź temat automatycznie (Event Registry)")
    print("2. Wpisz temat ręcznie")
    while True:
        choice = input("Wybierz numer (1-2): ")
        if choice in ['1', '2']:
            return choice
        else:
            print("Niepoprawny wybór.")

def get_manual_topic():
    print("\n--- Ręczne wprowadzanie tematu ---")
    title = input("Podaj tytuł / główną myśl artykułu: ")
    url = input("Podaj opcjonalny URL do artykułu źródłowego (jeśli jest): ")
    body_snippet = input("Podaj opcjonalny dodatkowy kontekst (jeśli jest): ")
    image_url = input("Podaj opcjonalny URL do obrazka (jeśli jest): ")
    return {
        "title": title, "url": url, "body_snippet": body_snippet,
        "source_name": "Dane ręczne", "image_url": image_url
    }
    
# --- NOWY, TRÓJETAPOWY PROCES GENEROWANIA ARTYKUŁU ---

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

def step1_research(topic_data, site_config):
    """Krok 1: AI przeprowadza research i zbiera 'surowe' dane oraz elementy narracyjne."""
    logging.info("--- KROK 1: Rozpoczynam research i syntezę danych... ---")
    prompt = textwrap.dedent(f"""
        Twoim zadaniem jest przeprowadzenie dogłębnego researchu na temat z poniższych danych. Przeanalizuj podany URL i znajdź dodatkowe, wiarygodne źródła.
        **NIE PISZ ARTYKUŁU.** Twoim celem jest wyłącznie zebranie i przedstawienie kluczowych informacji.

        **TEMAT DO ANALIZY:**
        - URL: {topic_data.get('url', 'Brak')}
        - Tytuł: "{topic_data.get('title', '')}"
        - Kontekst: "{topic_data.get('body_snippet', '')}"

        **ZNAJDŹ I WYPISZ W PUNKTACH:**
        - Kluczowe fakty, liczby, statystyki.
        - Nazwiska ekspertów i ich tezy.
        - Ważne daty i nazwy oficjalnych dokumentów lub raportów.
        - Główne argumenty "za" i "przeciw" (jeśli dotyczy).
        - Potencjalny materiał do tabeli porównawczej.
        - **Elementy narracyjne:** Znajdź "ludzki" kąt, interesujące anegdoty, kontrowersje lub punkty zwrotne w historii tematu, które mogą uczynić artykuł ciekawszym.

        Zwróć odpowiedź jako zwięzłą, dobrze zorganizowaną listę punktów.
    """)
    return _call_perplexity_api(prompt)

def step2_create_outline(research_data, site_config):
    """Krok 2: AI tworzy kreatywny i zhumanizowany plan artykułu."""
    logging.info("--- KROK 2: Tworzę kreatywny i szczegółowy plan artykułu... ---")
    prompt = textwrap.dedent(f"""
        Na podstawie poniższej syntezy danych, stwórz **kreatywny, angażujący i logiczny plan artykułu premium** dla portalu {site_config['friendly_name']}.

        **ZEBRANE DANE:**
        {research_data}

        **TWOJE ZADANIE:**
        1.  Zaproponuj nowy, chwytliwy i merytoryczny tytuł. Umieść go w tagu `<h2>`.
        2.  **Stwórz unikalną strukturę artykułu.** Nie trzymaj się jednego szablonu. Dobierz sekcje i ich kolejność tak, aby jak najlepiej opowiedzieć historię i wyjaśnić temat czytelnikowi. Zacznij od leada, który ma zachęcić do dalszego czytania tekstu.
        3.  Zaproponuj **kreatywne i intrygujące tytuły dla poszczególnych sekcji** (`<h2>`, `<h3>`), a nie tylko generyczne opisy typu "Analiza danych".
        4.  **Inteligentnie dobierz elementy wysokiej jakości treści.** Zastanów się, czy do TEGO KONKRETNEGO tematu pasują takie bloki jak: **tabela porównawcza**, **analiza historyczna**, **praktyczne porady** lub **box z kluczowymi informacjami**. Włącz je do planu **tylko wtedy, gdy mają sens** i realnie wzbogacają treść, a nie dlatego, że musisz.
        5.  Pod każdym nagłówkiem napisz w 1-2 zdaniach, co dokładnie zostanie w tej sekcji opisane.

        Zwróć tylko i wyłącznie kompletny, gotowy do realizacji plan artykułu.
    """)
    return _call_perplexity_api(prompt)

def step3_write_article(research_data, outline, site_config):
    """Krok 3: AI pisze finalny artykuł, trzymając się planu i zasad, z naciskiem na styl."""
    logging.info("--- KROK 3: Piszę finalny artykuł... To może potrwać kilka minut. ---")
    
    # Pobieramy szablon z config.py, który nadal zawiera wszystkie kluczowe zasady formatowania
    prompt_template = SITES[site_config['site_key']]['prompt_template']

    final_prompt = textwrap.dedent(f"""
        Twoim zadaniem jest napisanie kompletnego artykułu premium na podstawie poniższych danych i planu.
        **Kluczowe jest, abyś pisał w sposób angażujący i narracyjny. Opowiadaj historię, a nie tylko referuj fakty.**

        **ZEBRANE DANE (Użyj ich do wypełnienia treści):**
        {research_data}

        ---
        **PLAN ARTYKUŁU (Trzymaj się go ściśle, włącznie z kreatywnymi tytułami sekcji):**
        {outline}
        ---

        **ZASADY PISANIA (Zastosuj je do tworzenia finalnego tekstu):**
        {prompt_template}

        Napisz kompletny artykuł w HTML, zaczynając od tytułu w `<h2>`, zgodnie z przekazanym planem i wszystkimi zasadami.
    """)
    return _call_perplexity_api(final_prompt)


# --- FUNKCJE POMOCNICZE (bez zmian) ---
# ... wklej tutaj wszystkie funkcje pomocnicze z poprzedniej wersji:
# get_auth_header, get_event_registry_topics, get_all_wp_categories, 
# choose_category_ai, generate_tags_ai, get_or_create_term_id, 
# upload_image_to_wp, publish_to_wp
# Poniżej wklejam je dla kompletności.

def get_auth_header(site_config):
    if site_config['auth_method'] == 'bearer':
        return {'Authorization': f"Bearer {site_config['wp_bearer_token']}"}
    else:
        credentials = f"{site_config['wp_username']}:{site_config['wp_password']}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        return {'Authorization': f"Basic {token}"}

def get_event_registry_topics(site_config):
    logging.info("Pobieranie tematów z EventRegistry...")
    try:
        er = EventRegistry(apiKey=site_config['event_registry_key'])
        query = QueryArticlesIter(conceptUri=site_config['er_concept_uri'], lang="pol", dateStart=datetime.now().date() - timedelta(days=3))
        for article in query.execQuery(er, sortBy="rel", maxItems=1):
            return {"title": article.get("title"), "body_snippet": article.get("body", "")[:700], "source_name": article.get("source", {}).get("title"), "url": article.get("url"), "image_url": article.get("image")}
        return None
    except Exception as e:
        logging.error(f"Błąd podczas pobierania tematów z EventRegistry: {e}")
        return None

def get_all_wp_categories(site_config):
    logging.info(f"Pobieranie kategorii z {site_config['friendly_name']}...")
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
        return next(iter(available_categories_names)) if available_categories_names else fallback_category
    logging.info(f"Wybieranie kategorii przez AI...")
    categories_str = ", ".join(available_categories_names)
    prompt_content = (f"Wybierz JEDNĄ, najlepszą kategorię dla artykułu z listy. Tytuł: \"{title}\". Dostępne kategorie: [{categories_str}]. Zwróć tylko nazwę.")
    try:
        response = openai_client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt_content}], temperature=0.0, max_tokens=20)
        chosen_category = response.choices[0].message.content.strip().replace('"', '')
        return chosen_category if chosen_category in available_categories_names else fallback_category
    except Exception as e:
        logging.error(f"Błąd podczas wyboru kategorii przez AI: {e}")
        return fallback_category

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

def upload_image_to_wp(image_url, article_title, site_config):
    if not image_url: return None
    logging.info(f"Przesyłanie obrazka: {image_url}")
    try:
        img_response = requests.get(image_url, stream=True, timeout=20)
        img_response.raise_for_status()
        headers = get_auth_header(site_config)
        ascii_title = article_title.encode('ascii', 'ignore').decode('ascii')
        safe_filename_base = ''.join(c for c in ascii_title if c.isalnum() or c in " ").strip().replace(' ', '_')
        filename = f"{safe_filename_base[:50]}_img.jpg"
        headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        headers['Content-Type'] = img_response.headers.get('content-type', 'image/jpeg')
        wp_r = requests.post(f"{site_config['wp_api_url_base']}/media", headers=headers, data=img_response.content)
        wp_r.raise_for_status()
        logging.info("Obrazek przesłany pomyślnie.")
        return wp_r.json().get("id")
    except requests.exceptions.RequestException as e:
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
        logging.error(f"Błąd podczas publikacji w WordPress: {e}")
        logging.error(f"Odpowiedź serwera: {r.text}")
        return None

# --- GŁÓWNA PĘTLA PROGRAMU (w nowej, agentowej wersji) ---
def main():
    chosen_site_key = select_portal()
    site_config = SITES[chosen_site_key]
    site_config['site_key'] = chosen_site_key # Dodajemy klucz do configa dla łatwiejszego dostępu

    topic_source = select_topic_source()
    topic_data = get_manual_topic() if topic_source == '2' else get_event_registry_topics(site_config)
    if not topic_data:
        print("Nie udało się uzyskać tematu. Koniec pracy.")
        return

    # === NOWY PROCES TRÓJETAPOWY ===
    research_data = step1_research(topic_data, site_config)
    if not research_data:
        print("Nie udało się przeprowadzić researchu. Koniec pracy.")
        return
    
    outline = step2_create_outline(research_data, site_config)
    if not outline:
        print("Nie udało się stworzyć planu artykułu. Koniec pracy.")
        return

    print("\n--- WYGENEROWANY PLAN ARTYKUŁU ---")
    print(outline)
    print("------------------------------------")
    
    proceed = input("Czy kontynuować pisanie artykułu na podstawie tego planu? (t/n): ").lower()
    if proceed != 't':
        print("Przerwano proces na życzenie użytkownika.")
        return
        
    generated_html = step3_write_article(research_data, outline, site_config)
    if not generated_html:
        print("Nie udało się napisać finalnego artykułu. Koniec pracy.")
        return
    
    # === KONIEC NOWEGO PROCESU, reszta jak wcześniej ===

    soup = BeautifulSoup(generated_html, 'html.parser')
    title_tag = soup.find('h2')
    post_title = title_tag.get_text(strip=True) if title_tag else topic_data['title']
    if title_tag: title_tag.decompose()
    post_content = str(soup)
    logging.info(f"Wygenerowano nowy tytuł: '{post_title}'")

    all_categories = get_all_wp_categories(site_config)
    chosen_category_name = choose_category_ai(post_title, post_content, list(all_categories.keys()))
    category_id = all_categories.get(chosen_category_name)
    
    tags_list = generate_tags_ai(post_title, post_content)
    tag_ids = [get_or_create_term_id(tag, "tags", site_config) for tag in tags_list]
    
    featured_media_id = upload_image_to_wp(topic_data.get('image_url'), post_title, site_config)

    data_to_publish = {"title": post_title, "content": post_content, "status": "publish", "categories": [category_id] if category_id else [], "tags": [tid for tid in tag_ids if tid]}
    if featured_media_id:
        data_to_publish['featured_media'] = featured_media_id

    publish_to_wp(data_to_publish, site_config)
    logging.info("--- Proces zakończony pomyślnie! ---")

if __name__ == "__main__":
    main()