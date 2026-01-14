# SOHZ - System Optymalizacji Harmonogramów Zajęć

## Wymagania
- Python 3.10+
- pip

## Instalacja

1. Utwórz wirtualne środowisko (opcjonalnie):
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

3. Wypełnij bazę przykładowymi danymi:
```bash
python seed.py
```

## Uruchomienie

```bash
python run.py
```

Otwórz http://localhost:5000 w przeglądarce.

## Konta testowe

Po wykonaniu seeda dostępne są następujące konta:

| Rola | Email | Hasło |
|------|-------|-------|
| Dziekanat (Admin) | admin@uczelnia.pl | password123 |
| Pracownik dydaktyczny | jan.nowak@uczelnia.pl | password123 |
| Student | student1@uczelnia.pl | password123 |

## Funkcje systemu

### Dziekanat (Admin)
- Zarządzanie użytkownikami, salami, przedmiotami, grupami
- Przypisywanie pracowników do przedmiotów i grup
- Generowanie harmonogramu z automatyczną optymalizacją
- Interaktywne rozwiązywanie konfliktów

### Pracownik dydaktyczny
- Definiowanie preferencji czasowych
- Przeglądanie własnego harmonogramu

### Student
- Przeglądanie harmonogramu swojej grupy
- Wyszukiwanie planów wykładowców
