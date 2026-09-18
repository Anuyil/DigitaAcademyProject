# 🛡️ Albo Sicuro — Pitch Deck (Hackathon Campionato Universitario AI)

> **Evento:** Hackathon Campionato Universitario AI 2026 — DIGITA Academy / AI2B (Napoli)  
> **Traccia:** 2. PRIVACY — Privacy & Security Auditor per Smart City e PA  
> **Durata stimata:** 3:30 – 4:00 minuti  
> **Target:** Giuria aziendale, esperti di innovazione e investitori corporate  

---

## 📌 Executive Summary & Punti di Forza
- **Problema:** Il contrasto strutturale tra trasparenza della Pubblica Amministrazione (Albo Pretorio online) e tutela dei dati personali (GDPR). Ogni giorno si verificano leak di dati sanitari, disabilità di minori e disagio economico a causa di processi manuali ed errori umani.
- **Soluzione:** **Albo Sicuro**, auditor intelligente a doppio livello:
  1. *Preventivo (Gatekeeper):* Intercetta e sanifica i documenti prima del rilascio.
  2. *Continuo (Watchdog Daemon):* Scansiona h24 i portali istituzionali della Smart City per rilevare e azzerare i tempi di esposizione delle violazioni già online.
- **Innovazione ("Privacy by Design"):** *Zero-Knowledge AI*. L'LLM ragiona sulla semantica e sul contesto normativo senza mai ricevere né processare dati personali reali (grazie a un layer locale di pseudonimizzazione deterministica).
- **Business & Scalabilità:** Modello SaaS B2G integrabile via API nei software gestionali esistenti della PA (Maggioli, Halley, Engineering). ROI immediato calcolato sull'azzeramento del rischio sanzionatorio del Garante (€ 10k–50k per atto).

---

## 🎬 Struttura Dettagliata Slide per Slide

```
[Slide 1: Hook] ──> [Slide 2: Il Problema] ──> [Slide 3: La Soluzione]
      │
      ▼
[Slide 4: Architettura & Privacy by Design] ──> [Slide 5: Live Demo Flow]
      │
      ▼
[Slide 6: Modello di Business B2G] ──> [Slide 7: Roadmap & Team]
```

---

### SLIDE 1: Cover & The Hook
* **Titolo:** **Albo Sicuro**
* **Sottotitolo:** *L'Auditor Intelligente per la Privacy e la Sicurezza nella Smart City*
* **Elementi Visivi:**
  * Logo essenziale: scudo di protezione con spunta digitale e nodo di rete urbana.
  * Mockup pulito della dashboard con l'indicatore semaforico verde/giallo/rosso.
  * Badge: *Hackathon Campionato Universitario AI — Traccia Privacy*.
* **Speaker Script (20-25 sec):**
  > *"Buongiorno a tutti. Ogni giorno, oltre 7.900 Comuni italiani pubblicano online decine di migliaia di atti amministrativi. E ogni giorno, per un semplice errore umano, finiscono liberamente accessibili sul web diagnosi oncologiche, disabilità di minori, ISEE e conti correnti bancari.  
  > Abbiamo creato **Albo Sicuro**: il primo auditor autonomo che previene, intercetta e bonifica i leak di dati personali nella PA prima che diventino un danno per i cittadini e una sanzione del Garante."*

---

### SLIDE 2: Il Problema di Mercato (The Burning Pain)
* **Titolo:** **La trasparenza amministrativa non può distruggere la privacy**
* **Tre Numeri Chiave (Layout a 3 colonne):**
  * **€ 10.000 – € 50.000:** La sanzione media comminata dal Garante Privacy per singolo atto illecito (violazioni Art. 2-septies Codice Privacy e Art. 26 D.Lgs. 33/2013).
  * **15 Giorni:** Durata legale di pubblicazione all'Albo, ma i PDF rimangono indicizzati dai motori di ricerca per anni (perdita irreversibile del diritto all'oblio).
  * **100% Errore Umano:** I funzionari pubblici non hanno strumenti di supporto: devono validare a mano decine di determine e allegati complessi ogni giorno.
* **Elementi Visivi:**
  * Collage di ordinanze e provvedimenti sanzionatori reali emessi dal Garante contro enti locali, con timbro rosso *"SANZIONATO"* ed evidenziazione delle infrazioni (*"pubblicati dati sanitari e contributi per indigenza"*).
* **Speaker Script (30-35 sec):**
  > *"La legge impone la trasparenza degli atti pubblici, ma il GDPR vieta categoricamente la diffusione di dati su salute, disagio economico e minori.  
  > Oggi la responsabilità ricade tutta su un funzionario comunale che gestisce centinaia di pagine senza alcun supporto tecnologico. Basta dimenticare una riga in una determina per buoni spesa, ed ecco che il nome di una famiglia in difficoltà economica o la patologia di un dipendente finiscono per sempre su Google. Non è un problema teorico: è una falla strutturale quotidiana che costa milioni di euro e distrugge la fiducia dei cittadini."*

---

### SLIDE 3: La Soluzione (Value Proposition)
* **Titolo:** **Albo Sicuro: Doppia Protezione, Zero Compromessi**
* **I Due Motori del Sistema:**
  1. **Modulo Preventivo (Gatekeeper Pre-Pubblicazione):**
     * Il funzionario carica il PDF prima del rilascio.
     * Analisi semantica in tempo reale e classificazione di conformità.
     * Generazione automatica del PDF corretto con *vera redazione vettoriale* (*omissis*).
  2. **Modulo Continuo (Watchdog Daemon h24):**
     * Processo demone che monitora costantemente i portali istituzionali della Smart City.
     * Intercetta in tempo reale documenti non conformi già pubblicati.
     * Alert immediato al DPO con indicazione dei giorni di esposizione residui.
* **Elementi Visivi:**
  * Schema comparativo a due flussi simmetrici: a sinistra la verifica preventiva a monte (form upload), a destra il ciclo di scansione continua a valle (daemon watcher).
* **Speaker Script (30 sec):**
  > *"Albo Sicuro risolve il problema su due livelli complementari:  
  > A monte, come **Gatekeeper**: prima della pubblicazione, il funzionario carica l'atto; l'app segnala i passaggi critici, spiega la norma violata e genera con un clic il PDF bonificato.  
  > A valle, come **Watchdog**: un demone indipendente vigila costantemente sui flussi dell'infrastruttura cittadina, intercetta gli atti pubblicati per errore, calcola il countdown di esposizione e avvisa i responsabili prima che l'incidente diventi una sanzione."*

---

### SLIDE 4: Architettura & "Privacy by Design" (L'Innovazione)
* **Titolo:** **"L'IA comprende il contesto, mai l'identità"**
* **Pilastri Tecnologici:**
  * **Pseudonimizzazione Deterministica Locale:** Regex avanzate + validazione formale (`python-stdnum` per CF e IBAN) + NER locale con spaCy. I nomi diventano `[PERSONA_1]`, i codici `[CF_1]`.
  * **Zero-Knowledge LLM:** Il modello linguistico riceve esclusivamente testo pseudonimizzato. Nessun dato personale esce dal perimetro locale né viene inviato ai server dell'LLM.
  * **RAG Giurisprudenziale (Garante Privacy):** I verdetti sono motivati agganciandosi all'archivio dei precedenti sanzionatori reali del Garante della Privacy.
  * **Vera Redazione Vettoriale (PyMuPDF):** I dati non vengono coperti con una forma grafica sovrapposta, ma distrutti e rimossi fisicamente dai metadati e dai caratteri del file PDF.
* **Elementi Visivi:**
  * Diagramma di flusso a 4 stadi:
    $$\text{PDF Originale} \longrightarrow \fbox{Detector Locali (stdnum + spaCy)} \longrightarrow \text{Testo Pseudonimizzato} \longrightarrow \fbox{LLM Reasoning + RAG} \longrightarrow \fbox{True Redaction} \longrightarrow \text{PDF Sanificato}$$
* **Speaker Script (35-40 sec):**
  > *"Il paradosso di usare l'intelligenza artificiale per tutelare la privacy è il rischio di inviare dati sensibili di cittadini a modelli cloud esterni.  
  > In Albo Sicuro abbiamo risolto questo alla radice con una vera architettura **Privacy by Design**: prima che il testo arrivi all'LLM, un motore locale sostituisce ogni dato identificativo con token anonimi. L'IA vede solo che [PERSONA_1] ha una certa diagnosi in un atto, e riconosce la violazione dell'Art. 2-septies senza sapere chi sia la persona.  
  > E per la sanificazione finale, non usiamo banali rettangoli neri: applichiamo una redazione vettoriale crittograficamente irreversibile che distrugge il dato dal file."*

---

### SLIDE 5: Live Demo & Esperienza Utente
* **Titolo:** **Dall'Allarme alla Risoluzione in 3 Clic**
* **Caratteristiche dell'Interfaccia:**
  * **Traffic Light Verdict:** Semaforo verde/giallo/rosso per una decisione istantanea.
  * **Spiegazione Normativa Trasparente:** Indicazione esatta del passaggio critico, della norma violata e del precedente del Garante (es. Comune sanzionato e importo).
  * **Confronto Side-by-Side:** Pannello affiancato con il PDF originale e il PDF corretto con le diciture "omissis".
* **Elementi Visivi:**
  * Tre schermate reali dell'app:
    1. Feed degli allarmi con badge di gravità e giorni di esposizione.
    2. Card del precedente sanzionatorio collegato (es. *GPDP Tricase — € 15.000*).
    3. Il lettore PDF affiancato (Originale vs Bonificato).
* **Speaker Script (30-35 sec):**
  > *(Mostrando la demo o le schermate)*  
  > *"Ecco Albo Sicuro in azione: il nostro demone intercetta una determina con i beneficiari di contributi straordinari con ISEE in chiaro.  
  > Il sistema alza subito il semaforo rosso e richiama dalla knowledge base il precedente specifico del Garante: 'Attenzione, per un caso analogo il Comune di Tricase ha ricevuto 15.000 euro di sanzione'.  
  > Il responsabile può visionare i passaggi critici evidenziati e, con un singolo clic, scaricare la versione bonificata e sostituirla all'albo, sanando la non conformità in pochi secondi."*

---

### SLIDE 6: Modello di Business & Scalabilità B2G / B2B
* **Titolo:** **Mercato e Modello di Business**
* **Mercato Target:**
  * **PA Locale:** 7.900+ Comuni, Città Metropolitane e Unioni di Comuni.
  * **Sanità Pubblica:** Oltre 100 ASL e Aziende Ospedaliere soggette a trasparenza e ad alto rischio di leak sanitari.
  * **Partecipate & Utilities:** Municipalizzate e concessionarie di servizi urbani.
* **Strategia Go-To-Market:**
  * **API Layer / Add-on:** Non vogliamo rimpiazzare i complessi software gestionali della PA (Maggioli, Halley, Engineering), ma integrarci nei loro flussi come motore di conformità: *"Privacy-Verified by Albo Sicuro"*.
* **Modello di Ricavo:**
  * Abbonamento annuale SaaS a canone scalabile in base alla dimensione dell'ente (fasce demografiche / volume di atti).
* **ROI per l'Ente Pubblico:**
  * Il costo annuale di Albo Sicuro è nettamente inferiore a una singola sanzione del Garante o alle spese legali di un contenzioso.
* **Speaker Script (30 sec):**
  > *"Il nostro mercato non è solo la PA locale, ma l'intero ecosistema della digitalizzazione pubblica.  
  > Non chiediamo ai Comuni di cambiare software gestionale: ci integriamo via API come strato di certificazione e sicurezza.  
  > Per una qualsiasi amministrazione, il ritorno sull'investimento è matematico: evitare anche una sola sanzione da 20.000 euro o il risarcimento per danno d'immagine ripaga il canone di Albo Sicuro per anni."*

---

### SLIDE 7: Roadmap, Vision & Chiusura
* **Titolo:** **Il Futuro della Sicurezza nelle Smart City**
* **Roadmap di Sviluppo:**
  * **Q3:** Integrazione modulo OCR locale privacy-preserving per atti storici cartacei o scansionati.
  * **Q4:** Estensione dell'auditor ai flussi di telemetria IoT urbana (smart meter e registri di videosorveglianza urbana, come previsto dalla traccia di hackathon).
  * **Compliance:** Certificazione e qualificazione su ACN (Agenzia per la Cybersicurezza Nazionale) per il catalogo Cloud della PA.
* **Il Team:** 3 persone con competenze complementari in Data Engineering, AI/LLM e Architettura Software.
* **Punchline Finale:**
  > *"La vera digitalizzazione di una Smart City non consiste nel pubblicare indiscriminatamente tutto online, ma nel tutelare i diritti dei cittadini mentre si garantisce la trasparenza.  
  > Albo Sicuro trasforma la privacy da rischio sanzionatorio a processo automatico e sicuro.  
  > Grazie, siamo pronti per le vostre domande."*

---

## 🛡️ Q&A Cheat Sheet (Domande Tipiche delle Aziende & Risposte Vincenti)

### 1. "Perché usare un LLM se avete già le regex e spaCy?"
> **Risposta:** *"Le regex e spaCy riconoscono la sintassi (un codice fiscale o un nome proprio), ma non possono comprendere il **contesto giuridico**. Solo un LLM comprende la differenza tra un nome legittimamente inserito in una graduatoria di concorso pubblico (trasparenza lecita) e lo stesso nome associato all'erogazione di un sussidio di povertà (illecito ex Art. 26 D.Lgs. 33/2013)."*

### 2. "Come garantite che l'LLM non allucini norme o articoli inesistenti?"
> **Risposta:** *"Adottiamo un'architettura RAG ancorata al nostro corpus verificato di provvedimenti e linee guida del Garante della Privacy. L'LLM opera a temperatura zero con output forzato in formato JSON vincolato, citando esclusivamente norme e precedenti presenti nella base di conoscenza validata."*

### 3. "E se il documento caricato fosse una scansione o un'immagine?"
> **Risposta:** *"La nostra architettura è modulare: nella roadmap a breve termine la pipeline include un modulo OCR on-premise (es. Tesseract o PaddleOCR) prima della fase di pseudonimizzazione, preservando il nostro principio cardine: nessun dato in chiaro lascia mai l'infrastruttura locale."*
