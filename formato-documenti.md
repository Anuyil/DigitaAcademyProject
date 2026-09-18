# Albo Sicuro — Formato dei dati da raccogliere

Due file JSON diversi, con scopo diverso. Non mischiare i contenuti.

---

## 1. `data/schede_provvedimenti.json` — i precedenti reali (RAG)

Sono i casi veri del Garante Privacy. Servono all'LLM per citare un precedente
pertinente e motivare la gravità. **Chi li scrive**: chi ha fatto la ricerca sui
provvedimenti reali (non serve inventare nulla, solo sintetizzare casi veri).

### Schema

```json
{
  "id_provvedimento": "stringa breve univoca, es. 'ordinanza-3-2020'",
  "ente": "tipo di ente coinvolto nel caso reale, es. 'Comune'",
  "tipo_atto": "determina_dirigenziale | delibera | ordinanza | graduatoria | altro",
  "dati_esposti": ["lista breve, es. 'patologia', 'iban'"],
  "categoria_violazione": "salute | disagio_economico | minori | giudiziario | dati_economici | altro",
  "norma_violata": "articolo/norma citata nel provvedimento reale",
  "giorni_esposizione": null,
  "sanzione_euro": 10000,
  "descrizione_fatti": "2-3 frasi: cosa conteneva l'atto, perché è stato ritenuto eccedente. NIENTE nomi o dati reali di persone — solo il tipo di informazione."
}
```

Note sui campi:
- `categoria_violazione` è il campo che userà `find_precedent()` per il filtro — usate sempre uno di questi 5 valori, non inventatene altri senza avvisare chi scrive `core/precedents.py`.
- `giorni_esposizione`: mettetelo solo se il provvedimento lo specifica esplicitamente (es. "pubblicato per 8 mesi invece dei 15 giorni previsti"), altrimenti `null`.
- `sanzione_euro`: numero, senza simbolo. Se il provvedimento non è un'ordinanza-ingiunzione (es. è solo un provvedimento di oscuramento senza sanzione pecuniaria), mettete `0` e scrivetelo in `descrizione_fatti`.
- `descrizione_fatti` non deve MAI contenere un nome reale, un codice fiscale reale, o dettagli che permettano di risalire alla persona coinvolta nel caso originale — anche se il provvedimento pubblico li riporta parzialmente omessi. Riassumete solo la tipologia del dato e il motivo della violazione.

### Esempio già pronto (potete usarlo com'è)

```json
{
  "id_provvedimento": "ordinanza-3-2020",
  "ente": "Comune",
  "tipo_atto": "determina_dirigenziale",
  "dati_esposti": ["patologia", "iban"],
  "categoria_violazione": "salute",
  "norma_violata": "art. 2-septies c.8 Codice privacy; art. 5.1.c GDPR",
  "giorni_esposizione": null,
  "sanzione_euro": 10000,
  "descrizione_fatti": "Determina dirigenziale relativa a un'istanza giudiziale di un dipendente per un beneficio connesso a malattia: pubblicata con indicazione della patologia e con l'IBAN del legale incaricato dal Comune, dato ritenuto eccedente rispetto alle finalità dell'atto."
}
```

**Target**: 15-20 schede di questo tipo. Coprire almeno le 5 categorie (salute, disagio_economico, minori, giudiziario, dati_economici).

---

## 2. `data/dataset/` + `data/dataset/labels.json` — i documenti di prova

Sono i PDF che userete per popolare la demo (`scripts/seed.py`) e per testare che
la pipeline funzioni. **Tutti inventati** — mai un documento reale scaricato da un
albo con dati di persone vere.

### Come costruire ogni documento

Prendete come canovaccio UNA scheda del file precedente (stessa `categoria_violazione`
e `tipo_atto`), scrivete un atto amministrativo fittizio con la stessa struttura del
problema, ma:
- nomi e cognomi inventati
- **codici fiscali finti ma validi**: generateli con `python-stdnum` o un generatore online di CF sintatticamente corretti (carattere di controllo valido), mai un CF vero
- IBAN nello stesso modo: formato valido, valori inventati
- indirizzi plausibili ma non reali (via inventata, numero civico)

Servono sia atti **non conformi** (con il problema) sia atti **conformi** (per
verificare che il sistema non segnali falsi positivi).

### Schema di `labels.json`

```json
{
  "file": "nome_del_pdf.pdf",
  "conforme": false,
  "categoria_violazione": "salute",
  "tipo_atto": "determina_dirigenziale",
  "id_provvedimento_origine": "ordinanza-3-2020",
  "passaggi_problematici": [
    "frase esatta, copiata dal testo del PDF, che contiene il problema"
  ]
}
```

Per un documento conforme:
```json
{
  "file": "graduatoria_concorso_01.pdf",
  "conforme": true,
  "categoria_violazione": null,
  "tipo_atto": "graduatoria",
  "id_provvedimento_origine": null,
  "passaggi_problematici": []
}
```

Note:
- `passaggi_problematici` deve contenere il testo **esatto** (copia-incolla dal PDF), non un riassunto — serve poi a verificare che il sistema lo trovi davvero, e alla pipeline per la redazione (`page.search_for`).
- `id_provvedimento_origine` collega il documento di test alla scheda del punto 1: permette di verificare che `find_precedent()` trovi il caso giusto.
- Un documento può avere più `passaggi_problematici` di categorie diverse (es. sia salute che iban) — in quel caso `categoria_violazione` mettete quella prevalente/più grave, ma elencate comunque tutti i passaggi.

### Mix consigliato per la demo (6-8 documenti totali)

| # | conforme | categoria | esempio |
|---|---|---|---|
| 1 | true | — | graduatoria di concorso, nomi legittimi |
| 2 | true | — | delibera di bilancio, nessun dato personale sensibile |
| 3 | false | salute | contributo economico con patologia indicata |
| 4 | false | disagio_economico | determina con beneficiario di sussidio nominato + importo |
| 5 | false | minori | ordinanza con nome di un minore coinvolto |
| 6 | false | dati_economici | determina con IBAN eccedente |
| 7 | false | giudiziario | atto con dettagli di una vicenda giudiziaria in corso |
| 8 | true | — | ordinanza di viabilità, solo dati istituzionali |

---

## Riepilogo per chi recupera i documenti

- **Non scaricate PDF reali da Albi Pretori con dati di persone vere** per il dataset di test — solo per farvi un'idea dello stile/formato di un atto vero, poi si scrive da zero con dati finti.
- Ogni documento di test deve poter essere ricondotto (tramite `id_provvedimento_origine`) a una scheda reale del corpus dei precedenti, così la demo mostra una catena coerente: atto → problema → precedente citato.
- Se non siete sicuri di una categoria o di quale norma citare, meglio segnare il dubbio e chiedere piuttosto che inventare una norma — il campo `norma_violata`/`norma` finisce mostrato a schermo in demo.