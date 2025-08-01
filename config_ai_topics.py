# config_ai_topics.py
import os

# Wczytujemy klucze API z sekretów (zmiennych środowiskowych)
COMMON_KEYS = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY"),
    "PEXELS_API_KEY": os.getenv("PEXELS_API_KEY")
}

# --- SZABLON PROMPTU PREMIUM (pozostaje bez zmian) ---
PREMIUM_PROMPT_TEMPLATE = """
### GŁÓWNE ZADANIE I PERSPEKTYWA
Jesteś uznanym analitykiem rynkowym i dziennikarzem danych... (cała reszta promptu bez zmian)
"""

# Konfiguracja poszczególnych portali z promptami do generowania tematów
SITES = {
    "tylkoslask": {
        "friendly_name": "TylkoSlask.pl",
        "wp_api_url_base": "https://tylkoslask.pl/wp-json/wp/v2",
        "wp_username": os.getenv("TYLKOSLASK_USER"),
        "wp_password": os.getenv("TYLKOSLASK_PASS"),
        "auth_method": "basic",
        "ai_topic_prompt": "Zaproponuj 5 aktualnych, interesujących i lokalnych tematów na artykuł dla regionalnego portalu informacyjnego o Górnym Śląsku i Zagłębiu. Skup się na sprawach ważnych dla mieszkańców Katowic, Częstochowy, Sosnowca, Gliwic. Tematy powinny być świeże i dotyczyć ostatnich wydarzeń, np. z ostatniego tygodnia.",
        "thematic_focus": "Górnego Śląska i Zagłębia (portal regionalny)",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 3
    },
    "autozakup": {
        "friendly_name": "Autozakup.com.pl",
        "wp_api_url_base": "https://autozakup.com.pl/wp-json/wp/v2",
        "wp_username": os.getenv("AUTOZAKUP_USER"),
        "wp_password": os.getenv("AUTOZAKUP_PASS"),
        "auth_method": "basic",
        "ai_topic_prompt": "Zaproponuj 5 angażujących tematów na artykuł dla portalu motoryzacyjnego. Skup się na nowościach rynkowych, testach popularnych modeli aut, zmianach w przepisach drogowych lub praktycznych poradach dla kierowców w Polsce.",
        "thematic_focus": "motoryzacji (samochody, przepisy, testy, nowości rynkowe)",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 1
    },
    # --- Uzupełnij pozostałe portale w podobny sposób ---
    "krakowskiryneknieruchomosci": {
        "friendly_name": "Krakowski Rynek Nieruchomości",
        "wp_api_url_base": "https://krakowskiryneknieruchomosci.pl/wp-json/wp/v2",
        "wp_username": os.getenv("KRN_USER"),
        "wp_password": os.getenv("KRN_PASS"),
        "auth_method": "basic",
        "ai_topic_prompt": "Zaproponuj 5 tematów na artykuł dla portalu o nieruchomościach w Krakowie. Mogą dotyczyć analizy cen w dzielnicach, nowych inwestycji deweloperskich, porad dla kupujących pierwsze mieszkanie lub trendów na rynku najmu.",
        "thematic_focus": "nieruchomości (ceny mieszkań, porady dla kupujących, nowe inwestycje, prawo budowlane)",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 2
    }
    # ... i tak dalej dla reszty portali
}
