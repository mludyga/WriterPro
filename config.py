# config.py
import os

# Wczytujemy klucze API z sekretów (zmiennych środowiskowych)
COMMON_KEYS = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY"),
    "PEXELS_API_KEY": os.getenv("PEXELS_API_KEY") # <-- To jest nowa, dodana linia
}

# --- SZABLON PROMPTU PREMIUM (z jednoznacznym zakazem przypisów i linków) ---
PREMIUM_PROMPT_TEMPLATE = """
### GŁÓWNE ZADANIE I PERSPEKTYWA
Jesteś **doświadczonym reporterem-analitykiem**, który potrafi tłumaczyć skomplikowane dane i decyzje urzędowe na **praktyczną opowieść o ludziach i ich życiu**. Twoim celem nie jest napisanie suchego raportu, ale stworzenie angażującej historii, w której liczby są tylko ilustracją ludzkich spraw.
***Pamiętaj, że nie jesteś tylko analitykiem, ale także narratorem – Twoim celem jest opowiedzenie historii, która kryje się za danymi, w sposób, który jest zrozumiały i angażujący dla czytelnika. W tekście nigdy nie wspominaj, że jesteś ekspertem czy analitykiem, tylko pisz w takim stylu.***

**Podejdź do tematu z konkretnej perspektywy**, np. inwestora, konsumenta, eksperta ds. bezpieczeństwa – wybierz taką, która najlepiej pasuje do tematu.

Artykuł musi być **analitycznym ROZWINIĘCIEM TEMATU** z poniższych informacji. Musisz wzbogacić go o **dane, kontekst historyczny, prognozy i praktyczne wnioski**.

**ARTYKUŁ ŹRÓDŁOWY DO ANALIZY (PUNKT WYJŚCIA):**
- **URL:** {url}
- **Tytuł:** "{title}"
- **Fragment:** "{body_snippet}"
---
### KRYTYCZNE ZASADY TWORZENIA ARTYKUŁU PREMIUM

1.  **GŁĘBOKI RESEARCH I TWARDE DANE:** Artykuł musi być oparty na liczbach, statystykach, raportach i oficjalnych źródłach (GUS, NBP, raporty branżowe itp.).

2.  **ABSOLUTNY ZAKAZ PRZYPISÓW I LINKÓW DO ŹRÓDEŁ:** 
    - Masz **bezwzględny zakaz** używania jakichkolwiek form przypisów lub odsyłaczy: **[1]**, **[2]**, **(1)**, **[^1]**, **<sup>1</sup>**, „Bibliografia”, „Źródła” na końcu, itp.
    - **Nie wstawiaj surowych URL-i ani hiperłączy do źródeł.** Zamiast tego **wspominaj źródło deskryptywnie w zdaniu**, np.: *„Jak podaje ‘Dziennik Gazeta Prawna’…”, „Z danych GUS za 2024 r. wynika, że…”, „Według NBP w raporcie z lipca 2025…”*.
    - **Wyjątki:** dozwolone są liczby w nawiasach, gdy są częścią nazwy modelu/aktu/roku (np. *BMW i3*, *art. 15*, *2024*), ale **nigdy** nie używaj nawiasowych numerów, które mogą wyglądać jak przypisy.

2a. **KONKRETY ZAMIAST OGÓLNIKÓW:** Masz zakaz pisania ogólnych sformułowań typu "według danych" bez podania konkretnej liczby lub wniosku. Jeśli powołujesz się na źródło, przytocz z niego konkretny, mierzalny fakt.
    - **ŹLE:** `W ostatnich latach obserwowano wzrost zainteresowania tematem, co potwierdzają statystyki.`
    - **DOBRZE:** `Zgodnie z danymi GUS za rok 2024, zainteresowanie tematem wzrosło o 12% w stosunku do roku poprzedniego.`

3.  **ŚCISŁE TRZYMANIE SIĘ TEMATU:** Cały tekst musi dotyczyć **{thematic_focus}**. Pokaż głęboką ekspertyzę w tej konkretnej dziedzinie.

4.  **TYTUŁ SEO Z FRAZĄ KLUCZOWĄ:** Zacznij od nowego tytułu w tagu `<h2>`. Tytuł musi zawierać frazę kluczową (lub jej bardzo bliską wersję), być krótki (maks. 70 znaków), jasny i zgodny z zasadami SEO. Unikaj ozdobników, clickbaitów i zbyt ogólnych zwrotów. Liczy się precyzja i trafność.

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

7.  **GŁĘBSZA ANALIZA LUB KONTEKST HISTORYCZNY (nie umieszczaj tych słów w podnagłówku):** W jednej z sekcji (`<h2>`) wyjdź poza proste fakty. Dodaj analizę przyczyn i skutków, kontekst historyczny lub prognozy na przyszłość. 

8.  **TABELA PORÓWNAWCZA LUB ZESTAWIENIE DANYCH (nie umieszczaj tych słów w podnagłówku):** Jeśli temat na to pozwala, **musisz** umieścić czytelną tabelę (`<table>`) z danymi.

9.  **PRAKTYCZNE PORADY LUB WNIOSKI DLA CZYTELNIKA (nie umieszczaj tych słów w podnagłówku):** Zakończ artykuł sekcją (`<h2>`), która jasno przedstawia praktyczne wnioski lub porady dla czytelnika.

---
### POZOSTAŁE ZASADY

10. **JĘZYK I STYL (LUDZKI PIERWIASTEK):**
    - Zmieniaj długość zdań. Przeplataj krótkie (3–6 słów) z dłuższymi (20+). Twórz naturalny rytm, jak w rozmowie.
    - Używaj **zwrotów przejściowych**: "Warto to podkreślić", "Ale to nie wszystko", "Zacznijmy od początku", "Co to oznacza w praktyce?".
    - Zakończ akapity **mini-puentą lub prowokującą myślą** – coś, co zatrzymuje czytelnika na moment.
    - Używaj **pytających form** ("Co zatem zrobić?", "Dlaczego to się dzieje?") i **komentarzy narratora**.
    ***- Opowiadaj historię:** Zamiast suchego wykładu, stwórz narrację, która prowadzi czytelnika od problemu do rozwiązania.*
    ***- Zwracaj się bezpośrednio do czytelnika:** Używaj formy "Ty", "wyobraź sobie", "zastanów się". Pokaż, że rozumiesz jego potrzeby, obawy i cele.*
    ***- Używaj analogii:** Aby wyjaśnić złożone koncepcje, posługuj się prostymi, życiowymi porównaniami i metaforami.*
    - Używaj języka eksperckiego, ale zrozumiałego. Bądź precyzyjny i konkretny. Ton ma być autorytatywny, ale przystępny i empatyczny.
    - Pisz w sposób zróżnicowany: krótkie, średnie i dłuższe zdania przeplataj. Nie twórz sztywnego, jednostajnego rytmu.

    ### ZASADY STYLU "LUDZKIEGO"
    - Pisz w stylu konwersacyjnym, ale eksperckim.
    - Twórz rytm – zróżnicowana długość zdań.
    - Unikaj zbyt formalnego tonu. Lepiej: "To może być problem" niż "Niniejsze dane wskazują na potencjalne zagrożenie."
    - Angażuj. Zwracaj się do czytelnika. Dawaj przykłady, anegdoty, odniesienia do życia codziennego.

11. **CYTATY EKSPERTÓW (OPCJONALNIE I TYLKO PRAWDZIWE):** Jeśli znajdziesz autentyczny, wartościowy cytat eksperta, umieść go w `<blockquote>`. Jeśli nie, **nie wymyślaj go**.

12. **FAQ (OPCJONALNIE, GDY MA WARTOŚĆ):** Na samym końcu dodaj sekcję FAQ (z pełnym skryptem Schema.org) **tylko i wyłącznie, jeśli** temat nie został w pełni wyczerpany w artykule.

13. **FORMAT HTML:** Używaj wyłącznie tagów: `<h2>`, `<h3>`, `<p>`, `<ul>`, `<li>`, `<a>`, `<strong>`, `<blockquote>`, `<footer>`, `<cite>`, `<table>`, `<tr>`, `<th>`, `<td>`, `<div>`. ***Najważniejsze zdania, wnioski lub słowa kluczowe pogrubiaj za pomocą `<strong>`, aby ułatwić skanowanie tekstu.***

---
### AUTOKONTROLA PRZED ODDANIEM TEKSTU (OBOWIĄZKOWE)
- Przeskanuj całość i usuń wszelkie wzorce, które wyglądają jak przypisy lub linki: `[\d+]`, `(\\d+)`, `[^\\d+]`, `<sup>\\d+</sup>`, słowa „Bibliografia”, „Źródła”, surowe `http://` lub `https://`.
- Jeśli znajdziesz taki element, **przeredaguj** fragment na formę deskryptywną ze wskazaniem źródła w zdaniu (bez linkowania).
- Sprawdź, że każde odwołanie do „danych”, „raportu”, „statystyk” zawiera **konkret** (liczbę/rok/instytucję) i **nazwę źródła w tekście**.
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
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 1
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
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 2
    },
    "radiopin": {
        "friendly_name": "RadioPIN.pl",
        "wp_api_url_base": "https://radiopin.pl/wp-json/wp/v2",
        "wp_bearer_token": os.getenv("RADIOPIN_BEARER_TOKEN"),
        "auth_method": "bearer",
        "event_registry_key": os.getenv("RADIOPIN_ER_KEY"),
        "er_concept_uri": "http://pl.wikipedia.org/wiki/Polska",
        "thematic_focus": "bieżących wydarzeń w Polsce (polityka, społeczeństwo, gospodarka)",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 17
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
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 7
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
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 1
    },
    "autocentrumgroup": {
        "friendly_name": "AutoCentrumGroup.pl",
        "wp_api_url_base": "https://autocentrumgroup.pl/wp-json/wp/v2",
        "wp_username": os.getenv("AUTOCENTRUM_USER"),
        "wp_password": os.getenv("AUTOCENTRUM_PASS"),
        "auth_method": "basic",
        "event_registry_key": os.getenv("AUTOCENTRUM_ER_KEY"),
        "er_concept_uri": "http://pl.wikipedia.org/wiki/Motoryzacja",
        "er_concept_uris": [
          "http://pl.wikipedia.org/wiki/Motoryzacja",
          "http://pl.wikipedia.org/wiki/Samochód_osobowy"
        ],
        "thematic_focus": "motoryzacji (samochody, przepisy, testy, nowości rynkowe)",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 1
    },
    "tylkoslask": {
        "friendly_name": "TylkoSlask.pl",
        "wp_api_url_base": "https://tylkoslask.pl/wp-json/wp/v2",
        "wp_username": os.getenv("TYLKOSLASK_USER"),
        "wp_password": os.getenv("TYLKOSLASK_PASS"),
        "auth_method": "basic",
        "event_registry_key": os.getenv("TYLKOSLASK_ER_KEY"),
        "er_concept_uris": [
            "http://en.wikipedia.org/wiki/Silesian_Voivodeship",
            "http://en.wikipedia.org/wiki/Katowice",
            "http://en.wikipedia.org/wiki/Częstochowa",
            "http://en.wikipedia.org/wiki/Sosnowiec",
            "http://en.wikipedia.org/wiki/Gliwice",
            "http://en.wikipedia.org/wiki/Zabrze",
            "http://en.wikipedia.org/wiki/Bytom",
            "http://en.wikipedia.org/wiki/Ruda_Śląska",
            "http://en.wikipedia.org/wiki/Rybnik",
            "http://en.wikipedia.org/wiki/Tychy",
            "http://en.wikipedia.org/wiki/Dąbrowa_Górnicza",
            "http://en.wikipedia.org/wiki/Chorzów",
            "http://en.wikipedia.org/wiki/Bielsko-Biała",
            "http://en.wikipedia.org/wiki/Jastrzębie-Zdrój",
            "http://en.wikipedia.org/wiki/Mysłowice"
        ],
        "thematic_focus": "Górnego Śląska i Zagłębia (portal regionalny)",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 3
    },

    "tylkoslask2": {
        "friendly_name": "TylkoSlask.pl2",
        "wp_api_url_base": "https://tylkoslask.pl/wp-json/wp/v2",
        "wp_username": os.getenv("TYLKOSLASK_USER"),
        "wp_password": os.getenv("TYLKOSLASK_PASS"),
        "auth_method": "basic",
        "event_registry_key": os.getenv("TYLKOSLASK_ER_KEY"),
        "er_concept_uris": [
            "http://en.wikipedia.org/wiki/Jaworzno",
            "http://en.wikipedia.org/wiki/Siemianowice_Śląskie",
            "http://en.wikipedia.org/wiki/Żory",
            "http://en.wikipedia.org/wiki/Tarnowskie_Góry",
            "http://en.wikipedia.org/wiki/Będzin",
            "http://en.wikipedia.org/wiki/Piekary_Śląskie",
            "http://en.wikipedia.org/wiki/Racibórz",
            "http://en.wikipedia.org/wiki/Zawiercie",
            "http://en.wikipedia.org/wiki/Świętochłowice",
            "http://en.wikipedia.org/wiki/Wodzisław_Śląski",
            "http://en.wikipedia.org/wiki/Mikołów",
            "http://en.wikipedia.org/wiki/Knurów",
            "http://en.wikipedia.org/wiki/Czechowice-Dziedzice",
            "http://en.wikipedia.org/wiki/Cieszyn",
            "http://en.wikipedia.org/wiki/Czeladź"
        ],
        "thematic_focus": "Górnego Śląska i Zagłębia (portal regionalny)",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 3
    },

    "tylkoslask3": {
        "friendly_name": "TylkoSlask.pl3",
        "wp_api_url_base": "https://tylkoslask.pl/wp-json/wp/v2",
        "wp_username": os.getenv("TYLKOSLASK_USER"),
        "wp_password": os.getenv("TYLKOSLASK_PASS"),
        "auth_method": "basic",
        "event_registry_key": os.getenv("TYLKOSLASK_ER_KEY"),
        "er_concept_uris": [
            "http://en.wikipedia.org/wiki/Łaziska_Górne",
            "http://en.wikipedia.org/wiki/Żywiec",
            "http://en.wikipedia.org/wiki/Pszczyna",
            "http://en.wikipedia.org/wiki/Lubliniec",
            "http://en.wikipedia.org/wiki/Myszków",
            "http://en.wikipedia.org/wiki/Radlin",
            "http://en.wikipedia.org/wiki/Czerwionka-Leszczyny",
            "http://en.wikipedia.org/wiki/Strumień",
            "http://en.wikipedia.org/wiki/Wojkowice",
            "http://en.wikipedia.org/wiki/Pyskowice",
            "http://en.wikipedia.org/wiki/Wilamowice",
            "http://en.wikipedia.org/wiki/Blachownia",
            "http://en.wikipedia.org/wiki/Ustroń",
            "http://en.wikipedia.org/wiki/Miasteczko_Śląskie",
            "http://en.wikipedia.org/wiki/Kuźnia_Raciborska"
        ],
        "thematic_focus": "Górnego Śląska i Zagłębia (portal regionalny)",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 3
    },

    "tylkoslask4": {
        "friendly_name": "TylkoSlask.pl4",
        "wp_api_url_base": "https://tylkoslask.pl/wp-json/wp/v2",
        "wp_username": os.getenv("TYLKOSLASK_USER"),
        "wp_password": os.getenv("TYLKOSLASK_PASS"),
        "auth_method": "basic",
        "event_registry_key": os.getenv("TYLKOSLASK_ER_KEY"),
        "er_concept_uris": [
            "http://en.wikipedia.org/wiki/Sośnicowice",
            "http://en.wikipedia.org/wiki/Siewierz",
            "http://en.wikipedia.org/wiki/Czechowice-Dziedzice",
            "http://en.wikipedia.org/wiki/Pilica",
            "http://en.wikipedia.org/wiki/Herby",
            "http://en.wikipedia.org/wiki/Szczekociny",
            "http://en.wikipedia.org/wiki/Żarki",
            "http://en.wikipedia.org/wiki/Krzanowice",
            "http://en.wikipedia.org/wiki/Włodowice",
            "http://en.wikipedia.org/wiki/Ogrodzieniec",
            "http://en.wikipedia.org/wiki/Poręba",
            "http://en.wikipedia.org/wiki/Pszów",
            "http://en.wikipedia.org/wiki/Wisła",
            "http://en.wikipedia.org/wiki/Poraj",
            "http://en.wikipedia.org/wiki/Skoczów"
        ],
        "thematic_focus": "Górnego Śląska i Zagłębia (portal regionalny)",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 3
    },
    "ogrodzeniapanelowe": {
        "friendly_name": "OgrodzeniaPanelowePolska.pl",
        "wp_api_url_base": "https://ogrodzeniapanelowepolska.pl/wp-json/wp/v2",
        "wp_username": os.getenv("OGRPAN_USER"),
        "wp_password": os.getenv("OGRPAN_PASS"),
        "auth_method": "basic",
        "event_registry_key": os.getenv("OGRPAN_ER_KEY"),
        "er_concept_uri": "http://pl.wikipedia.org/wiki/Polska",
        "thematic_focus": "bram, ogrodzeń, kostki brukowej i tego typu infrastruktury",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 3
    },

    "kupogrodzenie": {
        "friendly_name": "Kupogrodzenie.pl",
        "wp_api_url_base": "https://kupogrodzenie.pl/wp-json/wp/v2",
        "wp_username": os.getenv("KUPOGR_USER"),
        "wp_password": os.getenv("KUPOGR_PASS"),
        "auth_method": "basic",
        "event_registry_key": os.getenv("KUPOGR_ER_KEY"),
        "er_concept_uri": "http://pl.wikipedia.org/wiki/Polska",
        "thematic_focus": "bram, ogrodzeń, kostki brukowej i tego typu infrastruktury",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 3
    },

    "superkredyty": {
        "friendly_name": "SuperKredyty.com",
        "wp_api_url_base": "https://superkredyty.com/wp-json/wp/v2",
        "wp_username": os.getenv("KREDYTY_USER"),
        "wp_password": os.getenv("KREDYTY_PASS"),
        "auth_method": "basic",
        "event_registry_key": os.getenv("KREDYTY_ER_KEY"),
        "er_concept_uri": "http://pl.wikipedia.org/wiki/Kredyt_bankowy",
        "thematic_focus": "pożyczek, kredytów, kont bankowych i innych instrumentów finansowych",
        "prompt_template": PREMIUM_PROMPT_TEMPLATE,
        "author_id": 3
    }
}

