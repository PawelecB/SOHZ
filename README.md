# SOHZ - System Optymalizacji Harmonogramów Zajęć

SOHZ (System Optymalizacji Harmonogramów Zajęć) to nowoczesna aplikacja webowa przeznaczona do automatyzacji procesu tworzenia planów zajęć na uczelniach wyższych. System skupia się na optymalizacji pod kątem preferencji pracowników oraz minimalizacji okienek w planach zarówno wykładowców, jak i studentów.

## 🚀 Technologie

Projekt został zbudowany przy użyciu następujących technologii:

- **Backend:** Python (Flask 3.0)
- **Baza danych:** SQLite z wykorzystaniem SQLAlchemy (ORM)
- **Frontend:** Jinja2 (Templates), Vanilla JavaScript, CSS (modern design system)
- **Uwierzytelnienie:** Flask-Login z hashowaniem haseł (Bcrypt)

## 🧠 Algorytm Optymalizacji

Głównym atutem systemu jest zaawansowany silnik generowania harmonogramów, który przeszedł ewolucję od prostego modelu przeszukiwania zachłannego do wielokryterialnej optymalizacji wagowej.

### Kluczowe mechanizmy:

1.  **Ważona Punktacja (Scoring):**
    Każdy potencjalny slot czasowy dla zajęć jest oceniany punktowo na podstawie trzech regulowanych wag:
    - **Preferencje pracowników:** Punkty za zgodność z godzinami, w których wykładowca chciałby pracować.
    - **Okienka Nauczycieli:** Kary za "rozstrzelony" plan zajęć prowadzącego.
    - **Okienka Studentów:** Kary za długie przerwy między zajęciami grupy.

2.  **Twarde Ograniczenia (Hard Constraints):**
    - **Limit dzienny:** Maksymalnie 2 bloki (3 godziny zegarowe) danego przedmiotu w jednym dniu dla danej grupy.
    - **Równomierny rozkład:** Algorytm automatycznie oblicza limit zajęć na tydzień (np. max 1-2 bloki), co zapobiega kumulacji jednego przedmiotu w krótkim okresie czasu.
    - **Brak konfliktów:** Gwarancja braku nakładania się zajęć tego samego nauczyciela, grupy studenckiej lub sali w tym samym czasie.

3.  **Proces Dziekanatu:**
    - Harmonogramy są najpierw tworzone jako wersje robocze (**DRAFT**).
    - Przed publikacją pracownik dziekanatu może ręcznie dostosować wagi optymalizacji i uruchomić ponowne przeliczenie wybranych planów.
    - **Rozwiązywanie konfliktów:** W sytuacjach braku dostępnych slotów (np. przeciążenie sali), system oferuje interaktywny interfejs do ręcznego wyboru alternatywnych terminów.

## 🛠️ Pierwsze Uruchomienie

### Wymagania
- Python 3.10 lub nowszy
- pip (menedżer pakietów)

### Instalacja i konfiguracja

1. **Sklonuj repozytorium** (jeśli jeszcze tego nie zrobiłeś).
2. **Utwórz i aktywuj wirtualne środowisko:**
   ```bash
   python -m venv venv
   # Aktywacja (Windows):
   venv\Scripts\activate
   # Aktywacja (Linux/macOS):
   source venv/bin/activate
   ```
3. **Zainstaluj wymagane biblioteki:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Zainicjalizuj bazę danych przykładowymi danymi:**
   ```bash
   python seed.py
   ```
   *Ten krok usunie istniejącą bazę danych `instance/dev.db` i utworzy nową z kompletem danych testowych (użytkownicy, sale, przedmioty).*

### Uruchomienie aplikacji

```bash
python run.py
```
Aplikacja będzie dostępna pod adresem: [http://localhost:5000](http://localhost:5000)

## 👤 Role i Konta Testowe

| Rola | Email | Hasło |
| :--- | :--- | :--- |
| **Dziekanat (Admin)** | admin@uczelnia.pl | password123 |
| **Pracownik dydaktyczny** | jan.nowak@uczelnia.pl | password123 |
| **Student** | student1@uczelnia.pl | password123 |

### Główne funkcjonalności:
- **Admin:** Zarządzanie całą uczelnią, generowanie/publikacja planów, interaktywna optymalizacja.
- **Pracownik:** Ustawianie preferencji (dostępne w panelu), podgląd swojego planu zajęć.
- **Student:** Podgląd planu grupy oraz wyszukiwarka zajęć prowadzących.

---
*Projekt zrealizowany w ramach migracji systemu z Next.js/TypeScript na nowoczesny stos Python/Flask.*
