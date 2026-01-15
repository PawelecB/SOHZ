# Dokumentacja Algorytmu Optymalizacji SOHZ

Dokument ten opisuje szczegółowo działanie silnika generującego harmonogramy w systemie SOHZ.

## 1. Typ Algorytmu

Zastosowano **algorytm zachłanny z heurystyką wagową (Weighted Greedy Heuristic)**.

System nie przeszukuje całej przestrzeni rozwiązań (co byłoby zbyt kosztowne obliczeniowo), lecz iteracyjnie przydziela zajęcia, podejmując lokalnie optymalne decyzje dla każdego przedmiotu w oparciu o złożony system punktacji.

### Główne cechy:
- **Determinizm:** Dla tych samych danych wejściowych (wagi + preferencje) wynik jest zawsze ten sam (dzięki sortowaniu).
- **Strategia:** "Best-fit" – dla każdego przedmiotu szukany jest najlepszy dostępny w danym momencie slot czasowy.
- **Rozwiązywanie konfliktów:** Jeśli algorytm nie może znaleźć miejsca, nie cofa wcześniejszych decyzji (brak backtrackingu), lecz raportuje konflikt.

---

## 2. Proces Decyzyjny (Krok po kroku)

### Faza 1: Przygotowanie
1. **Czyszczenie:** Usuwane są stare wersje robocze (DRAFT) dla danej grupy.
2. **Mapa zajętości:** Budowana jest mapa zajętych terminów na podstawie:
   - Planów już opublikowanych (PUBLISHED).
   - Innych planów roboczych (DRAFT) innych grup (aby uniknąć kolizji sal i nauczycieli).
3. **Sortowanie Zadań:** Przedmioty do zaplanowania są sortowane według priorytetu nauczyciela (nauczyciele z wyższymi wymaganiami są obsługiwani najpierw).

### Faza 2: Alokacja (Dla każdego przedmiotu)
Dla każdego przedmiotu system:
1. Oblicza ile slotów jest potrzebnych (np. 30h wykładu = 20 slotów po 1.5h).
2. Próbuje znaleźć najlepszy slot w dostępnych tygodniach.
3. Dla każdego potencjalnego slotu (Dzień X, Godzina Y) oblicza **SCORE (Punktację)**.
4. Wybiera slot z najwyższym wynikiem.

---

## 3. Punktacja (Scoring System)

Każdy potencjalny termin otrzymuje punkty. Wyższy wynik = lepszy termin.

Wzór na ocenę slotu:

```
SCORE = (BasePref * WeightPref * 2) 
        + MorningBonus 
        - LoadPenalty 
        ± TeacherGapBonus 
        ± StudentGapBonus
```

### Składniki oceny:

1.  **Preferencje Nauczyciela (`BasePref`)**:
    *   Wartość od 0 do 10 (na podstawie ustawień "Suwaków" nauczyciela).
    *   Mnożona przez wagę `preferences` (domyślnie 2).

2.  **Bonus Poranny (`MorningBonus`)**:
    *   Algorytm preferuje zajęcia poranne.
    *   Wzór: `(8 - numer_slotu) * 10`.
    *   Slot 1 (08:00) dostaje +70 pkt, Slot 7 (18:00) dostaje +10 pkt.

3.  **Kary za Obciążenie (`LoadPenalty`)**:
    *   Kluczowy mechanizm równoważenia planu ("Load Balancing").
    *   Kara za dokładanie zajęć do dnia, który jest już mocno obłożony dla danej grupy.
    *   Wzór: `Liczba_zajęć_w_tym_dniu * 50`.

4.  **Analiza Okienek (`Gap Analysis`)**:
    *   Sprawdzana dla Nauczyciela i Studenta osobno.
    *   **Bonus za zwartość:** Jeśli slot sąsiaduje z innymi zajęciami (np. 8:00-9:30, a planujemy 9:45-11:15), dodawane jest `40 * waga`.
    *   **Kara za okienko:** Jeśli slot tworzy dziurę w planie, odejmowane jest `30 * waga`.

---

## 4. Ograniczenia i Zasady (Constraints)

Algorytm przestrzega dwóch typów ograniczeń:

### A. Twarde ograniczenia (Hard Constraints)
*Nieprzekraczalne. Naruszenie = Slot niedostępny.*

1.  **Konflikt Nauczyciela:** Nauczyciel nie może prowadzić dwóch zajęć jednocześnie.
2.  **Konflikt Grupy:** Grupa studencka nie może mieć dwóch zajęć jednocześnie.
3.  **Dostępność Sali:** Sala nie może być zajęta przez inną grupę.
4.  **Pojemność Sali:** Sala musi pomieścić liczebność grupy (`room.capacity >= group.size`).
5.  **Rodzaj Sali:** Wykład musi być w sali wykładowej, lab w komputerowej.

### B. Miękkie ograniczenia (Soft Constraints)
*Mogą być poluzowane w trybie "Fallback", jeśli nie da się inaczej ułożyć planu.*

1.  **Limit Dzienny Przedmiotu:** Max **2 bloki** tego samego przedmiotu dziennie (3h zegarowe).
2.  **Limit Dzienny Grupy:** Max **5 bloków** zajęć łącznie dziennie.
    *   *Jeśli algorytm nie może znaleźć miejsca, to ograniczenie jest ignorowane (Fallback Mode).*

---

## 5. Tryb Awaryjny (Fallback)

Jeśli algorytm nie znajdzie slotu spełniającego wszystkie kryteria:
1. System wchodzi w tryb **Fallback**.
2. Poluzowuje limit `MAX_DAILY_SLOTS_FOR_GROUP` (pozwala na więcej niż 5 bloków zajęć dziennie).
3. Ponawia próbę znalezienia slotu.
4. Jeśli nadal brak miejsca -> generuje **Konflikt**.

## 6. Możliwe Konflikty

W przypadku niepowodzenia, system zwraca listę konfliktów typu `UNSCHEDULED`.
Zawiera ona listę "Sugerowanych Slotów" (wolnych terminów, które zostały odrzucone np. przez brak odpowiedniej sali lub niską punktację), co pozwala operatorowi na ręczną interwencję.
