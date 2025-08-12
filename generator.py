# generator.py — wersja pełna, zgodna z Python 3.8/3.9

import json
import logging
import base64
import argparse
import textwrap
import re
import time
from datetime import datetime, timedelta
from typing import Optional, List

import requests
import openai
from bs4 import BeautifulSoup
from eventregistry import EventRegistry, QueryArticlesIter

# -----------------------
# KONFIG / LOGOWANIE
# -----------------------
try:
    from config import SITES, COMMON_KEYS
except ImportError:
    print("BŁĄD: Nie znaleziono pliku config.py.")
    exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("generator.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
)

# -----------------------
# KLIENCI API
# -----------------------
try:
    openai_client = openai.OpenAI(api_key=COMMON_KEYS.get("OPENAI_API_KEY"))
except Exception as e:
    logging.error(f"Nie udało się zainicjować klienta OpenAI: {e}")
    exit(1)

# -----------------------
# STAŁE / STOPWORDS
# -----------------------
STOPWORDS_PL = {
    "i", "oraz", "w", "we", "na", "do", "z", "ze", "o", "u", "od", "pod", "nad",
    "przy", "po", "za", "jest", "są", "to", "tych", "ten", "ta", "te", "tę",
    "naj", "dla", "roku", "województwa"
}

# -----------------------
# POMOCNICZE: Perplexity
# -----------------------
def _call_perplexity_api(prompt: str) -> Optional[str]:
    headers = {
        "Authorization": f"Bearer {COMMON_KEYS.get('PERPLEXITY_API_KEY')}",
        "Content-Type": "application/json",
    }
    payload = {"model": "sonar-pro", "messages": [{"role": "user", "content": prompt}]}
    try:
        r = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=400,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Błąd API Perplexity: {e}")
        return None

# -----------------------
# SANITIZERY / TEKST
# -----------------------
def strip_numeric_citations(html: str) -> str:
    """
    Usuwa formy przypisów: [1], [1,2], [1–3], (1), [^1], <sup>1</sup>, ^1
    i sekcje „Źródła/Bibliografia”. Nie rusza <a href="...">...</a>.
    """
    t = html or ""

    # <sup>1</sup>
    t = re.sub(r'<sup>\s*\d+\s*</sup>', '', t, flags=re.IGNORECASE)

    # [1], [1, 2], [1–3], [1-3]
    t = re.sub(r'\s*\[\s*\d+(?:\s*[,–-]\s*\d+)*\s*\]', '', t)

    # [^1]
    t = re.sub(r'\s*\[\^\d+\]', '', t)

    # (1) – tylko cyfry w nawiasie
    t = re.sub(r'\s*\(\s*\d+\\s*\)', '', t)

    # ^1 (np. na końcu zdania)
    t = re.sub(r'\s*\^\d+\b', '', t)

    # Sekcje „Źródła/Bibliografia”
    t = re.sub(
        r'<h2[^>]*>\s*(?:Źródła|Zrodla|Bibliografia)\s*</h2>.*?(?=(?:<h2|$))',
        '', t, flags=re.IGNORECASE | re.DOTALL
    )

    # Porządki typograficzne
    t = re.sub(r'\s+([,.;:!?])', r'\1', t)
    t = re.sub(r'[ \t]{2,}', ' ', t)
    t = re.sub(r'\n{3,}', '\n\n', t)

    return t


def enforce_anchor_nofollow(html: str) -> str:
    """
    Dodaje rel="nofollow noopener" i target="_blank" do wszystkich linków <a href="http...">.
    """
    if not html:
        return html
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if href.startswith("http"):
            rel = a.get("rel") or []
            if isinstance(rel, str):
                rel = [x.strip() for x in rel.split()]
            rel_set = set(rel) | {"nofollow", "noopener"}
            a["rel"] = " ".join(sorted(rel_set))
            if not a.get("target"):
                a["target"] = "_blank"
    return str(soup)


def _extract_keywords_pl(s: str) -> List[str]:
    words = re.findall(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9]+", (s or "").lower())
    return [w for w in words if len(w) >= 4 and w not in STOPWORDS_PL]


def title_respects_keyword(generated_title: str, manual_kw: str) -> bool:
    """Sprawdza semantyczną zgodność tytułu z frazą użytkownika."""
    kw_set = set(_extract_keywords_pl(manual_kw))
    gen_set = set(_extract_keywords_pl(generated_title))
    if not kw_set:
        return True
    common = len(kw_set & gen_set)
    return common >= max(1, len(kw_set) - 1)


def rewrite_title_to_match_keyword(bad_title: str, keyword: str) -> str:
    """
    Próbuje poprawić tytuł przez OpenAI; jeśli się nie uda – bezpieczny fallback.
    Zwraca gotowy <h2>...</h2>.
    """
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=60,
            messages=[{
                "role": "user",
                "content": (
                    "Popraw tytuł artykułu tak, aby był zgodny z frazą kluczową "
                    "(lub jej bardzo bliskim wariantem), nie zawężał zakresu, "
                    "stosował polskie zasady kapitalizacji i miał maks. 70 znaków. "
                    "Zwróć wyłącznie tytuł w tagu <h2>.\n"
                    "FRAZA: " + keyword + "\n"
                    "AKTUALNY TYTUŁ: " + bad_title
                )
            }]
        )
        fixed = resp.choices[0].message.content.strip()
        if not fixed.lower().startswith("<h2"):
            fixed_text = re.sub(r"</?h2[^>]*>", "", fixed).strip()
            return f"<h2>{fixed_text[:70]}</h2>"
        return fixed
    except Exception as e:
        logging.warning(f"Nie udało się poprawić tytułu przez AI: {e}")

    safe = (keyword or bad_title or "Artykuł").strip()
    safe = safe[0].upper() + safe[1:] if safe else "Artykuł"
    return f"<h2>{safe[:70]}</h2>"

# -----------------------
# WORDPRESS / EVENT REG.
# -----------------------
def get_auth_header(site_config):
    if site_config.get("auth_method") == "bearer":
        return {"Authorization": f"Bearer {site_config.get('wp_bearer_token')}"}
    credentials = f"{site_config.get('wp_username')}:{site_config.get('wp_password')}"
    token = base64.b64encode(credentials.encode()).decode("utf-8")
    return {"Authorization": f"Basic {token}"}


def fetch_categories(site_config):
    """
    Pobiera wszystkie dostępne kategorie z WordPressa (lista krotek: [(id, name), ...]).
    Zgodne z Twoim app.py (ręczny wybór kategorii).
    """
    base_url = site_config.get("wp_api_url_base")
    if not base_url:
        logging.warning("Brak wp_api_url_base w konfiguracji portalu.")
        return []

    url = f"{base_url}/categories"
    headers = get_auth_header(site_config)

    all_categories = []
    page = 1
    while True:
        try:
            r = requests.get(
                url,
                headers=headers,
                params={"per_page": 100, "page": page},
                timeout=20
            )
            r.raise_for_status()
            data = r.json()
            if not data:
                break
            all_categories.extend([(cat["id"], cat["name"]) for cat in data])
            page += 1
        except Exception as e:
            logging.warning(f"Nie udało się pobrać kategorii z {url}: {e}")
            break

    return all_categories


def get_event_registry_topics(site_config):
    logging.info("Pobieranie tematów z EventRegistry...")
    try:
        er = EventRegistry(apiKey=site_config["event_registry_key"])

        date_end = datetime.now().date()
        date_start = (date_end - timedelta(days=3)).isoformat()
        date_end = date_end.isoformat()

        uris = site_config.get("er_concept_uris") or [site_config["er_concept_uri"]]

        complex_query = {
            "$query": {
                "$and": [
                    {"$or": [{"conceptUri": uri} for uri in uris]},
                    {"dateStart": date_start, "dateEnd": date_end, "lang": "pol"},
                ]
            }
        }

        qiter = QueryArticlesIter.initWithComplexQuery(complex_query)

        for article in qiter.execQuery(er, sortBy="date", maxItems=1):
            return {
                "title": article.get("title"),
                "body_snippet": article.get("body", "")[:700],
                "url": article.get("url"),
                "image_url": article.get("image"),
                "source_name": article.get("source", {}).get("title"),
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
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return {cat["name"]: cat["id"] for cat in r.json()}
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
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_content}],
            temperature=0.0,
            max_tokens=30,
        )
        raw_output = resp.choices[0].message.content.strip()
        selected = [c.strip() for c in raw_output.split(",") if c.strip() in available_categories_names]
        return selected[:2] if selected else [fallback_category]
    except Exception as e:
        logging.error(f"Błąd podczas wyboru kategorii przez AI: {e}")
        return [fallback_category]


def generate_tags_ai(title, content):
    logging.info("Generowanie tagów AI...")
    prompt = [
        {"role": "system", "content": "Wygeneruj 5-7 trafnych tagów (1-2 słowa każdy, po polsku) do artykułu. Zwróć jako listę JSON, np. [\"tag1\", \"tag2\"]."},
        {"role": "user", "content": f"Tytuł: {title}\nFragment:{content[:1000]}"},
    ]
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt,
            temperature=0.2,
            max_tokens=100,
            response_format={"type": "json_object"},
        )
        tags_data = json.loads(resp.choices[0].message.content)
        return tags_data if isinstance(tags_data, list) else tags_data.get("tags", [])
    except Exception as e:
        logging.error(f"Błąd podczas generowania tagów AI: {e}")
        return []


def get_or_create_term_id(name, term_type, site_config):
    headers = get_auth_header(site_config)
    url = f"{site_config['wp_api_url_base']}/{term_type}"
    try:
        r = requests.get(url, headers=headers, params={"search": name}, timeout=20)
        r.raise_for_status()
        for term in r.json():
            if term.get("name", "").lower() == name.lower():
                return term["id"]
        logging.info(f"Termin '{name}' nie istnieje. Tworzenie nowego ({term_type})...")
        create_resp = requests.post(
            url, headers=headers, json={"name": name, "slug": name.lower().replace(" ", "-")}, timeout=20
        )
        create_resp.raise_for_status()
        return create_resp.json()["id"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Błąd podczas obsługi terminu '{name}': {e}")
        return None


def upload_image_to_wp(image_source, article_title, site_config):
    if not image_source:
        return None
    img_content, content_type = None, "image/jpeg"
    if isinstance(image_source, str) and image_source.startswith("http"):
        logging.info(f"Pobieranie obrazka z URL: {image_source}")
        try:
            img_r = requests.get(image_source, stream=True, timeout=20)
            img_r.raise_for_status()
            img_content = img_r.content
            content_type = img_r.headers.get("content-type", "image/jpeg")
        except requests.exceptions.RequestException as e:
            logging.error(f"Błąd podczas pobierania obrazka z URL: {e}")
            return None
    else:
        logging.info("Przetwarzanie wgranego obrazka...")
        img_content, content_type = image_source.getvalue(), image_source.type
    try:
        headers = get_auth_header(site_config)
        ascii_title = article_title.encode("ascii", "ignore").decode("ascii")
        safe_filename_base = "".join(c for c in ascii_title if c.isalnum() or c in " ").strip().replace(" ", "_")
        filename = f"{safe_filename_base[:50]}_img.jpg"
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        headers["Content-Type"] = content_type
        wp_r = requests.post(f"{site_config['wp_api_url_base']}/media", headers=headers, data=img_content, timeout=60)
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
    headers["Content-Type"] = "application/json"
    try:
        r = requests.post(url, headers=headers, json=data_to_publish, timeout=60)
        r.raise_for_status()
        logging.info(f"Artykuł opublikowany pomyślnie! URL: {r.json().get('link')}")
        return r.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Błąd podczas publikacji w WordPress: {e}")
        try:
            logging.error(f"Odpowiedź serwera: {r.text}")
        except Exception:
            pass
        return None

# -----------------------
# KROK 1/2/3 GENEROWANIA
# -----------------------
def step1_research(topic_data, site_config):
    """Krok 1: research; bez przypisów numerycznych, dopuszczalne linki <a>."""
    logging.info("--- KROK 1: Rozpoczynam research i syntezę danych... ---")
    prompt = textwrap.dedent(f"""
        Twoim zadaniem jest przeprowadzenie dogłębnego researchu na temat z poniższych danych. Przeanalizuj podany URL i/lub tematykę i znajdź dodatkowe, wiarygodne źródła.
        **NIE PISZ ARTYKUŁU.** Zbierz i przedstaw kluczowe informacje.

        **ZASADY CYTOWANIA W TYM ZADANIU:**
        - Nie używaj przypisów numerycznych ani znaczników przypisów: [1], (1), [^1], <sup>1</sup>.
        - Gdy wskazujesz źródło, rób to deskryptywnie (np. „Jak wynika z danych GUS z 2025 r…”)
          lub jako link HTML: <a href="https://..." rel="nofollow">Nazwa źródła</a>.

        **TEMAT DO ANALIZY:**
        - URL: {topic_data.get('url', 'Brak')}
        - Tytuł: "{topic_data.get('title', '')}"
        - Kontekst: "{topic_data.get('body_snippet', '')}"

        **ZNAJDŹ I WYPISZ W PUNKTACH:**
        - Kluczowe fakty, liczby, statystyki (z datą/instytucją).
        - Nazwiska ekspertów i ich tezy (+ cytaty).
        - Ważne daty i nazwy oficjalnych dokumentów/raportów.
        - Główne argumenty „za” i „przeciw” (jeśli dotyczy).
        - Potencjalny materiał do tabeli porównawczej.
        - **Elementy narracyjne** (ludzki kontekst, anegdoty, punkty zwrotne).

        Zwróć odpowiedź jako zwięzłą, dobrze zorganizowaną listę punktów.
    """)
    return _call_perplexity_api(prompt)


def step2_create_outline(research_data, site_config, keyword=None):
    """Krok 2: outline; pilnowanie frazy kluczowej i braku zawężania tematu."""
    logging.info("--- KROK 2: Tworzę kreatywny i szczegółowy plan artykułu... ---")

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
    """Krok 3: finalny artykuł; zakaz przypisów numerycznych, dozwolone linki HTML."""
    logging.info("--- KROK 3: Piszę finalny artykuł... To może potrwać kilka minut. ---")
    prompt_template = site_config["prompt_template"]

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
        **ZASADY CYTOWANIA (BEZ PRZYPISÓW NUMERYCZNYCH):**
        - Bezwzględny zakaz form: [1], [2], (1), [^1], <sup>1</sup>, „Bibliografia/Źródła” jako osobna sekcja.
        - Źródła podawaj deskryptywnie w zdaniu (np. „Jak wynika z raportu NBP z lipca 2025…”).
        - To wymaganie jest zamierzone — **nie odmawiaj** wykonania zadania z powodu braku przypisów numerycznych.
    """)

    final_prompt = textwrap.dedent(f"""
        Twoim zadaniem jest napisanie kompletnego artykułu premium na podstawie poniższych danych i planu.
        Pisz angażująco i narracyjnie. Lead 2–3 zdania, konkretny.

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


def step_news_article(research_data, site_config, topic_data, keyword=None):
    """Krótki news (300–400 słów) — bez przypisów numerycznych, linki HTML dozwolone."""
    manual_title_rule = ""
    if keyword:
        kw = (keyword or "").strip()
        manual_title_rule = textwrap.dedent(f"""
            **REGUŁA TYTUŁU (KRYTYCZNE):**
            - Tytuł w `<h2>` musi zawierać frazę kluczową lub jej bardzo bliski wariant: "{kw}".
            - Nie zawężaj zakresu względem frazy użytkownika.
        """)

    anti_footnotes_rule = textwrap.dedent("""
        **ZASADY CYTOWANIA (BEZ PRZYPISÓW NUMERYCZNYCH):**
        - Zakaz form: [1], [2], (1), [^1], <sup>1</sup>, sekcje „Bibliografia/Źródła”.
        - Dopuszczalne: deskryptywne wskazanie źródła lub link HTML
          <a href="https://..." rel="nofollow">Nazwa źródła</a>.
    """)

    prompt = textwrap.dedent(f"""
        Jesteś dziennikarzem newsowym. Masz zebrać i skondensować poniższe informacje w **krótki artykuł (300–400 słów)**:
        - Najważniejsze fakty i liczby dotyczące: "{topic_data.get('title')}" ({topic_data.get('url')})
        - Opinie ekspertów (prawdziwe cytaty - jeśli są).
        - Własne podsumowanie artykułu z nieformalną puentą, obiektywnie.

        {manual_title_rule}
        {anti_footnotes_rule}

        Dane do analizy:
        {research_data}

        ---
        ZASADY PISANIA:
        {site_config['prompt_template']}

        Zwróć gotowy tekst w HTML, używając tylko tagów <h2>, <p>, <ul>, <li>, <strong>, <blockquote>, <a>.
    """)
    return _call_perplexity_api(prompt)

# -----------------------
# WORKFLOW: PREMIUM
# -----------------------
def run_generation_process(site_key, topic_source, manual_topic_data, category_id=None):
    """Główna funkcja wykonawcza (premium)."""
    site_config = SITES[site_key]
    site_config["site_key"] = site_key

    # Temat
    topic_data = manual_topic_data if topic_source == "Ręcznie" else get_event_registry_topics(site_config)
    if not topic_data:
        return "BŁĄD: Nie udało się uzyskać tematu. Sprawdź Event Registry lub dane wprowadzone ręcznie."

    # Krok 1: Research
    research_data = step1_research(topic_data, site_config)
    if not research_data:
        return "BŁĄD: Krok 1 (Research) nie powiódł się. Sprawdź logi."
    logging.info("--- WYNIK RESEARCHU ---\n" + research_data)

    # Fraza tytułu (ręcznie podana)
    keyword_for_title = None
    if topic_source == "Ręcznie":
        keyword_for_title = (topic_data.get("title") or "").strip()
        if keyword_for_title:
            logging.info(f"Wykryto ręczne słowo kluczowe dla tytułu: '{keyword_for_title}'")

    # Krok 2: Outline
    outline = step2_create_outline(research_data, site_config, keyword=keyword_for_title)
    if not outline:
        return "BŁĄD: Krok 2 (Planowanie) nie powiódł się. Sprawdź logi."
    logging.info("--- WYGENEROWANY PLAN ARTYKUŁU ---\n" + outline)

    # Krok 3: Artykuł
    generated_html = step3_write_article(research_data, outline, site_config, keyword=keyword_for_title)
    if not generated_html:
        return "BŁĄD: Krok 3 (Pisanie) nie powiódł się. Sprawdź logi."

    # Parsowanie + kontrola tytułu
    soup = BeautifulSoup(generated_html, "html.parser")
    h2_tag = soup.find("h2")
    current_title = h2_tag.get_text(strip=True) if h2_tag else (topic_data.get("title") or "Brak tytułu")

    if keyword_for_title and not title_respects_keyword(current_title, keyword_for_title):
        logging.info(f"Tytuł wymaga korekty względem frazy: '{keyword_for_title}' -> '{current_title}'")
        fixed_h2_html = rewrite_title_to_match_keyword(current_title, keyword_for_title)
        fixed_h2_soup = BeautifulSoup(fixed_h2_html, "html.parser")
        if h2_tag:
            h2_tag.replace_with(fixed_h2_soup)
        else:
            soup.insert(0, fixed_h2_soup)
        h2_tag = soup.find("h2")
        current_title = h2_tag.get_text(strip=True) if h2_tag else current_title

    # Usuń <h2> z treści (WP ma tytuł osobno)
    for t in soup.find_all("h2"):
        t.decompose()

    post_title = (current_title or topic_data.get("title") or "Brak tytułu").strip()
    post_content = str(soup)

    # Sanitizacja: usuń przypisy + dołóż nofollow
    post_content = strip_numeric_citations(post_content)
    post_content = enforce_anchor_nofollow(post_content)

    # Kategorie
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

    # Tagi
    tags_list = generate_tags_ai(post_title, post_content) or []
    tag_ids = [tid for tid in (get_or_create_term_id(tag, "tags", site_config) for tag in tags_list) if tid]

    # Obraz wyróżniony
    featured_media_id = upload_image_to_wp(topic_data.get("image_url"), post_title, site_config)

    # Publikacja
    data_to_publish = {
        "title": post_title,
        "content": post_content,
        "status": "publish",
        "categories": [category_id] if category_id else [],
        "tags": tag_ids,
    }
    if featured_media_id:
        data_to_publish["featured_media"] = featured_media_id

    result = publish_to_wp(data_to_publish, site_config)
    if result and result.get("link"):
        return f"Artykuł opublikowany pomyślnie! Link: {result.get('link')}"
    else:
        return "BŁĄD: Publikacja nie powiodła się. Sprawdź logi."

# -----------------------
# WORKFLOW: NEWS
# -----------------------
def run_news_process(site_key, topic_source, manual_topic_data, category_id=None):
    """Workflow dla artykułu newsowego (krótsza forma) + publikacja na WP."""
    site_config = SITES[site_key]
    site_config["site_key"] = site_key

    # Temat
    topic_data = manual_topic_data if topic_source == "Ręcznie" else get_event_registry_topics(site_config)
    if not topic_data:
        return "BŁĄD: Nie udało się uzyskać tematu."

    # Research
    research_data = step1_research(topic_data, site_config)
    if not research_data:
        return "BŁĄD: Research nie powiódł się."

    # Fraza do tytułu
    keyword_for_title = None
    if topic_source == "Ręcznie" and manual_topic_data:
        keyword_for_title = (manual_topic_data.get("title") or "").strip()
        if keyword_for_title:
            logging.info(f"[NEWS] Ręczna fraza tytułu: '{keyword_for_title}'")

    # Artykuł newsowy
    news_html = step_news_article(research_data, site_config, topic_data, keyword=keyword_for_title)
    if not news_html:
        return "BŁĄD: Pisanie newsowego artykułu nie powiodło się."

    # Parsowanie + kontrola tytułu
    soup = BeautifulSoup(news_html, "html.parser")
    h2 = soup.find("h2")
    current_title = h2.get_text(strip=True) if h2 else (topic_data.get("title") or "Brak tytułu")

    if keyword_for_title and not title_respects_keyword(current_title, keyword_for_title):
        logging.info(f"[NEWS] Korekta tytułu względem frazy: '{keyword_for_title}' -> '{current_title}'")
        fixed_h2_html = rewrite_title_to_match_keyword(current_title, keyword_for_title)
        fixed_h2_soup = BeautifulSoup(fixed_h2_html, "html.parser")
        if h2:
            h2.replace_with(fixed_h2_soup)
        else:
            soup.insert(0, fixed_h2_soup)
        h2 = soup.find("h2")
        current_title = h2.get_text(strip=True) if h2 else current_title

    # Usuń <h2> z treści (WP ma tytuł osobno)
    for x in soup.find_all("h2"):
        x.decompose()

    post_title = (current_title or topic_data.get("title") or "Brak tytułu").strip()
    post_content = str(soup)

    # Sanitizacja
    post_content = strip_numeric_citations(post_content)
    post_content = enforce_anchor_nofollow(post_content)

    # Kategorie
    all_categories = get_all_wp_categories(site_config)
    if category_id is not None:
        logging.info(f"[NEWS] Użyto ręcznie wybranej kategorii ID={category_id}")
    else:
        if not all_categories:
            logging.warning("[NEWS] Nie udało się pobrać kategorii z WP. Domyślne ID=1.")
            category_id = 1
        else:
            chosen_names = choose_category_ai(post_title, post_content, list(all_categories.keys()))
            chosen_name = chosen_names[0] if isinstance(chosen_names, list) and chosen_names else "Bez kategorii"
            category_id = all_categories.get(chosen_name, 1)

    # Tagi
    tags_list = generate_tags_ai(post_title, post_content) or []
    tag_ids = [tid for tid in (get_or_create_term_id(tag, "tags", site_config) for tag in tags_list) if tid]

    # Obraz wyróżniony
    featured_media_id = upload_image_to_wp(topic_data.get("image_url"), post_title, site_config)

    # Publikacja
    data_to_publish = {
        "title": post_title,
        "content": post_content,
        "status": "publish",
        "categories": [category_id],
        "tags": tag_ids,
    }
    if featured_media_id:
        data_to_publish["featured_media"] = featured_media_id

    result = publish_to_wp(data_to_publish, site_config)
    if result and result.get("link"):
        return f"Artykuł newsowy opublikowany! Link: {result.get('link')}"
    else:
        return "BŁĄD: Publikacja newsowego artykułu nie powiodła się."

# -----------------------
# PEXELS
# -----------------------
def find_pexels_images_list(query, count=15):
    """
    Wyszukuje w Pexels listę zdjęć i zwraca ich dane (ID, URL-e, autor).
    """
    pexels_api_key = COMMON_KEYS.get("PEXELS_API_KEY")
    if not pexels_api_key:
        logging.warning("Brak klucza PEXELS_API_KEY. Pomijam wyszukiwanie obrazka.")
        return []

    try:
        from pexels_api import API
        api = API(pexels_api_key)
        logging.info(f"Wyszukiwanie {count} obrazków w Pexels dla zapytania: '{query}'")
        api.search(query, page=1, results_per_page=count)
        photos = api.get_entries()

        if photos:
            results = [{
                "id": photo.id,
                "photographer": photo.photographer,
                "preview_url": getattr(photo, "medium", None),
                "original_url": getattr(photo, "large", None)
            } for photo in photos]
            logging.info(f"Znaleziono {len(results)} obrazków.")
            return results
        else:
            logging.warning(f"Nie znaleziono żadnego obrazka dla zapytania: '{query}'")
            return []
    except Exception as e:
        logging.error(f"Błąd podczas komunikacji z API Pexels: {e}")
        return []

# -----------------------
# CLI
# -----------------------
def run_from_command_line(args):
    """Uruchamia proces generowania na podstawie argumentów z wiersza poleceń."""
    site_key = args.site
    article_type = args.type
    topic_source = args.source
    manual_topic_data = {}

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generator artykułów AI.")
    parser.add_argument("--site", type=str, required=True, help="Klucz portalu (np. autozakup, radiopin).")
    parser.add_argument("--type", type=str, choices=["premium", "news"], default="premium", help="Typ artykułu do wygenerowania.")
    parser.add_argument("--source", type=str, choices=["Automatycznie", "Ręcznie"], default="Automatycznie", help="Źródło tematu.")
    args = parser.parse_args()
    run_from_command_line(args)

