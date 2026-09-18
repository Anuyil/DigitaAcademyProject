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

### SLIDE 5: Live Demo (Il Flusso in 3 Clic)
* **Titolo:** **La Demo dal Vivo**
* **Sequenza da mostrare:**
  1. Caricamento di una determina con contributi per disabilità grave.
  2. Semaforo Rosso con spiegazione della violazione e card del precedente reale del Garante.
  3. Visualizzazione affiancata del testo originale e del PDF sanificato pronto al download.
* **Visual:** Screenshot dell'interfaccia (Dashboard $\rightarrow$ Dettaglio Report $\rightarrow$ Download PDF corretto).
* **Speaker Script (35 sec):**
  > *(Mostrando la demo a schermo)*  
  > *"Ecco la demo live: carichiamo una determina comunale. Il sistema rileva subito tre passaggi critici relativi allo stato di salute, accende il semaforo rosso e richiama il precedente ufficiale del Garante.  
  > A destra, il funzionario vede il confronto side-by-side e con un clic scarica il PDF bonificato con la dicitura 'omissis' al posto giusto."*

---

### SLIDE 6: Valore per la PA & Modello di Diffusione
* **Titolo:** **Impatto e Diffusione nei Comuni**
* **Punti chiave:**
  * **Target:** 7.900+ Comuni italiani, ASL e comunità montane.
  * **Vantaggi immediati:**
    * Zero sanzioni del Garante.
    * 90% di tempo risparmiato per i funzionari nella redazione manuale.
    * Massima tutela per i cittadini più fragili.
  * **Facilità di adozione:** Web app leggera, nessun software invasivo da installare, possibilità di deployment on-premise.
* **Speaker Script (25 sec):**
  > *"Per un Comune, Albo Sicuro significa zero rischi di sanzione, tutela totale dei cittadini più deboli e ore di lavoro manuale risparmiate. È uno strumento leggero, conforme alle linee guida nazionali, pronto per essere adottato sia dai piccoli Comuni che dalle grandi città."*

---

### SLIDE 7: Conclusioni & Team
* **Titolo:** **Rendere la trasparenza finalmente sicura**
* **Riepilogo:**
  * Privacy by Design reale.
  * Protezione preventiva e continua.
  * Pronto per la digitalizzazione sicura della PA.
* **Il Team:** 3 studenti sviluppatori (Campionato Universitario AI).
* **Speaker Script (15 sec):**
  > *"La digitalizzazione della Pubblica Amministrazione non deve mai avvenire a spese della dignità dei cittadini. Con Albo Sicuro la trasparenza diventa finalmente sicura. Grazie a tutti!"*
