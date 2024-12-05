# Evadarea din Labirint: Joc cu Client-Server TCP

Aceasta aplicatie reprezinta un joc tip "Labirint", implementat utilizand un model de comunicare **client-server** prin intermediul protocolului TCP. Scopul jucatorului este de a iesi din labirint fara sa fie prins de monstru. Jocul se desfasoara intr-un labirint generat aleator, iar interactiunea dintre jucator si server se face prin intermediul comenzilor text.

---

## Structura Proiectului
Proiectul contine doua fisiere principale:
- **`server.py`** - Codul serverului care gestioneaza logica jocului si comunica cu clientul.
- **`client.py`** - Codul clientului care permite utilizatorului sa interactioneze cu serverul.

---

## Reguli Joc si Functionalitati

### Obiectivul Jocului
Scopul principal este ca jucatorul (`J`) sa navigheze prin labirint si sa gaseasca o iesire (`E`), evitand monstrul (`M`). Jocul este generat dinamic, iar fiecare partida ofera o provocare unica datorita pozitionarii aleatorii si regulilor stricte de plasare a entitatilor.

---

### Pozitionare Jucator (J)
Jucatorul incepe intr-o pozitie generata aleatoriu, cu respectarea urmatoarelor reguli:
1. **Restrictii pozitionare:**
   - Nu poate fi plasat pe pereti (`#`) sau pe iesiri (`E`).
2. **Distanta fata de iesiri:**
   - Pentru fiecare iesire (`E`), exista o distanta minima de **3 mutari** intre jucator si iesire.
   - Distanta de **3 mutari** inseamna cel putin **2 casute libere** intre jucator si iesire.

### Pozitionare Monstru (M)
Monstrul este plasat aleatoriu, cu respectarea urmatoarelor reguli:
1. **Restrictii pozitionare:**
   - Nu poate fi plasat pe iesiri (`E`), pereti (`#`) sau pe pozitia jucatorului (`J`).
2. **Distanta fata de jucator:**
   - Trebuie sa existe cel putin **3 casute libere** intre jucator si monstru.
3. **Blocarea iesirilor:**
   - Monstrul nu poate bloca o iesire (`E`).
   - Trebuie sa existe minim **2 casute libere** intre monstru si iesire.

---

### Generare Labirint
- Labirintul este ales aleatoriu dintre cinci modele (`labirint_0.txt`, `labirint_1.txt`, etc.).
- Modelul este reprezentat sub forma de matrice 2D, fiecare celula avand unul dintre urmatoarele simboluri:
  - `#` - Perete (obstacol).
  - `E` - Iesire (scopul jocului).
  - ` ` - Spatiu liber (casute unde te poti deplasa).

---

### Functionalitati Aditionale
1. **Dinamica de joc:**
   - Jucatorul poate folosi comenzi precum `U` (sus), `D` (jos), `L` (stanga), si `R` (dreapta) pentru a se deplasa.
   - Daca jucatorul loveste un perete (`#`), acesta este informat si trebuie sa aleaga o alta directie.
2. **Victorie si Infrangere:**
   - Jucatorul castiga daca ajunge pe o iesire (`E`).
   - Jucatorul pierde daca este prins de monstru (`M`).
3. **Explorare limitata:**
   - La inceput, labirintul este intunecat, iar jucatorul poate vedea doar casutele vizitate.
4. **Algoritmi de validare:**
   - Se verifica ca labirintul este **jucabil**, adica exista cel putin un drum de la jucator la o iesire.
   - Monstrul este pozitionat astfel incat sa nu fie "blocat" (generat intr-o camera fara iesiri) si sa reprezinte o amenintare reala pentru jucator.
