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

7.  **GŁĘBSZA ANALIZA LUB KONTEKST HISTORYCZNY:** W jednej z sekcji (`<h2>`) wyjdź poza proste fakty. Dodaj analizę przyczyn i skutków, kontekst historyczny lub prognozy na przyszłość.

8.  **TABELA PORÓWNAWCZA LUB ZESTAWIENIE DANYCH:** Jeśli temat na to pozwala, **musisz** umieścić czytelną tabelę (`<table>`) z danymi.

9.  **PRAKTYCZNE PORADY LUB WNIOSKI DLA CZYTELNIKA:** Zakończ artykuł sekcją (`<h2>`), która jasno przedstawia praktyczne wnioski lub porady dla czytelnika.

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
            "http://en.wikipedia.org/wiki/Będzin",
            "http://en.wikipedia.org/wiki/Bestwina",
            "http://en.wikipedia.org/wiki/Bielsko-Biała",
            "http://en.wikipedia.org/wiki/Bieruń",
            "http://en.wikipedia.org/wiki/Bobrowniki",
            "http://en.wikipedia.org/wiki/Bojszowy",
            "http://en.wikipedia.org/wiki/Boronów",
            "http://en.wikipedia.org/wiki/Brenna",
            "http://en.wikipedia.org/wiki/Buczkowice",
            "http://en.wikipedia.org/wiki/Bytom",
            "http://en.wikipedia.org/wiki/Chełm Śląski",
            "http://en.wikipedia.org/wiki/Chorzów",
            "http://en.wikipedia.org/wiki/Chybie",
            "http://en.wikipedia.org/wiki/Ciasna",
            "http://en.wikipedia.org/wiki/Cieszyn",
            "http://en.wikipedia.org/wiki/Czechowice-Dziedzice",
            "http://en.wikipedia.org/wiki/Czeladź",
            "http://en.wikipedia.org/wiki/Czernichów",
            "http://en.wikipedia.org/wiki/Czerwionka-Leszczyny",
            "http://en.wikipedia.org/wiki/Częstochowa",
            "http://en.wikipedia.org/wiki/Dąbrowa Górnicza",
            "http://en.wikipedia.org/wiki/Dąbrowa Zielona",
            "http://en.wikipedia.org/wiki/Gaszowice",
            "http://en.wikipedia.org/wiki/Gierałtowice",
             "http://en.wikipedia.org/wiki/Gliwice",
            "http://en.wikipedia.org/wiki/Goczałkowice-Zdrój",
            "http://en.wikipedia.org/wiki/Godów",
            "http://en.wikipedia.org/wiki/Goleszów",
            "http://en.wikipedia.org/wiki/Gorzyce",
            "http://en.wikipedia.org/wiki/Hażlach",
            "http://en.wikipedia.org/wiki/Herby",
            "http://en.wikipedia.org/wiki/Imielin",
            "http://en.wikipedia.org/wiki/Irządze",
            "http://en.wikipedia.org/wiki/Istebna",
            "http://en.wikipedia.org/wiki/Janów",
            "http://en.wikipedia.org/wiki/Jasienica",
            "http://en.wikipedia.org/wiki/Jastrzębie-Zdrój",
            "http://en.wikipedia.org/wiki/Jaworze",
            "http://en.wikipedia.org/wiki/Jaworzno",
            "http://en.wikipedia.org/wiki/Jejkowice",
            "http://en.wikipedia.org/wiki/Jeleśnia",
            "http://en.wikipedia.org/wiki/Kalety",
            "http://en.wikipedia.org/wiki/Katowice",
            "http://en.wikipedia.org/wiki/Kłobuck",
            "http://en.wikipedia.org/wiki/Kłomnice",
            "http://en.wikipedia.org/wiki/Knurów",
            "http://en.wikipedia.org/wiki/Kobiór",
            "http://en.wikipedia.org/wiki/Kochanowice",
            "http://en.wikipedia.org/wiki/Koniecpol",
            "http://en.wikipedia.org/wiki/Konopiska",
            "http://en.wikipedia.org/wiki/Kornowac",
            "http://en.wikipedia.org/wiki/Koszęcin",
            "http://en.wikipedia.org/wiki/Kozy",
            "http://en.wikipedia.org/wiki/Kroczyce",
            "http://en.wikipedia.org/wiki/Krupski Młyn",
            "http://en.wikipedia.org/wiki/Kruszyna",
            "http://en.wikipedia.org/wiki/Krzanowice",
            "http://en.wikipedia.org/wiki/Krzepice",
            "http://en.wikipedia.org/wiki/Krzyżanowice",
            "http://en.wikipedia.org/wiki/Kuźnia Raciborska",
            "http://en.wikipedia.org/wiki/Łaziska Górne",
            "http://en.wikipedia.org/wiki/Łazy",
            "http://en.wikipedia.org/wiki/Lędziny",
            "http://en.wikipedia.org/wiki/Lelów",
            "http://en.wikipedia.org/wiki/Lipie",
            "http://en.wikipedia.org/wiki/Lipowa",
            "http://en.wikipedia.org/wiki/Łodygowice",
            "http://en.wikipedia.org/wiki/Lubliniec",
            "http://en.wikipedia.org/wiki/Lubomia",
            "http://en.wikipedia.org/wiki/Lyski",
            "http://en.wikipedia.org/wiki/Marklowice",
            "http://en.wikipedia.org/wiki/Miasteczko Śląskie",
            "http://en.wikipedia.org/wiki/Miedźna",
            "http://en.wikipedia.org/wiki/Miedźno",
            "http://en.wikipedia.org/wiki/Mierzęcice",
            "http://en.wikipedia.org/wiki/Mikołów",
            "http://en.wikipedia.org/wiki/Mstów",
            "http://en.wikipedia.org/wiki/Mszana",
            "http://en.wikipedia.org/wiki/Mykanów",
            "http://en.wikipedia.org/wiki/Mysłowice",
            "http://en.wikipedia.org/wiki/Myszków",
            "http://en.wikipedia.org/wiki/Niegowa",
            "http://en.wikipedia.org/wiki/Ogrodzieniec",
            "http://en.wikipedia.org/wiki/Olsztyn",
            "http://en.wikipedia.org/wiki/Opatów",
            "http://en.wikipedia.org/wiki/Ornontowice",
            "http://en.wikipedia.org/wiki/Orzesze",
            "http://en.wikipedia.org/wiki/Ożarowice",
            "http://en.wikipedia.org/wiki/Panki",
            "http://en.wikipedia.org/wiki/Pawłowice",
            "http://en.wikipedia.org/wiki/Pawonków",
            "http://en.wikipedia.org/wiki/Piekary Śląskie",
            "http://en.wikipedia.org/wiki/Pilchowice",
            "http://en.wikipedia.org/wiki/Poczesna",
            "http://en.wikipedia.org/wiki/Porąbka",
            "http://en.wikipedia.org/wiki/Poraj",
            "http://en.wikipedia.org/wiki/Poręba",
            "http://en.wikipedia.org/wiki/Przyrów",
            "http://en.wikipedia.org/wiki/Przystajń",
            "http://en.wikipedia.org/wiki/Psary",
            "http://en.wikipedia.org/wiki/Pszczyna",
            "http://en.wikipedia.org/wiki/Pszów",
            "http://en.wikipedia.org/wiki/Pyskowice",
            "http://en.wikipedia.org/wiki/Racibórz",
            "http://en.wikipedia.org/wiki/Radlin",
            "http://en.wikipedia.org/wiki/Radzionków",
            "http://en.wikipedia.org/wiki/Rajcza",
            "http://en.wikipedia.org/wiki/Rędziny",
            "http://en.wikipedia.org/wiki/Ruda Śląska",
            "http://en.wikipedia.org/wiki/Rudziniec",
            "http://en.wikipedia.org/wiki/Rybnik",
            "http://en.wikipedia.org/wiki/Rydułtowy",
            "http://en.wikipedia.org/wiki/Siemianowice Śląskie",
            "http://en.wikipedia.org/wiki/Siewierz",
            "http://en.wikipedia.org/wiki/Skoczów",
            "http://en.wikipedia.org/wiki/Sławków",
            "http://en.wikipedia.org/wiki/Ślemień",
            "http://en.wikipedia.org/wiki/Sośnicowice",
            "http://en.wikipedia.org/wiki/Sosnowiec",
            "http://en.wikipedia.org/wiki/Starcza",
            "http://en.wikipedia.org/wiki/Strumień",
            "http://en.wikipedia.org/wiki/Suszec",
            "http://en.wikipedia.org/wiki/Świerklaniec",
            "http://en.wikipedia.org/wiki/Świerklany",
            "http://en.wikipedia.org/wiki/Świętochłowice",
            "http://en.wikipedia.org/wiki/Świnna",
            "http://en.wikipedia.org/wiki/Szczekociny",
            "http://en.wikipedia.org/wiki/Szczyrk",
            "http://en.wikipedia.org/wiki/Tarnowskie Góry",
            "http://en.wikipedia.org/wiki/Toszek",
            "http://en.wikipedia.org/wiki/Tworóg",
            "http://en.wikipedia.org/wiki/Tychy",
            "http://en.wikipedia.org/wiki/Ustroń",
            "http://en.wikipedia.org/wiki/Wielowieś",
            "http://en.wikipedia.org/wiki/Wilamowice",
            "http://en.wikipedia.org/wiki/Wilkowice",
            "http://en.wikipedia.org/wiki/Wisła",
            "http://en.wikipedia.org/wiki/Wodzisław Śląski",
            "http://en.wikipedia.org/wiki/Wojkowice",
            "http://en.wikipedia.org/wiki/Woźniki",
            "http://en.wikipedia.org/wiki/Wręczyca Wielka",
            "http://en.wikipedia.org/wiki/Wyry",
            "http://en.wikipedia.org/wiki/Zabrze",
            "http://en.wikipedia.org/wiki/Żarki",
            "http://en.wikipedia.org/wiki/Żarnowiec",
            "http://en.wikipedia.org/wiki/Zawiercie",
            "http://en.wikipedia.org/wiki/Zbrosławice",
            "http://en.wikipedia.org/wiki/Zebrzydowice",
            "http://en.wikipedia.org/wiki/Żory",
            "http://en.wikipedia.org/wiki/Żywiec"
        ]
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
