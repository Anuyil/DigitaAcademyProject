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

### SLIDE 5: Demo 1 — Il Controllo Preventivo (/upload)
* **Titolo:** **Demo: Il Controllo Preventivo Prima della Pubblicazione**
* **Contenuto Visivo della Web App:**
  * Box di caricamento **Drag & Drop** del PDF amministrativo.
  * **Semaforo Decisionale Rosso:** Allarme immediato per violazione di dati particolari (es. salute o indigenza).
  * Pannello trasparente **"Cosa vede l'IA"**: confronto tra testo originale e testo pseudonimizzato con i segnaposto (`[PERSONA_1]`, `[CF_1]`).
  * Tasto per il **Download istantaneo del PDF bonificato** con gli *omissis* al posto giusto.
* **Speaker Script (30 sec):**
  > *"Mostriamo ora la prima funzionalità della Web App: il controllo preventivo all'indirizzo /upload. Il funzionario trascina il PDF della determina prima di pubblicarla. In pochi secondi il sistema analizza il documento, accende il semaforo rosso e mostra con trasparenza il pannello 'Cosa vede l'IA': a sinistra il testo originale, a destra il testo con i segnaposto pseudonimizzati. Con un solo clic, l'utente scarica il PDF già bonificato e conforme."*

---

### SLIDE 6: Demo 2 — Dashboard Live & Demone H24 (/)
* **Titolo:** **Demo: Dashboard Live & Monitoraggio H24 del Demone**
* **Contenuto Visivo della Web App:**
  * Indicatore verde in tempo reale: **"Demone attivo — Ultimo controllo 4s fa"**.
  * **Card Riassuntive dell'Ente:** Atti monitorati, Atti non conformi e Gravità alta aperti.
  * **Feed Allarmi Dinamico:** I nuovi atti a rischio compaiono in cima evidenziati.
  * **Countdown di Esposizione:** Mostra i giorni di esposizione rimanenti rispetto ai 15 giorni di affissione legale per intervenire prima di segnalazioni.
* **Speaker Script (30 sec):**
  > *"Passiamo ora alla seconda anima di Albo Sicuro: la Dashboard Live. In alto notiamo l'indicatore verde che pulsa: il demone è attivo e scansiona l'albo ogni pochi secondi. Le card mostrano il quadro complessivo dell'ente. Nel feed allarmi, ogni atto a rischio viene evidenziato con la categoria di violazione e il countdown dei giorni di esposizione: questo permette al responsabile di intervenire prima che l'atto venga segnalato o indicizzato in modo irreversibile."*

---

### SLIDE 7: Demo 3 — Dettaglio Report & Risoluzione (/reports/{id})
* **Titolo:** **Demo: Dettaglio Violazione, Precedente Garante e Risoluzione**
* **Contenuto Visivo della Web App:**
  * **Visualizzatore PDF Affiancati (Side-by-Side):** Documento originale a sinistra con dati in chiaro e documento sanificato a destra con gli *omissis*.
  * **Card del Precedente Garante:** Richiamo del caso storico reale con Ente coinvolto, norma violata e importo della sanzione (es. *GPDP Tricase — € 15.000*).
  * **Pulsanti di Azione:** Tasti rapidi *"Sostituisci Atto"*, *"Segna Risolto"* o *"Falso Positivo"*.
  * **Audit Trail:** Cronologia degli eventi per garantire l'accountability.
* **Speaker Script (30 sec):**
  > *"Cliccando su un allarme entriamo nel dettaglio del report. La schermata mostra i due PDF affiancati: a sinistra l'atto originario con i dati personali esposti, a destra la versione sanificata dal nostro algoritmo con la dicitura 'omissis'. Inoltre, una card evidenzia il precedente ufficiale del Garante con la sanzione storica abbinata. Con un clic l'atto viene sostituito all'albo e l'incidente viene marcato come risolto nell'audit trail."*

---

### SLIDE 8: Valore Operativo, Modello di Pricing & ROI per la PA
* **Titolo:** **Valore Operativo, Modello di Pricing & ROI per la PA**
* **Parte Superiore: I 3 Scaglioni di Pricing SaaS Annuo All-Inclusive:**
  1. **Tier Small (Piccoli Comuni < 5.000 ab.):**
     * **€ 1.800 – € 2.400 / anno** *(~150-200 €/mese)*
     * Fino a 1.000 atti/anno • Demone H24 attivo • Supporto standard.
  2. **Tier Medium (Comuni Medi 5.000 – 40.000 ab.):**
     * **€ 4.500 – € 6.000 / anno** *(~400-500 €/mese)*
     * Fino a 5.000 atti/anno • Utenti illimitati • Connettori API per gestionali.
  3. **Tier Enterprise (Grandi Capoluoghi & ASL):**
     * **€ 12.000 – € 18.000 / anno**
     * Atti illimitati • Multi-settore (Sociale, Sanità, Tributi) • Audit Trail DPO.
* **Parte Inferiore: I 3 Pilastri di Valore Operativo & Driver d'Acquisto:**
  * **1. Azzeramento Sanzioni & ROI:** Evitare anche 1 sola sanzione del Garante (€ 10k–50k) ripaga da 3 a 5 anni di canone dell'ente, proteggendo i dirigenti dalla Corte dei Conti per danno erariale.
  * **2. 90% Risparmio di Tempo:** I funzionari comunali non devono più rileggere a mano parola per parola centinaia di pagine di allegati: l'IA evidenzia solo le criticità e genera la versione conforme in 3 clic.
  * **3. Zero Burocrazia MePA:** Acquisto immediato sotto soglia D.Lgs. 36/2023 (< € 140k) senza bandire gare d'appalto. Web app leggera integrabile via API nei gestionali già in uso (Maggioli, Halley).
* **Speaker Script (30 sec):**
  > *"Quanto vale e quanto costa Albo Sicuro alla Pubblica Amministrazione? Abbiamo integrato efficienza operativa e sostenibilità economica:  
  > Sul piano operativo, facciamo risparmiare fino al 90% del tempo al personale comunale, evitando di dover controllare a mano centinaia di pagine di atti.  
  > Sul piano economico, offriamo un modello SaaS a canone annuale all-inclusive scalabile: da 1.800 €/anno per i piccoli Comuni, a 4.500 €/anno per i Comuni medi, fino a 12.000-18.000 €/anno per capoluoghi e ASL.  
  > Per la PA l'acquisto è immediato: rientra negli affidamenti diretti sotto soglia sul MePA (< 140k €), e una singola sanzione del Garante evitata ripaga il servizio per oltre 4 anni, tutelando i dirigenti dal danno erariale."*

---

### SLIDE 9: Conclusioni, Roadmap & Team
* **Titolo:** **Rendere la trasparenza finalmente sicura**
* **Roadmap di Sviluppo:**
  * **Q3 2026:** Modulo OCR locale on-premise per atti cartacei e scansioni storiche.
  * **Q4 2026:** Estensione dell'auditor ai flussi di telemetria urbana, log di smart meter e videosorveglianza urbana (Traccia Hackathon).
  * **Conformità:** Qualificazione su ACN (Agenzia per la Cybersicurezza Nazionale) per il catalogo Cloud della PA.
* **Il Team:** 3 studenti sviluppatori (Campionato Universitario AI — DIGITA Academy).
* **Speaker Script (15 sec):**
  > *"La digitalizzazione della Pubblica Amministrazione non deve mai avvenire a spese della dignità e della privacy dei cittadini. Con Albo Sicuro la trasparenza diventa finalmente sicura, garantita e conforme per tutti. Grazie a tutti!"*
