# 🛡️ Opzione 1: Pitch Focalizzato su Prodotto, Demo & Soluzione Hackathon

> **Target:** Presentazione classica da Hackathon (focus su Prodotto, Demo Live e Funzionalità)  
> **Durata stimata:** 3:30 minuti  
> **File:** `PRESENTAZIONE_OPZIONE_1_STANDARD.md`

---

## 📌 Sintesi della Strategia (Opzione 1)
Questa versione è pensata per valorizzare al massimo il **lavoro pratico svolto dal team**, mettendo al centro:
1. Il dolore vivo dei Comuni italiani (i leak di dati sanitari e minori).
2. L'interfaccia utente semplice a semaforo e la Live Demo.
3. Il funzionamento tecnico chiaro (*"L'IA vede il contesto, mai l'identità"*).
4. Il risultato concreto: download del PDF corretto con i passaggi oscurati (*omissis*).

---

## 🎬 Scaletta Slide per Slide

### SLIDE 1: Cover & The Hook
* **Titolo:** **Albo Sicuro**
* **Sottotitolo:** *Proteggere la privacy dei cittadini nell'Albo Pretorio online*
* **Visual:** Logo pulito (scudo con spunta) + anteprima della dashboard semaforica (Verde / Giallo / Rosso).
* **Speaker Script (20 sec):**
  > *"Ogni giorno i Comuni italiani pubblicano online decine di atti amministrativi. E ogni giorno, per un semplice errore umano, finiscono su internet diagnosi mediche, disabilità di minori, ISEE e coordinate bancarie.  
  > Abbiamo creato **Albo Sicuro**: l'assistente intelligente che aiuta i funzionari a individuare e correggere i dati sensibili prima e dopo la pubblicazione."*

---

### SLIDE 2: Il Problema (The Pain)
* **Titolo:** **Il dilemma della PA: Trasparenza vs Privacy**
* **I 3 punti cardine:**
  * **La legge impone la trasparenza:** Delibere e determine devono essere pubbliche.
  * **Il GDPR impone il rigore:** Vietata la diffusione di dati su salute, minori e indigenza (Art. 2-septies Codice Privacy, D.Lgs. 33/2013).
  * **Il fattore umano:** I funzionari sono sommersi da decine di documenti al giorno, senza strumenti automatici di verifica. Le sanzioni del Garante superano facilmente i 20.000 euro per singolo atto.
* **Visual:** Esempi di determine con dati sensibili oscurati male o pubblicati in chiaro con timbro di richiamo normativo.
* **Speaker Script (30 sec):**
  > *"La legge impone ai Comuni di pubblicare gli atti, ma il GDPR e il Garante della Privacy vietano la diffusione di dati su salute o disagio economico. Oggi un funzionario deve controllare a mano centinaia di pagine. Basta una distrazione in una determina di sussidi scolastici o contributi affitto per distruggere la privacy di una famiglia. Albo Sicuro risolve questo problema alla radice."*

---

### SLIDE 3: La Soluzione (Come Funziona)
* **Titolo:** **Albo Sicuro: Prevenzione e Monitoraggio Continuo**
* **Le due funzionalità operative:**
  1. **Controllo Preventivo (/upload):** Il dipendente carica il PDF prima di pubblicarlo. L'app evidenzia le frasi critiche e genera in automatico il PDF corretto con gli *omissis*.
  2. **Demone di Monitoraggio:** Un processo in background analizza costantemente gli atti già pubblicati, segnalando tempestivamente le violazioni nella dashboard con il calcolo dei giorni di esposizione rimanenti.
* **Visual:** Schema a due schermate affiancate: la schermata di Upload e la Dashboard degli Allarmi.
* **Speaker Script (30 sec):**
  > *"Il sistema opera su due fronti: prima della pubblicazione, il funzionario fa un drag & drop del PDF: riceve un semaforo immediato e può scaricare subito la versione corretta con i dati oscurati.  
  > In parallelo, un demone autonomo controlla continuamente i documenti già online, allertando il Comune sui documenti a rischio per permettere la sostituzione tempestiva."*

---

### SLIDE 4: La Tecnologia ("Privacy by Design")
* **Titolo:** **"L'IA comprende il contesto, mai l'identità"**
* **Punti tecnici essenziali:**
  * **Pseudonimizzazione Locale:** Regex avanzate con validazione formale di Codici Fiscali e IBAN (`python-stdnum`) + Named Entity Recognition con spaCy.
  * **Zero Leakage verso l'LLM:** All'LLM viene inviato solo il testo con segnaposto astratti (`[PERSONA_1]`, `[CF_1]`). Nessun dato personale esce all'esterno.
  * **Vera Redazione Vettoriale (PyMuPDF):** Il testo oscurato viene eliminato fisicamente dal PDF, non coperto da semplici rettangoli neri.
* **Visual:** Schema del flusso:
  $$\text{PDF Originale} \rightarrow \text{Pseudonimizzazione Locale} \rightarrow \text{LLM Reasoning} \rightarrow \text{PDF Sanificato}$$
* **Speaker Script (35 sec):**
  > *"Non volevamo creare uno strumento per la privacy che a sua volta esponesse i dati a modelli esterni.  
  > Per questo abbiamo applicato un principio rigoroso: l'IA riceve solo testo pseudonimizzato. Vede che [PERSONA_1] ha un problema di salute, e sa che vìola la legge, ma non sa chi sia [PERSONA_1].  
  > E sul PDF finale applichiamo una redazione vera, cancellando il dato dal codice del file in modo irreversibile."*

---

### SLIDE 5: Live Demo 1 — La Dashboard & Il Monitoraggio H24 del Demone
* **Titolo:** **Live Demo: La Dashboard & Il Monitoraggio H24 del Demone**
* **Screenshot Reale Integrato:** `01_dashboard.jpg` (Vista Live Dashboard)
* **Cosa Mostra lo Schermo:**
  * Indicatore verde in alto: **"Ultimo check: 7m fa"** (la prova che il demone vigila in background).
  * Card metriche riassuntive: **6 Analizzati**, **2 Conformi**, **3 Non Conformi**, **1 Da Verificare**.
  * Tabella **Atti Analizzati**: aggiornamento automatico ogni 5s con tracciamento sorgente (`albo` vs `upload`) e livello di gravità (alta, media).
* **Speaker Script (25 sec):**
  > *"Ecco la prima schermata reale di Albo Sicuro: la Dashboard Live. Notate in alto a destra l'indicatore 'Ultimo check: 7m fa': il demone lavora in piena autonomia interrogando l'albo in background. Le card offrono un quadro di sintesi immediato, mentre la tabella sottostante cataloga ogni atto per sorgente e livello di gravità della violazione."*

---

### SLIDE 6: Live Demo 2 — Rilevamento Violazione e Vera Redazione Vettoriale
* **Titolo:** **Live Demo: Rilevamento Violazione e Vera Redazione Vettoriale**
* **Screenshot Reale Integrato:** `02_report_non_conforme_redacted.jpg` (Vista Report Non Conforme)
* **Cosa Mostra lo Schermo:**
  * **Determina Sussidio Disagio 04:** Rilevata con badge *"✗ Non conforme"* e gravità media.
  * **Confronto Side-by-Side:**
    * A sinistra: Il **PDF originale** con il nome del richiedente (*Bianchi Laura*), l'indirizzo di residenza, il Codice Fiscale e il sussidio economico in chiaro.
    * A destra: Il **PDF con dati oscurati** generato istantaneamente da PyMuPDF, con rettangoli neri di vera redazione irreversibile.
* **Speaker Script (30 sec):**
  > *"Questa è la schermata di dettaglio di un atto non conforme: la Determina per contributi straordinari. A sinistra vediamo il documento originale con il nominativo del cittadino, l'indirizzo e l'ISEE in chiaro. A destra, il PDF generato da Albo Sicuro: i dati sensibili sono stati rimossi con vera redazione vettoriale distruttiva. Il dato è fisicamente cancellato dal file, pronto per la pubblicazione conforme."*

---

### SLIDE 7: Live Demo 3 — Explainable AI, Normativa e Precedenti del Garante
* **Titolo:** **Live Demo: Explainable AI, Normativa e Precedenti del Garante**
* **Screenshot Reale Integrato:** `03_report_precedente_decisioni.jpg` (Decisioni per entità + Precedente)
* **Cosa Mostra lo Schermo:**
  * **Frase Critica Evidenziata:** *"possiede un'attestazione ISEE pari a euro 1.450,00 annui e stato di disoccupazione involontaria"*.
  * **RAG sui Precedenti del Garante:** Card del caso storico reale **Comune di Tricase (sanzione € 15.000)** per aver diffuso nominativi di beneficiari di buoni spesa alimentare.
  * **Tabella Decisioni per Entità:** Azione specifica per ogni dato (`[PERSONA_4] -> rimuovere`, `[ISEE] -> minimizzare`) con la norma violata (*Art. 26 c.4 D.Lgs. 33/2013* e *Art. 5 GDPR*).
* **Speaker Script (30 sec):**
  > *"Scendendo nel report vediamo la potenza del nostro motore di Explainable AI: il sistema isola la frase esatta che vìola la legge e a destra richiama dalla nostra knowledge base il precedente reale: 'Attenzione, per un caso analogo il Comune di Tricase è stato sanzionato dal Garante per 15.000 euro'. Sotto, la tabella delle decisioni per entità spiega al DPO ogni singola rimozione e la relativa norma violata."*

---

### SLIDE 8: Live Demo 4 — Distinzione Intelligente: Zero Falsi Positivi
* **Titolo:** **Live Demo: Distinzione Intelligente — Zero Falsi Positivi**
* **Screenshot Reale Integrato:** `04_report_conforme.jpg` (Graduatoria Concorso 01 Conforme)
* **Cosa Mostra lo Schermo:**
  * **001 Graduatoria Concorso 01:** Analisi di un bando con nomi e punteggi di vincitori e idonei.
  * **Badge e Spunta Verde:** *"✓ Conforme — Nessuna redazione necessaria"*.
  * **Rispetto delle Linee Guida Garante 2014:** L'atto non viene toccato perché la trasparenza sui concorsi pubblici è lecita e doverosa per legge.
* **Speaker Script (25 sec):**
  > *"Un timore frequente nella PA è che l'IA sia troppo zelante e oscuri atti che devono restare pubblici. Ecco la prova contraria: analizzando una graduatoria di concorso pubblico, Albo Sicuro la riconosce come lecita secondo le Linee Guida del Garante 2014. Il sistema emette verdetto Conforme con spunta verde e non tocca il file, garantendo zero falsi positivi."*

---

### SLIDE 9: Valore Operativo, Modello di Pricing & ROI per la PA
* **Titolo:** **Valore Operativo, Modello di Pricing & ROI per la PA**
* **Parte Superiore: I 3 Scaglioni di Pricing SaaS Annuo All-Inclusive:**
  1. **Tier Small (Piccoli Comuni < 5.000 ab.):**
     * **€ 1.800 – € 2.400 / anno** *(~150-200 €/mese)* • Fino a 1.000 atti/anno • Demone H24 attivo • Supporto standard.
  2. **Tier Medium (Comuni Medi 5.000 – 40.000 ab.):**
     * **€ 4.500 – € 6.000 / anno** *(~400-500 €/mese)* • Fino a 5.000 atti/anno • Utenti illimitati • Connettori API gestionali.
  3. **Tier Enterprise (Grandi Capoluoghi & ASL):**
     * **€ 12.000 – € 18.000 / anno** • Atti illimitati • Multi-settore (Sociale, Sanità, Tributi) • Audit Trail DPO.
* **Parte Inferiore: I 3 Pilastri di Valore Operativo & Driver d'Acquisto:**
  * **1. Azzeramento Sanzioni & ROI:** Evitare anche 1 sola sanzione del Garante (€ 10k–50k) ripaga da 3 a 5 anni di canone dell'ente, proteggendo i dirigenti dalla Corte dei Conti per danno erariale.
  * **2. 90% Risparmio di Tempo:** I funzionari comunali non devono più rileggere a mano centinaia di pagine: l'IA evidenzia solo le criticità e genera la versione conforme in 3 clic.
  * **3. Zero Burocrazia MePA:** Acquisto immediato sotto soglia D.Lgs. 36/2023 (< € 140k) senza gare d'appalto, con integrazione leggera via API sui gestionali già in uso (Maggioli, Halley).
* **Speaker Script (30 sec):**
  > *"Quanto vale e quanto costa Albo Sicuro alla Pubblica Amministrazione? Abbiamo unito efficienza operativa e sostenibilità economica: sul piano operativo, facciamo risparmiare fino al 90% del tempo al personale comunale. Sul piano economico, offriamo un canone SaaS all-inclusive scalabile da 1.800 €/anno per i piccoli Comuni a 12.000-18.000 €/anno per capoluoghi e ASL. Si acquista subito sul MePA sotto soglia (< 140k €) e un'unica sanzione evitata ripaga il servizio per oltre 4 anni."*

---

### SLIDE 10: Conclusioni, Roadmap & Team
* **Titolo:** **Rendere la trasparenza finalmente sicura**
* **Roadmap di Sviluppo:**
  * **Q3 2026:** Modulo OCR locale on-premise per atti cartacei e scansioni storiche.
  * **Q4 2026:** Estensione dell'auditor ai flussi di telemetria urbana, log di smart meter e videosorveglianza urbana (Traccia Hackathon).
  * **Conformità:** Qualificazione su ACN (Agenzia per la Cybersicurezza Nazionale) per il catalogo Cloud della PA.
* **Il Team:** 3 studenti sviluppatori (Campionato Universitario AI — DIGITA Academy).
* **Speaker Script (15 sec):**
  > *"La digitalizzazione della Pubblica Amministrazione non deve mai avvenire a spese della dignità e della privacy dei cittadini. Con Albo Sicuro la trasparenza diventa finalmente sicura, garantita e conforme per tutti. Grazie a tutti!"*
