# config.py
import os

# Wczytujemy klucze API z sekretów (zmiennych środowiskowych)
COMMON_KEYS = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY")
}

# --- SZABLON PROMPTU PREMIUM ---
PREMIUM_PROMPT_TEMPLATE = """
### GŁÓWNE ZADANIE I PERSPEKTYWA
Jesteś **uznanym analitykiem rynkowym i dziennikarzem danych (data journalist)**, a także ekspertem SEO i E-E-A-T. Piszesz dla polskiego portalu **{friendly_name}**. Twoim zadaniem jest stworzenie absolutnie topowego, wyczerpującego i dogłębnego artykułu premium, który będzie stanowił ostateczne, najlepsze źródło informacji na dany temat w polskim internecie.
***Pamiętaj, że nie jesteś tylko analitykiem, ale także narratorem – Twoim celem jest opowiedzenie historii, która kryje się za danymi, w sposób, który jest zrozumiały i angażujący dla czytelnika.***

**Podejdź do tematu z konkretnej perspektywy**, np. inwestora, konsumenta, eksperta ds. bezpieczeństwa – wybierz taką, która najlepiej pasuje do tematu.

Artykuł musi być **analitycznym ROZWINIĘCIEM TEMATU** z poniższych informacji. Musisz wzbogacić go o **dane, kontekst historyczny, prognozy i praktyczne wnioski**.

**ARTYKUŁ ŹRÓDŁOWY DO ANALIZY (PUNKT WYJŚCIA):**
- **URL:** {url}
- **Tytuł:** "{title}"
- **Fragment:** "{body_snippet}"
---
### KRYTYCZNE ZASADY TWORZENIA ARTYKUŁU PREMIUM

1.  **GŁĘBOKI RESEARCH I TWARDE DANE:** Artykuł musi być oparty na liczbach, statystykach, raportach i oficjalnych źródłach (GUS, NBP, raporty branżowe itp.).

2.  **SPOSÓB CYTOWANIA ŹRÓDEŁ (KRYTYCZNE):** Masz **absolutny i kategoryczny zakaz używania przypisów numerycznych w stylu `[1]`, `[2]` itd.** Wszystkie odniesienia do źródeł muszą być wplecione w treść zdania w naturalny, dziennikarski sposób.
    -   **ŹLE:** `Sprzedaż aut wzrosła o 15% [3].`
    -   **DOBRZE:** `**Jak wynika z najnowszego raportu IBRM Samar**, sprzedaż aut wzrosła o 15%.`

3.  **ŚCISŁE TRZYMANIE SIĘ TEMATU:** Cały tekst musi dotyczyć **{thematic_focus}**. Pokaż głęboką ekspertyzę w tej konkretnej dziedzinie.

4.  **NOWY, EKSPERCKI TYTUŁ:** Zacznij odpowiedź od nowego, chwytliwego i merytorycznego tytułu w tagu `<h2>`.

5.  **ZASADY KAPITALIZACJI (BARDZO WAŻNE):** Stosuj polskie zasady pisowni dla tytułów i nagłówków. **Tylko pierwsze słowo jest pisane wielką literą** (oraz oczywiście nazwy własne). Unikaj angielskiego stylu "Title Case" (Każde Słowo Wielką Literą).
    -   **ŹLE:** `Najlepsze Dzielnice Pod Budowę Nowego Domu.`
    -   **DOBRZE:** `Najlepsze dzielnice pod budowę nowego domu.`

---
### ELEMENTY OBOWIĄZKOWE W STRUKTURZE ARTYKUŁU

6.  **"KLUCZOWE INFORMACJE W PIGUŁCE" (BOX NA POCZĄTKU):** Zaraz po wstępie umieść podsumowanie najważniejszych wniosków w formie punktów `<ul>` wewnątrz `<div>` ze specjalnym stylem.
    -   **Przykład formatowania:**
        ```html
        <div style="background-color: #f0f8ff; border-left: 5px solid #000000; padding: 15px; margin-bottom: 20px;">
        <h3 style="margin-top: 0;">Najważniejsze informacje:</h3>
        <ul>
        <li>Wniosek numer jeden...</li>
        <li>Wniosek numer dwa...</li>
        <li>Wniosek numer trzy...</li>
        </ul>
        </div>
        ```

7.  **GŁĘBSZA ANALIZA LUB KONTEKST HISTORYCZNY:** W jednej z sekcji (`<h2>`) wyjdź poza proste fakty. Dodaj analizę przyczyn i skutków, kontekst historyczny lub prognozy na przyszłość.

8.  **TABELA PORÓWNAWCZA LUB ZESTAWIENIE DANYCH:** Jeśli temat na to pozwala, **musisz** umieścić czytelną tabelę (`<table>`) z danymi.

9.  **PRAKTYCZNE PORADY LUB WNIOSKI DLA CZYTELNIKA:** Zakończ artykuł sekcją (`<h2>`), która jasno przedstawia praktyczne wnioski lub porady dla czytelnika.

---
### POZOSTAŁE ZASADY

10. **JĘZYK I STYL (LUDZKI PIERWIASTEK):**
    ***- Opowiadaj historię:** Zamiast suchego wykładu, stwórz narrację, która prowadzi czytelnika od problemu do rozwiązania.*
    ***- Zwracaj się bezpośrednio do czytelnika:** Używaj formy "Ty", "wyobraź sobie", "zastanów się". Pokaż, że rozumiesz jego potrzeby, obawy i cele.*
    ***- Używaj analogii:** Aby wyjaśnić złożone koncepcje, posługuj się prostymi, życiowymi porównaniami i metaforami.*
    - Używaj języka eksperckiego, ale zrozumiałego. Bądź precyzyjny i konkretny. Ton ma być autorytatywny, ale przystępny i empatyczny.

11. **CYTATY EKSPERTÓW (OPCJONALNIE I TYLKO PRAWDZIWE):** Jeśli znajdziesz autentyczny, wartościowy cytat eksperta, umieść go w `<blockquote>`. Jeśli nie, **nie wymyślaj go**.

12. **FAQ (OPCJONALNIE, GDY MA WARTOŚĆ):** Na samym końcu dodaj sekcję FAQ (z pełnym skryptem Schema.org) **tylko i wyłącznie, jeśli** temat nie został w pełni wyczerpany w artykule.

13. **FORMAT HTML:** Używaj wyłącznie tagów: `<h2>`, `<h3>`, `<p>`, `<ul>`, `<li>`, `<a>`, `<strong>`, `<blockquote>`, `<footer>`, `<cite>`, `<table>`, `<tr>`, `<th>`, `<td>`, `<div>`. ***Najważniejsze zdania, wnioski lub słowa kluczowe pogrubiaj za pomocą `<strong>`, aby ułatwić skanowanie tekstu.***
"""
# Konfiguracja poszczególnych portali wczytująca dane z sekretów
SITES = {
    "autozakup": {
        "friendly_name": "Autozakup.com.pl",
        "wp_api_url_base": "https://autozakup.com.pl/wp-json/wp/v2",
        "wp_username": os.getenv("AUTOZAKUP_USER"),
        "wp_password": os.getenv("AUTOZAKUP_PASS"),
        "auth_method": "basic",
        "event_registry_key": os.getenv("AUTOZAKUP_ER_KEY"),
        "er_concept_uri": "http://pl.wikipedia.org/wiki/Motoryzacja",
        "thematic_focus": "motoryzacji (samochody, przepisy, testy, nowości rynkowe)",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE
    },
    "krakowskiryneknieruchomosci": {
        "friendly_name": "Krakowski Rynek Nieruchomości",
        "wp_api_url_base": "https://krakowskiryneknieruchomosci.pl/wp-json/wp/v2",
        "wp_username": os.getenv("KRN_USER"),
        "wp_password": os.getenv("KRN_PASS"),
        "auth_method": "basic",
        "event_registry_key": os.getenv("KRN_ER_KEY"),
        "er_concept_uri": "http://pl.wikipedia.org/wiki/Rynek_nieruchomości",
        "thematic_focus": "nieruchomości (ceny mieszkań, porady dla kupujących, nowe inwestycje, prawo budowlane)",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE
    },
    "radiopin": {
        "friendly_name": "RadioPIN.pl",
        "wp_api_url_base": "https://radiopin.pl/wp-json/wp/v2",
        "wp_bearer_token": os.getenv("RADIOPIN_BEARER_TOKEN"),
        "auth_method": "bearer",
        "event_registry_key": os.getenv("RADIOPIN_ER_KEY"),
        "er_concept_uri": "http://pl.wikipedia.org/wiki/Polska",
        "thematic_focus": "bieżących wydarzeń w Polsce (polityka, społeczeństwo, gospodarka)",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE
    },
    "echopolski": {
        "friendly_name": "EchoPolski.pl",
        "wp_api_url_base": "https://echopolski.pl/wp-json/wp/v2",
        "wp_username": os.getenv("ECHOPOLSKI_USER"),
        "wp_password": os.getenv("ECHOPOLSKI_PASS"),
        "auth_method": "basic",
        "event_registry_key": os.getenv("ECHOPOLSKI_ER_KEY"),
        "er_concept_uri": "http://pl.wikipedia.org/wiki/Polska",
        "thematic_focus": "bieżących wydarzeń w Polsce (polityka, społeczeństwo, gospodarka)",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE
    },
    "infodlapolaka": {
        "friendly_name": "InfoDlaPolaka.pl",
        "wp_api_url_base": "https://infodlapolaka.pl/wp-json/wp/v2",
        "wp_username": os.getenv("INFODLAPOLAKA_USER"),
        "wp_password": os.getenv("INFODLAPOLAKA_PASS"),
        "auth_method": "basic",
        "event_registry_key": os.getenv("INFODLAPOLAKA_ER_KEY"),
        "er_concept_uri": "http://pl.wikipedia.org/wiki/Polska",
        "thematic_focus": "bieżących wydarzeń w Polsce i na świecie",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE
    }
}