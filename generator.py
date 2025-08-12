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
import argparse
import re

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
    
# --- TRÓJETAPOWY PROCES GENEROWANIA ARTYKUŁU ---

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

def fetch_categories(site_config):
    """
    Pobiera wszystkie dostępne kategorie z WordPressa.
    """
    base_url = site_config.get("wp_api_url_base")
    if not base_url:
        logging.warning("Brak wp_api_url_base w konfiguracji portalu.")
        return []

    url = f"{base_url}/categories"
    headers = {}
    auth = None

    if site_config.get("auth_method") == "basic":
        username = site_config.get("wp_username")
        password = site_config.get("wp_password")
        auth = (username, password)
    elif site_config.get("auth_method") == "bearer":
        token = site_config.get("wp_bearer_token")
        headers["Authorization"] = f"Bearer {token}"

    all_categories = []
    page = 1

    while True:
        try:
            response = requests.get(
                url,
                headers=headers,
                auth=auth,
                params={"per_page": 100, "page": page},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            all_categories.extend([(cat['id'], cat['name']) for cat in data])
            page += 1
        except Exception as e:
            logging.warning(f"Nie udało się pobrać kategorii z {url}: {e}")
            break

    return all_categories

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

def step2_create_outline(research_data, site_config, keyword=None):
    """Krok 2: AI tworzy kreatywny i zhumanizowany plan artykułu."""
    logging.info("--- KROK 2: Tworzę kreatywny i szczegółowy plan artykułu... ---")

    # Instrukcja dla tytułu z prawdziwą interpolacją słowa kluczowego
    kw = (keyword or "").strip()
    title_instruction = (
        f"1. Zaproponuj krótki i merytoryczny tytuł (maks. 70 znaków). "
        + (f"Tytuł **musi zawierać frazę kluczową lub jej bardzo bliski wariant**: '{kw}'. " if kw else "")
        + "Nie zawężaj zakresu tematu względem hasła użytkownika: jeśli hasło jest ogólne/przeglądowe, "
          "to tytuł też ma być ogólny/przeglądowy (np. lista, przegląd, porównanie), "
          "a nie o jednej atrakcji/miejscu/firmie. "
          "Dopuszczalna jest parafraza i doprecyzowanie dla SEO. "
          "Umieść tytuł w tagu <h2> i stosuj polskie zasady kapitalizacji."
    )

    prompt = textwrap.dedent(f"""
        Na podstawie poniższej syntezy danych, stwórz **kreatywny, angażujący i logiczny plan artykułu premium** dla portalu {site_config['friendly_name']}.

        **ZEBRANE DANE:**
        {research_data}

        **TWOJE ZADANIE:**
        {title_instruction}
        2.  **Stwórz unikalną strukturę artykułu.** Nie trzymaj się jednego szablonu. Dobierz sekcje i ich kolejność tak, aby jak najlepiej opowiedzieć historię i wyjaśnić temat czytelnikowi.
        3.  Zaproponuj **kreatywne i intrygujące tytuły dla poszczególnych sekcji** (`<h2>`, `<h3>`), a nie tylko generyczne opisy typu "Analiza danych".
        4.  **Inteligentnie dobierz elementy z bardzo wartościowym contentem.** Zastanów się, czy do TEGO KONKRETNEGO tematu pasują takie bloki jak: **tabela porównawcza**, **analiza historyczna**, **praktyczne porady** lub **box z kluczowymi informacjami**. Włącz je do planu **tylko wtedy, gdy mają sens**.
        5.  Pod każdym nagłówkiem napisz w 1–2 zdaniach, co dokładnie zostanie w tej sekcji opisane.
        6.  Nie używaj w podtytułach słów: "Wstęp", "Zakończenie", "Prolog", "Epilog" "Premium", "Box".
        
        Zwróć tylko i wyłącznie kompletny, gotowy do realizacji plan artykułu.
    """)
    return _call_perplexity_api(prompt)


def step3_write_article(research_data, outline, site_config, keyword=None):
    """Krok 3: AI pisze finalny artykuł, trzymając się planu i zasad, z naciskiem na styl."""
    logging.info("--- KROK 3: Piszę finalny artykuł... To może potrwać kilka minut. ---")
    prompt_template = site_config['prompt_template']

    manual_title_rule = ""
    if keyword:
        kw = (keyword or "").strip()
        manual_title_rule = textwrap.dedent(f"""
            ---
            **REGUŁA TYTUŁU (KRYTYCZNE):**
            - Tytuł w `<h2>` **musi** zawierać frazę kluczową lub jej bardzo bliski wariant: "{kw}".
            - **Nie zawężaj zakresu**: jeśli fraza jest przeglądowa/ogólna, tytuł nie może dotyczyć pojedynczego przykładu.
        """)

    anti_footnotes_rule = textwrap.dedent("""
        ---
        **BEZWZGLĘDNY ZAKAZ PRZYPISÓW I ODNIESIEŃ NUMERYCZNYCH:**
        - Nie używaj form typu [1], [2], (1), [^1], <sup>1</sup>, ani sekcji „Źródła/Bibliografia”.
        - Jeśli w researchu/planie pojawiają się takie oznaczenia – **zignoruj je** lub zastąp deskryptywną wzmianką w zdaniu (np. „Jak wynika z danych GUS…”).
        - Nie wstawiaj surowych URL-i jako dowodów. Cytuj nazwy instytucji/raportów w tekście.
    """)

    final_prompt = textwrap.dedent(f"""
        Twoim zadaniem jest napisanie kompletnego artykułu premium na podstawie poniższych danych i planu.
        **Pisz angażująco i narracyjnie. Lead 2–3 zdania, konkretny, bez wodolejstwa.**

        **ZEBRANE DANE:**
        {research_data}

        ---
        **PLAN ARTYKUŁU (Trzymaj się go ściśle):**
        {outline}
        ---

        **ZASADY PISANIA:**
        {prompt_template}
        {manual_title_rule}
        {anti_footnotes_rule}

        Napisz kompletny artykuł w HTML, zaczynając od tytułu w `<h2>`.
    """)
    return _call_perplexity_api(final_prompt)

def strip_numeric_citations(html: str) -> str:
    t = html or ""

    # 1) <sup>1</sup>, <sup> 2 </sup>
    t = re.sub(r'<sup>\s*\d+\s*</sup>', '', t, flags=re.IGNORECASE)

    # 2) [1], [1, 2], [ 3 , 4 ,5 ]
    t = re.sub(r'\s*\[\s*\d+(?:\s*,\s*\d+)*\s*\]', '', t)

    # 3) [^1] (markdown footnotes)
    t = re.sub(r'\s*\[\^\d+\]', '', t)

    # 4) (1) — tylko jeśli w nawiasie są wyłącznie cyfry
    t = re.sub(r'\s*\(\s*\d+\s*\)', '', t)

    # 5) odnośniki typu ^1
    t = re.sub(r'\s*\^\d+', '', t)

    # 6) sekcje „Źródła” / „Bibliografia” (nagłówek + treść do kolejnego <h2> lub końca)
    t = re.sub(r'<h2[^>]*>\s*(?:Źródła|Zrodla|Bibliografia)\s*</h2>.*?(?=(?:<h2|$))',
               '', t, flags=re.IGNORECASE | re.DOTALL)

    # 7) sprzątanie: spacje przed znakami, wielokrotne odstępy/linie
    t = re.sub(r'\s+([,.;:!?])', r'\1', t)
    t = re.sub(r'[ \t]{2,}', ' ', t)
    t = re.sub(r'\n{3,}', '\n\n', t)

    return t


# --- FUNKCJE POMOCNICZE ---
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
        
        # POPRAWKA NR 1: Rozszerzamy okno wyszukiwania, by uniknąć problemów ze strefą czasową.
        date_end = datetime.now().date()
        date_start = (date_end - timedelta(days=3)).isoformat()
        date_end = date_end.isoformat()

        uris = site_config.get("er_concept_uris") or [site_config['er_concept_uri']]

        # POPRAWKA NR 2 (Kluczowa): Usuwamy "sortBy" z tego miejsca.
        complex_query = {
          "$query": {
            "$and": [
              {"$or": [{"conceptUri": uri} for uri in uris]},
              {"dateStart": date_start, "dateEnd": date_end, "lang": "pol"}
            ]
          }
          # "sortBy" zostało stąd usunięte
        }

        qiter = QueryArticlesIter.initWithComplexQuery(complex_query)
        
        # POPRAWKA NR 3 (Kluczowa): Dodajemy "sortBy" jako argument funkcji.
        for article in qiter.execQuery(er, sortBy="date", maxItems=1):
            return {
              "title": article.get("title"),
              "body_snippet": article.get("body", "")[:700],
              "url": article.get("url"),
              "image_url": article.get("image"),
              "source_name": article.get("source", {}).get("title")
            }
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
        return list(available_categories_names)[:1] if available_categories_names else [fallback_category]

    logging.info("Wybieranie kategorii przez AI...")
    categories_str = ", ".join(available_categories_names)
    
    prompt_content = (
        f"Wybierz JEDNĄ lub DWIE NAJLEPSZE kategorie dla artykułu z poniższej listy. "
        f"Zwróć je jako listę, oddzielone przecinkiem (bez innych znaków). "
        f"Tytuł: \"{title}\". "
        f"Zajawka: \"{content_snippet}\". "
        f"Dostępne kategorie: [{categories_str}]. "
        f"Zwróć tylko same nazwy kategorii (maksymalnie 2)."
    )

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_content}],
            temperature=0.0,
            max_tokens=30
        )
        raw_output = response.choices[0].message.content.strip()
        selected = [cat.strip() for cat in raw_output.split(",") if cat.strip() in available_categories_names]
        return selected[:2] if selected else [fallback_category]
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

def upload_image_to_wp(image_source, article_title, site_config):
    if not image_source: return None
    img_content, content_type = None, 'image/jpeg'
    if isinstance(image_source, str) and image_source.startswith('http'):
        logging.info(f"Pobieranie obrazka z URL: {image_source}")
        try:
            img_response = requests.get(image_source, stream=True, timeout=20)
            img_response.raise_for_status()
            img_content, content_type = img_response.content, img_response.headers.get('content-type', 'image/jpeg')
        except requests.exceptions.RequestException as e:
            logging.error(f"Błąd podczas pobierania obrazka z URL: {e}")
            return None
    else:
        logging.info("Przetwarzanie wgranego obrazka...")
        img_content, content_type = image_source.getvalue(), image_source.type
    try:
        headers = get_auth_header(site_config)
        ascii_title = article_title.encode('ascii', 'ignore').decode('ascii')
        safe_filename_base = ''.join(c for c in ascii_title if c.isalnum() or c in " ").strip().replace(' ', '_')
        filename = f"{safe_filename_base[:50]}_img.jpg"
        headers['Content-Disposition'] = f'attachment; filename="{filename}"'
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
        logging.error(f"Błąd podczas publikacji w WordPress: {e}")
        logging.error(f"Odpowiedź serwera: {r.text}")
        return None

def step_news_article(research_data, site_config, topic_data):
    """
    Generuje krótki artykuł newsowy na podstawie researchu:
    - wypunktowane kluczowe dane,
    - 1–2 cytaty ekspertów,
    - krótki komentarz i opis sytuacji.
    """
    prompt = textwrap.dedent(f"""
        Jesteś dziennikarzem newsowym. Masz zebrać i skondensować poniższe informacje w **krótki artykuł (300–400 słów)**:
        - Najważniejsze fakty i liczby dotyczące: "{topic_data.get('title')}" ({topic_data.get('url')})
        - Opinie ekspertów (prawdziwe cytaty - jeśli są).
        - własne podsumowanie artykułu z nieformalną puentą, lub komentarzem. Obiektywnie. Nastrój w zależności od tematyki artykułu.

        Dane do analizy:
        {research_data}

        ---
        ZASADY PISANIA:
        {site_config['prompt_template']}

        Zwróć gotowy tekst w HTML, używając tylko tagów <h2>, <p>, <ul>, <li>, <strong>, <blockquote>.
    """)
    return _call_perplexity_api(prompt)

def run_news_process(site_key, topic_source, manual_topic_data, category_id=None):
    """
    Workflow dla newsowego artykułu łącznie z publikacją na WP.
    """
    site_config = SITES[site_key]
    site_config['site_key'] = site_key

    # Pobierz dane tematu
    topic_data = manual_topic_data if topic_source == 'Ręcznie' else get_event_registry_topics(site_config)
    if not topic_data:
        return "BŁĄD: Nie udało się uzyskać tematu."

    # Newsowy research
    research_data = step1_research(topic_data, site_config)
    if not research_data:
        return "BŁĄD: Research nie powiódł się."

    # Generowanie krótkiego artykułu newsowego
    news_html = step_news_article(research_data, site_config, topic_data)
    if not news_html:
        return "BŁĄD: Pisanie newsowego artykułu nie powiodło się."

    # Parsowanie i przygotowanie do publikacji
    soup = BeautifulSoup(news_html, 'html.parser')
    title_tag = soup.find('h2')
    post_title = title_tag.get_text(strip=True) if title_tag else topic_data.get('title', 'Brak tytułu')
    if title_tag:
        title_tag.decompose()
    post_content = str(soup)

    # --- POPRAWIONA LOGIKA KATEGORII ---
    all_categories = get_all_wp_categories(site_config)
    
    # Jeśli kategoria nie została przekazana ręcznie, poproś AI o wybór
    if category_id is None:
        if all_categories:
            logging.info("Kategoria nie została wybrana ręcznie. Uruchamiam wybór przez AI.")
            # AI zwraca listę nazw, np. ["Wiadomości"]
            chosen_category_names = choose_category_ai(post_title, post_content, list(all_categories.keys()))
            
            # Bierzemy pierwszą nazwę z listy zwróconej przez AI
            if chosen_category_names:
                chosen_name = chosen_category_names[0]
                # Znajdujemy ID dla tej nazwy w naszym słowniku kategorii
                category_id = all_categories.get(chosen_name)
                if category_id:
                    logging.info(f"AI wybrało kategorię: '{chosen_name}' (ID: {category_id})")
                else:
                    logging.warning(f"AI wybrało kategorię '{chosen_name}', ale nie znaleziono jej ID. Używam domyślnej.")
                    category_id = 1 # Domyślne ID (np. "Bez kategorii")
            else:
                logging.warning("AI nie zwróciło poprawnej nazwy kategorii. Używam domyślnej.")
                category_id = 1
        else:
            logging.warning("Nie udało się pobrać kategorii z WP. Używam domyślnej (ID: 1).")
            category_id = 1
    else:
        logging.info(f"Użyto ręcznie wybranej kategorii o ID: {category_id}")
    # ------------------------------------

    # Tagi (bez zmian)
    tags_list = generate_tags_ai(post_title, post_content)
    tag_ids = [get_or_create_term_id(tag, 'tags', site_config) for tag in tags_list if tag]

    # Obraz wyróżniony (bez zmian)
    featured_media_id = upload_image_to_wp(topic_data.get('image_url'), post_title, site_config)

    # Przygotowanie danych do publikacji (bez zmian)
    data_to_publish = {
        'title': post_title,
        'content': post_content,
        'status': 'publish',
        'categories': [category_id], # Przekazujemy już poprawne ID
        'tags': [tid for tid in tag_ids if tid]
    }
    if featured_media_id:
        data_to_publish['featured_media'] = featured_media_id

    # Publikacja (bez zmian)
    result = publish_to_wp(data_to_publish, site_config)
    if result and result.get('link'):
        return f"Artykuł newsowy opublikowany! Link: {result.get('link')}"
    else:
        return "BŁĄD: Publikacja newsowego artykułu nie powiodła się."


    def insert_youtube_embeds(html, youtube_links):
        soup = BeautifulSoup(html, 'html.parser')
        for link in youtube_links:
            for a_tag in soup.find_all('a', href=link):
                iframe = soup.new_tag("iframe", width="560", height="315", frameborder="0", allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share", allowfullscreen=True)
                # Obsługa short i long URL
                video_id = None
                if "watch?v=" in link:
                    video_id = link.split("watch?v=")[-1].split("&")[0]
                elif "youtu.be/" in link:
                    video_id = link.split("youtu.be/")[-1].split("?")[0]
                if video_id:
                    iframe['src'] = f"https://www.youtube.com/embed/{video_id}"
                    a_tag.replace_with(iframe)
        return str(soup)

    def wrap_images_with_figures(html, image_data):
        soup = BeautifulSoup(html, 'html.parser')
        for img_info in image_data:
            img_tag = soup.find("img", src=img_info["src"])
            if img_tag:
                figure = soup.new_tag("figure")
                figcaption = soup.new_tag("figcaption")
                figcaption.string = f"Źródło: {img_info['src']}"
                img_tag.wrap(figure)
                figure.append(figcaption)
        return str(soup)

    # Zamień linki YouTube na iframe'y
    if media_references["youtube"]:
        post_content = insert_youtube_embeds(post_content, media_references["youtube"])

    # Obuduj obrazki figure/figcaption
    if media_references["images"]:
        post_content = wrap_images_with_figures(post_content, media_references["images"])
    logging.info(f"Znalezione linki do embedów: {media_references}")

    # Kategorie
    all_categories = get_all_wp_categories(site_config)
    if category_id is not None:
        logging.info(f"Użyto ręcznie wybranej kategorii o ID: {category_id}")
    else:
        if all_categories is None:
            category_id = 1
        else:
            chosen_cat = choose_category_ai(post_title, post_content, list(all_categories.keys()))
            if isinstance(chosen_cat, list) and chosen_cat:
                chosen_name = chosen_cat[0]
            elif isinstance(chosen_cat, str):
                chosen_name = chosen_cat
            else:
                chosen_name = "Bez kategorii"
            category_id = all_categories.get(chosen_name, 1)

    # Tagi
    tags_list = generate_tags_ai(post_title, post_content)
    tag_ids = [get_or_create_term_id(tag, 'tags', site_config) for tag in tags_list]

    # Obraz wyróżniony
    featured_media_id = upload_image_to_wp(topic_data.get('image_url'), post_title, site_config)

    # Przygotowanie payloadu
    data_to_publish = {
        'title': post_title,
        'content': post_content,
        'status': 'publish',
        'categories': [category_id],
        'tags': [tid for tid in tag_ids if tid]
    }
    if featured_media_id:
        data_to_publish['featured_media'] = featured_media_id

    # Publikacja
    result = publish_to_wp(data_to_publish, site_config)
    if result and result.get('link'):
        return f"Artykuł newsowy opublikowany! Link: {result.get('link')}"
    else:
        return "BŁĄD: Publikacja newsowego artykułu nie powiodła się."

def run_generation_process(site_key, topic_source, manual_topic_data, category_id=None):
    """Główna funkcja wykonawcza, wywoływana przez aplikację webową."""
    site_config = SITES[site_key]
    site_config['site_key'] = site_key

    # 1) Pozyskaj temat (ER lub ręcznie)
    topic_data = manual_topic_data if topic_source == 'Ręcznie' else get_event_registry_topics(site_config)
    if not topic_data:
        return "BŁĄD: Nie udało się uzyskać tematu. Sprawdź Event Registry lub dane wprowadzone ręcznie."

    # 2) Research
    research_data = step1_research(topic_data, site_config)
    if not research_data:
        return "BŁĄD: Krok 1 (Research) nie powiódł się. Sprawdź logi."
    logging.info("--- WYNIK RESEARCHU ---\n" + research_data)

    # 3) Fraza kluczowa do tytułu (tylko gdy temat podano ręcznie)
    keyword_for_title = None
    if topic_source == 'Ręcznie':
        keyword_for_title = (topic_data.get('title') or '').strip()
        if keyword_for_title:
            logging.info(f"Wykryto ręczne słowo kluczowe dla tytułu: '{keyword_for_title}'")

    # 4) Plan artykułu
    outline = step2_create_outline(research_data, site_config, keyword=keyword_for_title)
    if not outline:
        return "BŁĄD: Krok 2 (Planowanie) nie powiódł się. Sprawdź logi."
    logging.info("--- WYGENEROWANY PLAN ARTYKUŁU ---\n" + outline)

    # 5) Pisanie artykułu (z regułami anty-przypisowymi w promptach)
    generated_html = step3_write_article(research_data, outline, site_config, keyword=keyword_for_title)
    if not generated_html:
        return "BŁĄD: Krok 3 (Pisanie) nie powiódł się. Sprawdź logi."

    # 6) Parsowanie HTML i kontrola tytułu
    soup = BeautifulSoup(generated_html, 'html.parser')
    h2_tag = soup.find('h2')
    current_title = h2_tag.get_text(strip=True) if h2_tag else (topic_data.get('title') or 'Brak tytułu')

    # Jeśli podano frazę ręcznie, sprawdź zgodność tytułu i ewentualnie popraw
    if keyword_for_title and not title_respects_keyword(current_title, keyword_for_title):
        logging.info(f"Tytuł wymaga korekty względem frazy: '{keyword_for_title}' -> '{current_title}'")
        fixed_h2_html = rewrite_title_to_match_keyword(current_title, keyword_for_title)  # zwraca <h2>...</h2>
        fixed_h2_soup = BeautifulSoup(fixed_h2_html, 'html.parser')
        if h2_tag:
            h2_tag.replace_with(fixed_h2_soup)
        else:
            soup.insert(0, fixed_h2_soup)
        # odśwież bieżący tytuł po korekcie
        h2_tag = soup.find('h2')
        current_title = h2_tag.get_text(strip=True) if h2_tag else current_title

    # 7) Usuń <h2> z treści (WordPress tytuł ma osobno)
    for t in soup.find_all('h2'):
        t.decompose()

    post_title = current_title.strip() if current_title else (topic_data.get('title') or 'Brak tytułu').strip()
    post_content = str(soup)

    # 8) SANITYZACJA: usuń wszystkie formy przypisów/odnośników numerycznych i sekcje „Źródła/Bibliografia”
    post_content = strip_numeric_citations(post_content)

    # 9) Kategorie
    all_categories = get_all_wp_categories(site_config)
    if category_id is not None:
        logging.info(f"Użyto ręcznie wybranej kategorii o ID: {category_id}")
    else:
        if not all_categories:
            logging.warning("Nie udało się pobrać kategorii z WP. Używam domyślnej 'Bez kategorii' (ID: 1).")
            category_id = 1
        else:
            chosen = choose_category_ai(post_title, post_content, list(all_categories.keys()))
            chosen_name = chosen[0] if isinstance(chosen, list) and chosen else "Bez kategorii"
            category_id = all_categories.get(chosen_name, 1)

    # 10) Tagi
    tags_list = generate_tags_ai(post_title, post_content) or []
    tag_ids = [tid for tid in (get_or_create_term_id(tag, "tags", site_config) for tag in tags_list) if tid]

    # 11) Obraz wyróżniony
    featured_media_id = upload_image_to_wp(topic_data.get('image_url'), post_title, site_config)

    # 12) Publikacja
    data_to_publish = {
        "title": post_title,
        "content": post_content,
        "status": "publish",
        "categories": [category_id] if category_id else [],
        "tags": tag_ids
    }
    if featured_media_id:
        data_to_publish["featured_media"] = featured_media_id

    result = publish_to_wp(data_to_publish, site_config)
    if result and result.get('link'):
        return f"Artykuł opublikowany pomyślnie! Link: {result.get('link')}"
    else:
        return "BŁĄD: Publikacja nie powiodła się. Sprawdź logi."


# Dodaj tę funkcję gdzieś w pliku generator.py
def run_from_command_line(args):
    """Uruchamia proces generowania na podstawie argumentów z wiersza poleceń."""
    site_key = args.site
    article_type = args.type
    topic_source = args.source
    # Ustawiamy domyślne dane tematu, ponieważ w trybie auto i tak zostaną nadpisane
    manual_topic_data = {} 
    
    # Wybieramy odpowiedni proces na podstawie typu artykułu
    if article_type == "premium":
        logging.info(f"Uruchamiam generowanie [Premium] dla portalu: {site_key} ze źródła: {topic_source}")
        result = run_generation_process(site_key, topic_source, manual_topic_data)
    elif article_type == "news":
        logging.info(f"Uruchamiam generowanie [News] dla portalu: {site_key} ze źródła: {topic_source}")
        result = run_news_process(site_key, topic_source, manual_topic_data)
    else:
        logging.error(f"Nieznany typ artykułu: {article_type}")
        return

    logging.info(result)

def find_pexels_images_list(query, count=15):
    """
    Wyszukuje w Pexels listę zdjęć i zwraca ich dane (ID, URL-e, autor).
    """
    pexels_api_key = COMMON_KEYS.get("PEXELS_API_KEY")
    if not pexels_api_key:
        logging.warning("Brak klucza PEXELS_API_KEY. Pomijam wyszukiwanie obrazka.")
        return []

    try:
        # Ten import musi być tutaj, aby uniknąć błędów, gdy biblioteka nie jest zainstalowana
        from pexels_api import API
        api = API(pexels_api_key)
        logging.info(f"Wyszukiwanie {count} obrazków w Pexels dla zapytania: '{query}'")
        
        api.search(query, page=1, results_per_page=count)
        photos = api.get_entries()

        if photos:
            # POPRAWKA: Zmieniono photo.src['medium'] na photo.medium,
            # ponieważ ta biblioteka przechowuje URL bezpośrednio w atrybucie.
            results = [
                {
                    "id": photo.id,
                    "photographer": photo.photographer,
                    "preview_url": photo.medium,      # <-- POPRAWIONA LINIA
                    "original_url": photo.large
                } 
                for photo in photos
            ]
            logging.info(f"Znaleziono {len(results)} obrazków.")
            return results
        else:
            logging.warning(f"Nie znaleziono żadnego obrazka dla zapytania: '{query}'")
            return []
    except Exception as e:
        logging.error(f"Błąd podczas komunikacji z API Pexels: {e}")
        return []


# Ten fragment dodaj na samym końcu pliku generator.py
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generator artykułów AI.")
    parser.add_argument("--site", type=str, required=True, help="Klucz portalu (np. autozakup, radiopin).")
    parser.add_argument("--type", type=str, choices=['premium', 'news'], default='premium', help="Typ artykułu do wygenerowania (premium lub news).")
    parser.add_argument("--source", type=str, choices=['Automatycznie', 'Ręcznie'], default='Automatycznie', help="Źródło tematu.")
    
    args = parser.parse_args()
    run_from_command_line(args)





