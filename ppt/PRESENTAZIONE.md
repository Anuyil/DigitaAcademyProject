# 🛡️ Albo Sicuro — Pitch Deck (Hackathon Campionato Universitario AI)

> **Evento:** Hackathon Campionato Universitario AI 2026 — DIGITA Academy / AI2B (Napoli)  
> **Traccia:** 2. PRIVACY — Privacy & Security Auditor per Smart City e PA  
> **Giuria Corporate:** **Deloitte**, **DXC Technology**, **Enel**  
> **Durata stimata:** 3:30 – 4:00 minuti  

---

## 🎯 Match Strategico con i Giurati Corporate (Le "Leve Emotive")

Per conquistare questa giuria, ogni partner deve ritrovare la propria missione aziendale nella vostra soluzione:

| Azienda | Mission & Focus | Cosa vogliono sentirsi dire (Trigger) | Come risponde Albo Sicuro |
| :--- | :--- | :--- | :--- |
| **Deloitte** | Risk Advisory, Regulatory Compliance, Trustworthy AI, Governance DPO | *"Come garantite che l'IA non violi a sua volta il GDPR e come quantificate la mitigazione del rischio?"* | **Zero-Knowledge AI** (pseudonimizzazione locale a monte), audit log immutabili, RAG con citazione delle ordinanze del Garante e calcolo del rischio sanzionatorio (€ 10k-50k). |
| **DXC Technology** | Enterprise Systems Integration, Mission-Critical IT, Cyber Security & SOC | *"È scalabile? Si integra con le architetture legacy della PA o è una web app isolata?"* | **Architettura Middleware API-first**, demone autonomo asincrono per monitoraggio continuo (SOC della Privacy), predisposizione per Cloud sovrano ACN. |
| **Enel** | Smart Cities, Infrastrutture Critiche, IoT, Smart Metering, Governance Urbana | *"Come si inserisce nel contesto della Smart City e della gestione dei dati urbani/cittadini?"* | Guardiano dell'ecosistema urbano: tutela delle identità digitali nelle interazioni PA-Cittadino e roadmap verso l'auditing dei flussi IoT/Smart Metering (come da traccia). |

---

## 🎬 Struttura Slide per Slide con Punti di Forza Corporate

```
[Slide 1: Hook & Vision Urbana] ──> [Slide 2: Il Rischio Regolatorio & Economico]
                 │
                 ▼
[Slide 3: La Soluzione Dual-Engine] ──> [Slide 4: Privacy by Design & Zero-Knowledge AI]
                 │
                 ▼
[Slide 5: Live Demo & Audit Trail] ──> [Slide 6: Scalabilità B2G & System Integration]
                 │
                 ▼
[Slide 7: Roadmap Smart City & Team]
```

---

### SLIDE 1: Cover & The Hook
* **Titolo Slide:** **Albo Sicuro**
* **Sottotitolo:** *Privacy & Security Auditor per la Smart City e la Pubblica Amministrazione*
* **Visual:** 
  * Logo di Albo Sicuro (scudo con nodo di rete Smart City e spunta verde di conformità).
  * Dashboard in miniatura con semafori di conformità e indicatore del demone attivo.
  * Tagline in basso: *Privacy by Design. Zero Data Leakage. Piena Conformità GDPR.*
* **Speaker Script (20-25 sec):**
  > *"Buongiorno a tutti. La Smart City si fonda sulla fiducia dei cittadini e sulla digitalizzazione dei servizi. Eppure, ogni giorno, oltre 7.900 Comuni italiani pubblicano online decine di migliaia di atti amministrativi dove, per un banale errore umano, finiscono in rete diagnosi sanitarie, disabilità di minori, ISEE e coordinate bancarie.  
  > Abbiamo ideato **Albo Sicuro**: il primo auditor autonomo che previene, intercetta e sanifica i leak di dati personali nella PA prima che diventino un danno per i cittadini e una sanzione del Garante."*

---

### SLIDE 2: Il Problema (The Risk & Regulatory Pain) — *Per Deloitte & DPO*
* **Titolo Slide:** **La trasparenza amministrativa non può distruggere la privacy**
* **I 3 Numeri dell'Esposizione al Rischio:**
  * **€ 10.000 – € 50.000:** La sanzione media comminata dal Garante Privacy per singolo atto non conforme (violazioni Art. 2-septies Codice Privacy e Art. 26 D.Lgs. 33/2013).
  * **15 Giorni vs Permanente:** 15 giorni di affissione legale sull'Albo, ma i file restano indicizzati su Google per anni (perdita irreversibile del diritto all'oblio).
  * **100% Errore Umano:** I funzionari comunali usano gestionali obsoleti e devono validare a mano centinaia di pagine complesse ogni giorno.
* **Visual:** Collage di provvedimenti sanzionatori reali del Garante con timbro rosso *"SANZIONATO"* e citazione delle violazioni tipiche (es. contributi per indigenza, congedi per terapie oncologiche).
* **Speaker Script (35 sec):**
  > *"La legge impone la trasparenza, ma il GDPR vieta categoricamente la diffusione di dati su salute, disagio economico e minori.  
  > Oggi la responsabilità grava tutta su funzionari lasciati soli con software legacy: basta una svista in una determina per buoni spesa per esporre l'indigenza di decine di famiglie.  
  > Non è solo una violazione etica: per l'amministrazione significa contenziosi legali, danni reputazionali e sanzioni pesantissime da parte del Garante."*

---

### SLIDE 3: La Soluzione (Dual-Engine Protection)
* **Titolo Slide:** **Albo Sicuro: Doppia Protezione, Preventiva e Continua**
* **I Due Motori del Sistema:**
  1. **Gatekeeper Preventivo (Pre-Pubblicazione):**
     * Il funzionario carica il PDF prima del rilascio.
     * Analisi semantica istantanea e classificazione di conformità.
     * Generazione del PDF bonificato con vera redazione vettoriale irreversibile.
  2. **Watchdog Continuo (Demone H24):**
     * Monitoraggio asincrono dei portali e degli albi comunali.
     * Rilevamento in tempo reale di violazioni già online e calcolo dei giorni di esposizione.
     * Alert prioritari e gestione del ciclo di vita dell'incidente per il DPO.
* **Visual:** Schema a due colonne: a sinistra l'upload interattivo con semaforo, a destra il demone che scansiona in loop i flussi web urbani.
* **Speaker Script (30 sec):**
  > *"Albo Sicuro agisce con una logica a doppio livello:  
  > A monte, come **Gatekeeper**: prima che l'atto venga reso pubblico, il funzionario lo verifica in piattaforma, ottenendo evidenza delle criticità e la versione sanificata pronta per la firma.  
  > A valle, come **Watchdog Continuo**: un demone indipendente sorveglia costantemente l'albo, segnala all'istante le falle sfuggite ai controlli, calcola i giorni di esposizione e permette di sostituire l'atto prima dell'intervento delle autorità."*

---

### SLIDE 4: Architettura & "Privacy by Design" — *Per Deloitte & DXC*
* **Titolo Slide:** **"L'IA comprende il contesto, mai l'identità" (Zero-Knowledge AI)**
* **Pilastri Architetturali:**
  * **Layer Locale di Pseudonimizzazione Deterministica:** Regex con omocodia + validazione formale (`python-stdnum` per CF e IBAN) + NER con spaCy. I nomi diventano `[PERSONA_1]`, i codici `[CF_1]`.
  * **Zero Data Leakage:** Nessun dato personale in chiaro lascia mai il perimetro locale o viene inviato ai server LLM.
  * **RAG sui Precedenti del Garante:** L'LLM motiva i verdetti citando i precedenti sanzionatori reali e gli articoli normativi precisi, azzerando le allucinazioni.
  * **Vera Redazione Vettoriale (PyMuPDF):** I dati non vengono mascherati con rettangoli grafici rimovibili, ma distrutti fisicamente dal flusso di caratteri del PDF.
* **Visual:**
  $$\text{PDF Originale} \longrightarrow \fbox{Detector Locali} \longrightarrow \text{Testo [TOKEN]} \longrightarrow \fbox{LLM + RAG Garante} \longrightarrow \fbox{True Redaction} \longrightarrow \text{PDF Sanificato}$$
* **Speaker Script (40 sec):**
  > *(Punto fondamentale per Deloitte e DXC)*  
  > *"Il rischio maggiore nell'applicare l'IA alla privacy è mandare dati sensibili su endpoint cloud esterni.  
  > Noi abbiamo adottato un'architettura **Privacy by Design e Trustworthy AI**: prima dell'analisi, un motore locale sostituisce ogni dato identificativo con token astratti. L'IA riceve solo che '[PERSONA_1] beneficia di un contributo per grave disabilità' e determina la non conformità senza mai conoscere l'identità del cittadino.  
  > E per la bonifica finale, usiamo redazione vettoriale distruttiva: il dato sensibile cessa di esistere all'interno del file."*

---

### SLIDE 5: Live Demo & Audit Trail (UX & Controllo)
* **Titolo Slide:** **Dall'Allarme alla Bonifica in 3 Clic**
* **Punti di Forza dell'Interfaccia:**
  * **Semaforo Decisionale Immediato:** Verde (Conforme), Giallo (Da verificare), Rosso (Non conforme).
  * **Explainable Compliance:** Motivazione chiara, norma violata e scheda del provvedimento Garante collegato (con importo della sanzione storica).
  * **Pannello Side-by-Side:** Vista a specchio con confronto tra documento originale e documento sanificato con gli *omissis*.
* **Visual:** Tre schermate chiave dell'applicazione:
  1. Card allarme con conteggio dei giorni di esposizione online.
  2. Modale con il precedente reale del Garante (es. *Comune di Tricase, sanzione 15.000 €*).
  3. Il viewer PDF affiancato prima/dopo la bonifica.
* **Speaker Script (30 sec):**
  > *"Ecco la soluzione in azione: il nostro demone intercetta una determina con i beneficiari dei buoni spesa e relativi ISEE.  
  > Il sistema accende il semaforo rosso e associa il precedente ufficiale: 'Attenzione, per un caso identico il Comune di Tricase è stato sanzionato per 15.000 euro'.  
  > Il responsabile visualizza i passaggi critici evidenziati e, con un singolo clic, scarica la versione bonificata pronta per la sostituzione, sanando l'incidente in pochi secondi."*

---

### SLIDE 6: Business Model & System Integration — *Per DXC & Deloitte*
* **Titolo Slide:** **Modello di Business B2G e Scalabilità Enterprise**
* **Target di Mercato:**
  * **PA Locale:** 7.900+ Comuni, Città Metropolitane e Unioni di Comuni.
  * **Sanità Pubblica:** Oltre 100 ASL e Aziende Ospedaliere con alto volume di determine e dati sanitari.
  * **Partecipate e Utility Pubbliche:** Concessionari di servizi e infrastrutture urbane.
* **Strategia di Canale & Integrazione (La proposta per i System Integrator):**
  * **Non rimpiazziamo i gestionali:** Ci posizioniamo come **Middleware API Plug-and-Play** per i player enterprise (DXC, Maggioli, Halley, Engineering) che gestiscono i contratti quadro della PA.
  * **Privacy as a Service:** Layer di certificazione preventiva *"Privacy-Verified by Albo Sicuro"*.
* **Modello di Ricavo:** Abbonamento SaaS annuale a scaglioni in base alla popolazione / volume di atti.
* **ROI Matematico:** Il canone di Albo Sicuro costa meno di una frazione di una singola sanzione del Garante o delle spese legali di un ricorso.
* **Speaker Script (30 sec):**
  > *"Il nostro modello non richiede ai Comuni di cambiare software gestionale: Albo Sicuro è progettato come middleware API integrabile nelle piattaforme che system integrator come DXC già forniscono alla PA.  
  > Per un Comune o una ASL il ritorno sull'investimento è immediato: evitare anche una sola sanzione da 20.000 euro o un contenzioso legale ripaga il canone del servizio per diversi anni, garantendo ai vertici amministrativi la serenità dell'accountability GDPR."*

---

### SLIDE 7: Roadmap Smart City & Vision — *Per Enel & Chiusura*
* **Titolo Slide:** **Il Futuro dell'Auditing di Sicurezza nella Smart City**
* **Roadmap di Sviluppo:**
  * **Q3 2026:** Modulo OCR locale on-premise per atti cartacei e scansioni storiche.
  * **Q4 2026 (Smart City & IoT):** Estensione dell'auditor ai flussi di telemetria urbana, log di smart meter e registri di videosorveglianza urbana (in piena coerenza con la traccia di hackathon).
  * **Certificazioni:** Qualificazione ACN (Agenzia Cybersicurezza Nazionale) per il catalogo Cloud della PA.
* **Team:** 3 persone con competenze bilanciate tra Data Engineering, AI/LLM e Architetture Cloud.
* **Punchline Finale:**
  > *"La vera digitalizzazione di una Smart City non consiste nel pubblicare ciecamente tutto online, ma nel tutelare i dati dei cittadini mentre si rende la città più trasparente e intelligente.  
  > Albo Sicuro trasforma la compliance da rischio paralizzante a garanzia automatica.  
  > Grazie, siamo aperti alle vostre domande."*

---

## 🎯 Consigli Tattici per le Domande della Giuria (Q&A)

### Domanda probabile da DELOITTE:
> *"Come si posiziona il vostro strumento rispetto alla figura del DPO (Data Protection Officer) e all'accountability?"*
* **La vostra risposta vincente:**  
  *"Albo Sicuro non sostituisce il DPO, ne amplifica le capacità. Oggi il DPO fa controlli a campione ex-post. Albo Sicuro gli fornisce una dashboard centralizzata, un audit trail immutabile con hash SHA-256 di ogni documento analizzato e una retention policy automatica a 10 giorni, realizzando la vera accountability richiesta dall'Art. 5.2 del GDPR."*

### Domanda probabile da DXC TECHNOLOGY:
> *"Se un grande Comune processa 5.000 atti al giorno, come scala l'architettura e dove girano i modelli?"*
* **La vostra risposta vincente:**  
  *"L'architettura è a microservizi asincroni: il preprocessing regex/spaCy è estremamente leggero e viaggia a centinaia di pagine al secondo; l'LLM locale (Ollama con Qwen) o API compatibile interviene solo per la decisione semantica ad alta complessità, con un layer di caching sha256 su disco che azzera i costi di inferenza per testi ricorrenti. Può girare interamente on-premise o su infrastruttura sovereign cloud certificata ACN."*

### Domanda probabile da ENEL:
> *"Come si collega questa soluzione all'infrastruttura di una Smart City oltre ai documenti PDF?"*
* **La vostra risposta vincente:**  
  *"La pipeline core 'Detectors $\rightarrow$ Pseudonimizzazione $\rightarrow$ Semantic Audit' è agnostica rispetto al formato d'ingresso. Lo stesso motore che oggi audita un atto amministrativo, domani audita i log di telemetria degli smart meter o i registri di accesso ai varchi ZTL e videosorveglianza, rilevando pattern di leak (ad esempio associazioni anomale tra identificativo del contatore/targa e dati personali del residente) prima che escano sul cloud urbano."*
