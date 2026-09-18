import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation_with_screenshots():
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Palette
    C_BG_DARK = RGBColor(15, 23, 42)        # #0F172A Slate 900
    C_BG_LIGHT = RGBColor(248, 250, 252)    # #F8FAFC Slate 50
    C_WHITE = RGBColor(255, 255, 255)
    C_NAVY = RGBColor(30, 41, 59)          # #1E293B Slate 800
    C_CARD_BG = RGBColor(255, 255, 255)
    C_CARD_BORDER = RGBColor(226, 232, 240)# #E2E8F0
    C_BLUE = RGBColor(37, 99, 235)         # #2563EB Primary Blue
    C_BLUE_LIGHT = RGBColor(239, 246, 255) # #EFF6FF
    C_GREEN = RGBColor(16, 185, 129)       # #10B981 Success Green
    C_GREEN_LIGHT = RGBColor(236, 253, 245)# #ECFDF5
    C_RED = RGBColor(239, 68, 68)          # #EF4444 Danger Red
    C_AMBER = RGBColor(245, 158, 11)       # #F59E0B Warning Amber
    C_TEXT_MAIN = RGBColor(15, 23, 42)     # #0F172A
    C_TEXT_MUTED = RGBColor(100, 116, 139) # #64748B
    
    blank_layout = prs.slide_layouts[6]
    
    def set_slide_background(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="ALBO SICURO — CAMPIONATO UNIVERSITARIO AI (TRACCIA PRIVACY)"):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(11.7), Inches(0.35))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        p_c = tf_c.paragraphs[0]
        p_c.text = category_text.upper()
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = C_BLUE
        
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.7))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(23)
        p_t.font.bold = True
        p_t.font.color.rgb = C_TEXT_MAIN

    def add_speaker_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    def add_screenshot_slide(slide, title, category, img_filename, window_title, right_title, right_subtitle, bullets, notes):
        add_header(slide, title, category)
        
        # Screenshot area: Width 7.7 inches, Height 4.81 inches (matches 1024x640 aspect ratio 1.6:1)
        left_s = Inches(0.8)
        top_s = Inches(1.7)
        w_s = Inches(7.7)
        h_s = Inches(4.81)
        
        # Outer card frame
        win_frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_s, top_s, w_s, h_s)
        win_frame.fill.solid()
        win_frame.fill.fore_color.rgb = C_WHITE
        win_frame.line.color.rgb = RGBColor(203, 213, 225)
        win_frame.line.width = Pt(1.5)
        
        # Insert image
        img_path = os.path.join(os.getcwd(), "assets", "screenshots", img_filename)
        if os.path.exists(img_path):
            slide.shapes.add_picture(img_path, left_s + Inches(0.04), top_s + Inches(0.04), width=w_s - Inches(0.08), height=h_s - Inches(0.08))
            
        # Right Explanation Card
        right_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.75), top_s, Inches(3.78), h_s)
        right_card.fill.solid()
        right_card.fill.fore_color.rgb = C_CARD_BG
        right_card.line.color.rgb = C_CARD_BORDER
        right_card.line.width = Pt(1)
        
        tf_rc = right_card.text_frame
        tf_rc.margin_top = Inches(0.3)
        tf_rc.margin_left = Inches(0.25)
        tf_rc.margin_right = Inches(0.25)
        tf_rc.word_wrap = True
        
        pr_t = tf_rc.paragraphs[0]
        pr_t.text = right_title
        pr_t.font.size = Pt(15)
        pr_t.font.bold = True
        pr_t.font.color.rgb = C_TEXT_MAIN
        pr_t.space_after = Pt(4)
        
        pr_sub = tf_rc.add_paragraph()
        pr_sub.text = right_subtitle
        pr_sub.font.size = Pt(10)
        pr_sub.font.bold = True
        pr_sub.font.color.rgb = C_BLUE
        pr_sub.space_after = Pt(12)
        
        for b_t, b_d in bullets:
            pb1 = tf_rc.add_paragraph()
            pb1.text = f"• {b_t}"
            pb1.font.size = Pt(11.5)
            pb1.font.bold = True
            pb1.font.color.rgb = C_TEXT_MAIN
            pb1.space_before = Pt(4)
            
            pb2 = tf_rc.add_paragraph()
            pb2.text = f"  {b_d}"
            pb2.font.size = Pt(10)
            pb2.font.color.rgb = C_TEXT_MUTED
            pb2.space_after = Pt(4)
            
        add_speaker_notes(slide, notes)

    # ==========================================
    # SLIDE 1: COVER
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, C_BG_DARK)
    
    top_badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(3.2), Inches(0.45))
    top_badge.fill.solid()
    top_badge.fill.fore_color.rgb = RGBColor(30, 41, 59)
    top_badge.line.color.rgb = C_BLUE
    tf_badge = top_badge.text_frame
    pb = tf_badge.paragraphs[0]
    pb.text = "CANDIDATURA HACKATHON PRIVACY"
    pb.font.size = Pt(10.5)
    pb.font.bold = True
    pb.font.color.rgb = RGBColor(147, 197, 253)
    pb.alignment = PP_ALIGN.CENTER
    
    t1_box = s1.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(11.5), Inches(1.5))
    tf1 = t1_box.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "Albo Sicuro"
    p1.font.size = Pt(54)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    
    s1_box = s1.shapes.add_textbox(Inches(0.8), Inches(3.6), Inches(10.5), Inches(1.2))
    tfs1 = s1_box.text_frame
    tfs1.word_wrap = True
    ps1 = tfs1.paragraphs[0]
    ps1.text = "L'Auditor Intelligente che Rende la Trasparenza della PA Conforme e Sicura"
    ps1.font.size = Pt(22)
    ps1.font.color.rgb = RGBColor(203, 213, 225)
    
    pillars = [
        ("Zero-Knowledge AI", C_GREEN),
        ("Prevenzione & Monitoraggio H24", C_BLUE),
        ("Piena Conformità GDPR", C_AMBER)
    ]
    for idx, (pill_text, pill_color) in enumerate(pillars):
        pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 3.6), Inches(4.9), Inches(3.3), Inches(0.55))
        pill.fill.solid()
        pill.fill.fore_color.rgb = RGBColor(30, 41, 59)
        pill.line.color.rgb = pill_color
        tf_p = pill.text_frame
        pp = tf_p.paragraphs[0]
        pp.text = f"✓  {pill_text}"
        pp.font.size = Pt(12)
        pp.font.bold = True
        pp.font.color.rgb = C_WHITE
        pp.alignment = PP_ALIGN.CENTER
        
    f1_box = s1.shapes.add_textbox(Inches(0.8), Inches(6.3), Inches(11.5), Inches(0.5))
    tf_f1 = f1_box.text_frame
    pf1 = tf_f1.paragraphs[0]
    pf1.text = "Campionato Universitario AI 2026 | DIGITA Academy — Napoli | Team di Sviluppo Albo Sicuro"
    pf1.font.size = Pt(11)
    pf1.font.color.rgb = RGBColor(148, 163, 184)
    
    add_speaker_notes(s1, 
        "Buongiorno a tutti. Ogni giorno oltre 7.900 Comuni italiani pubblicano online decine di atti amministrativi. "
        "E ogni giorno, per un banale errore umano, finiscono liberamente accessibili sul web diagnosi mediche, "
        "disabilità di minori, ISEE e coordinate bancarie. "
        "Abbiamo creato Albo Sicuro: il primo assistente e auditor autonomo che aiuta i funzionari a individuare "
        "e correggere i dati sensibili prima e dopo la pubblicazione.")

    # ==========================================
    # SLIDE 2: IL PROBLEMA
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, C_BG_LIGHT)
    add_header(s2, "Il Dilemma della PA: Trasparenza vs Tutela della Privacy")
    
    stat_data = [
        ("€ 10.000 – € 50.000", "Sanzione media del Garante", "Comminata per singoli atti che espongono dati sanitari o disagio economico (Art. 2-septies Codice Privacy, D.Lgs. 33/2013).", C_RED),
        ("15 Giorni vs Forever", "Perdita del Diritto all'Oblio", "L'atto resta all'albo per soli 15 giorni per legge, ma rimane indicizzato e scaricabile da Google per anni.", C_AMBER),
        ("100% Errore Umano", "Zero Strumenti di Supporto", "I funzionari gestiscono a mano centinaia di pagine al giorno con software gestionali legacy privi di filtri intelligenti.", C_BLUE)
    ]
    for idx, (metric, subtitle, desc, bar_col) in enumerate(stat_data):
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 4.0), Inches(1.8), Inches(3.7), Inches(4.8))
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD_BG
        card.line.color.rgb = C_CARD_BORDER
        card.line.width = Pt(1)
        
        bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8 + idx * 4.0), Inches(1.8), Inches(3.7), Inches(0.12))
        bar.fill.solid()
        bar.fill.fore_color.rgb = bar_col
        bar.line.fill.background()
        
        tf_card = card.text_frame
        tf_card.margin_top = Inches(0.4)
        tf_card.margin_left = Inches(0.3)
        tf_card.margin_right = Inches(0.3)
        tf_card.word_wrap = True
        
        p_m = tf_card.paragraphs[0]
        p_m.text = metric
        p_m.font.size = Pt(22)
        p_m.font.bold = True
        p_m.font.color.rgb = bar_col
        p_m.space_after = Pt(8)
        
        p_st = tf_card.add_paragraph()
        p_st.text = subtitle
        p_st.font.size = Pt(15)
        p_st.font.bold = True
        p_st.font.color.rgb = C_TEXT_MAIN
        p_st.space_after = Pt(14)
        
        p_d = tf_card.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = C_TEXT_MUTED
        
    add_speaker_notes(s2,
        "La legge impone ai Comuni di pubblicare gli atti, ma il GDPR e le Linee Guida del Garante "
        "vietano categoricamente la diffusione di dati sulla salute o sul disagio economico. "
        "Oggi la responsabilità grava tutta sui singoli funzionari comunali, che devono controllare manualmente centinaia di pagine. "
        "Basta una distrazione in una determina per buoni spesa o disabilità per distruggere la privacy di una famiglia. "
        "Albo Sicuro risolve questo problema alla radice.")

    # ==========================================
    # SLIDE 3: LA SOLUZIONE DUAL-ENGINE
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, C_BG_LIGHT)
    add_header(s3, "Albo Sicuro: Protezione Preventiva e Monitoraggio Continuo")
    
    modes = [
        ("1. Modulo Preventivo (/upload)", "IL GATEKEEPER PRIMA DELLA PUBBLICAZIONE", [
            ("Upload Drag & Drop", "Il funzionario carica la bozza dell'atto amministrativo prima di renderlo pubblico."),
            ("Semaforo Decisionale", "Verdetto istantaneo: Conforme, Da Verificare o Non Conforme con motivazione normativa."),
            ("Download del PDF Bonificato", "Generazione immediata della versione sanificata con le diciture 'omissis' al posto giusto.")
        ], C_BLUE),
        ("2. Modulo Continuo (Daemon)", "IL WATCHDOG H24 SULL'ALBO PRETORIO", [
            ("Scansione Asincrona Autonoma", "Un demone in background monitora costantemente gli atti pubblicati sul portale comunale."),
            ("Rilevamento Tempestivo", "Identifica leak già online e invia allarmi istantanei al Responsabile Privacy / DPO."),
            ("Countdown di Esposizione", "Calcola i giorni rimanenti di affissione per consentire una bonifica prima di sanzioni.")
        ], C_GREEN)
    ]
    for idx, (title, sub, bullets, accent) in enumerate(modes):
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 6.0), Inches(1.8), Inches(5.7), Inches(4.8))
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD_BG
        card.line.color.rgb = C_CARD_BORDER
        card.line.width = Pt(1)
        
        strip = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1 + idx * 6.0), Inches(2.1), Inches(5.1), Inches(0.8))
        strip.fill.solid()
        strip.fill.fore_color.rgb = C_BLUE_LIGHT if idx == 0 else C_GREEN_LIGHT
        strip.line.color.rgb = accent
        tf_s = strip.text_frame
        tf_s.word_wrap = True
        ps = tf_s.paragraphs[0]
        ps.text = title
        ps.font.size = Pt(15)
        ps.font.bold = True
        ps.font.color.rgb = accent
        ps_sub = tf_s.add_paragraph()
        ps_sub.text = sub
        ps_sub.font.size = Pt(9)
        ps_sub.font.bold = True
        ps_sub.font.color.rgb = C_TEXT_MUTED
        
        b_box = s3.shapes.add_textbox(Inches(1.1 + idx * 6.0), Inches(3.1), Inches(5.1), Inches(3.3))
        tf_b = b_box.text_frame
        tf_b.word_wrap = True
        for b_idx, (b_t, b_d) in enumerate(bullets):
            pb = tf_b.paragraphs[0] if b_idx == 0 else tf_b.add_paragraph()
            pb.text = f"• {b_t}"
            pb.font.size = Pt(13)
            pb.font.bold = True
            pb.font.color.rgb = C_TEXT_MAIN
            pb.space_before = Pt(8)
            
            pbd = tf_b.add_paragraph()
            pbd.text = f"  {b_d}"
            pbd.font.size = Pt(11)
            pbd.font.color.rgb = C_TEXT_MUTED
            pbd.space_after = Pt(6)
            
    add_speaker_notes(s3,
        "Albo Sicuro agisce su due livelli: "
        "A monte, come Gatekeeper: prima della pubblicazione il funzionario carica il PDF, riceve un semaforo immediato "
        "e può scaricare subito la versione corretta con i dati oscurati. "
        "A valle, come Watchdog: un demone autonomo controlla continuamente i documenti già online, "
        "allertando l'ente sui documenti critici per permettere la sostituzione tempestiva prima dell'intervento del Garante.")

    # ==========================================
    # SLIDE 4: ARCHITETTURA & ZERO-KNOWLEDGE
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, C_BG_LIGHT)
    add_header(s4, "Tecnologia 'Privacy by Design': L'IA Vede il Contesto, Mai l'Identità")
    
    pill_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.7), Inches(11.7), Inches(0.6))
    pill_box.fill.solid()
    pill_box.fill.fore_color.rgb = C_NAVY
    pill_box.line.fill.background()
    tf_pb = pill_box.text_frame
    ppb = tf_pb.paragraphs[0]
    ppb.text = "ZERO DATA LEAKAGE: NESSUN DATO PERSONALE REALE RAGGIUNGE MAI IL MODELLO LLM"
    ppb.font.size = Pt(11)
    ppb.font.bold = True
    ppb.font.color.rgb = C_WHITE
    ppb.alignment = PP_ALIGN.CENTER
    
    steps = [
        ("1. Input Documento", "PDF Amministrativo", "Caricamento determina o delibera con testo e metadati.", C_BLUE),
        ("2. Pseudonimizzazione", "Engine Locale Off-line", "Regex avanzate + stdnum (CF, IBAN) + spaCy NER. I nomi diventano [PERSONA_1], i CF [CF_1].", C_BLUE),
        ("3. Ragionamento LLM", "Analisi Semantica Locale", "L'LLM riceve solo token anonimi, valuta il contesto normativo e cita i precedenti del Garante.", C_GREEN),
        ("4. Vera Redazione", "PyMuPDF Vettoriale", "Redazione distruttiva irreversibile: il testo viene cancellato dal codice del file, non coperto.", C_GREEN)
    ]
    for idx, (st_t, st_sub, st_d, st_col) in enumerate(steps):
        sbox = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 2.95), Inches(2.6), Inches(2.8), Inches(3.9))
        sbox.fill.solid()
        sbox.fill.fore_color.rgb = C_CARD_BG
        sbox.line.color.rgb = st_col
        sbox.line.width = Pt(1.5)
        
        sh = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8 + idx * 2.95), Inches(2.6), Inches(2.8), Inches(0.45))
        sh.fill.solid()
        sh.fill.fore_color.rgb = st_col
        sh.line.fill.background()
        tf_sh = sh.text_frame
        psh = tf_sh.paragraphs[0]
        psh.text = st_t
        psh.font.size = Pt(11)
        psh.font.bold = True
        psh.font.color.rgb = C_WHITE
        psh.alignment = PP_ALIGN.CENTER
        
        tf_sb = sbox.text_frame
        tf_sb.margin_top = Inches(0.6)
        tf_sb.margin_left = Inches(0.2)
        tf_sb.margin_right = Inches(0.2)
        tf_sb.word_wrap = True
        
        p_sub = tf_sb.paragraphs[0]
        p_sub.text = st_sub
        p_sub.font.size = Pt(13)
        p_sub.font.bold = True
        p_sub.font.color.rgb = C_TEXT_MAIN
        p_sub.space_after = Pt(10)
        
        p_desc = tf_sb.add_paragraph()
        p_desc.text = st_d
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = C_TEXT_MUTED
        
    add_speaker_notes(s4,
        "Il paradosso di usare l'IA per tutelare la privacy è il rischio di inviare dati sensibili di cittadini a modelli cloud esterni. "
        "In Albo Sicuro abbiamo applicato una vera architettura Privacy by Design: prima che il testo arrivi all'LLM, "
        "un motore locale isola e sostituisce ogni identificativo con token astratti. "
        "L'IA vede solo che [PERSONA_1] beneficia di un sussidio per disabilità e deduce la violazione senza sapere chi sia la persona. "
        "E sul PDF applichiamo una redazione vera con PyMuPDF, distruggendo fisicamente il dato dal file.")

    # ==========================================
    # SLIDE 5: LIVE DEMO 1 — DASHBOARD LIVE (01_dashboard.jpg)
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, C_BG_LIGHT)
    add_screenshot_slide(
        slide=s5,
        title="Live Demo: La Dashboard & Il Monitoraggio H24 del Demone",
        category="DEMO SCREENSHOT 1 — MONITORAGGIO CONTINUO /",
        img_filename="01_dashboard.jpg",
        window_title="Dashboard Live",
        right_title="Dashboard in Tempo Reale:",
        right_subtitle="CONTROLLO H24 DELL'ALBO PRETORIO",
        bullets=[
            ("Demone di Monitoraggio Attivo", "L'indicatore verde in alto mostra il controllo continuo in background ('Ultimo check: 7m fa')."),
            ("Contatori di Rischio Immediati", "Card chiare: 6 analizzati, 2 conformi, 3 non conformi e 1 da verificare."),
            ("Feed Dinamico degli Atti", "Tabella aggiornata automaticamente ogni 5s con tracciamento sorgente ('albo' vs 'upload')."),
            ("Priorità per Gravità", "Evidenziazione istantanea dei casi ad alta e media gravità per l'intervento immediato del DPO.")
        ],
        notes="Ecco la prima schermata reale di Albo Sicuro: la Dashboard Live. "
              "Notate in alto a destra l'indicatore 'Ultimo check: 7m fa': il demone lavora in autonomia interrogando l'albo in background. "
              "Le metriche offrono un quadro di sintesi immediato con semaforo verde, rosso e ambra. "
              "Nella tabella sottostante, ogni atto analizzato viene catalogato per sorgente e gravità della violazione."
    )

    # ==========================================
    # SLIDE 6: LIVE DEMO 2 — REPORT NON CONFORME SIDE-BY-SIDE (02_report_non_conforme_redacted.jpg)
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, C_BG_LIGHT)
    add_screenshot_slide(
        slide=s6,
        title="Live Demo: Rilevamento Violazione e Vera Redazione Vettoriale",
        category="DEMO SCREENSHOT 2 — ATTO NON CONFORME E BONIFICA /REPORTS",
        img_filename="02_report_non_conforme_redacted.jpg",
        window_title="Report Dettaglio — Non Conforme",
        right_title="Vera Redazione Vettoriale:",
        right_subtitle="CONFRONTO COMPARATO SIDE-BY-SIDE",
        bullets=[
            ("Rilevamento Determina Sussidio", "Individuata Determina 04 con beneficiari e importi di disagio economico in chiaro."),
            ("Tag di Violazione Accertata", "Badge '✗ Non conforme' con indicazione della gravità media e data di analisi."),
            ("Confronto Side-by-Side", "A sinistra il PDF originale con i dati esposti; a destra la versione sanificata generata da PyMuPDF."),
            ("Distruzione Fisica del Dato", "I dati (nome del beneficiario, indirizzo e CF) sono rimossi alla radice con veri omissis.")
        ],
        notes="Questa è la schermata di dettaglio di un atto non conforme: la Determina Sussidio Disagio 04. "
              "A sinistra vediamo il documento originale del Comune con il nome del beneficiario, l'indirizzo privato e l'ISEE in chiaro. "
              "A destra, il PDF generato istantaneamente da Albo Sicuro: i dati sensibili sono stati rimossi con una vera redazione vettoriale irreversibile. "
              "Non è una maschera grafica: il testo è stato fisicamente eliminato dal codice del file."
    )

    # ==========================================
    # SLIDE 7: LIVE DEMO 3 — MOTIVAZIONE GIURIDICA & RAG (03_report_precedente_decisioni.jpg)
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, C_BG_LIGHT)
    add_screenshot_slide(
        slide=s7,
        title="Live Demo: Explainable AI, Normativa e Precedenti del Garante",
        category="DEMO SCREENSHOT 3 — ANALISI NORMATIVA E RAG GIURISPRUDENZIALE",
        img_filename="03_report_precedente_decisioni.jpg",
        window_title="Dettaglio Violazione e Precedente",
        right_title="Trasparenza Decisionale:",
        right_subtitle="ZERO ALLUCINAZIONI E RAG NORMATIVO",
        bullets=[
            ("Frase Critica Contestata", "Evidenziazione testuale esatta: 'attestazione ISEE di 1.450,00 € e stato di disoccupazione'."),
            ("RAG Precedente del Garante", "Richiamo del caso storico reale: Comune di Tricase con sanzione comminata di € 15.000."),
            ("Decisioni per Singola Entità", "Tabella granulare che indica l'azione: [PERSONA] -> rimuovere, [ISEE] -> minimizzare."),
            ("Norma Puntuale Citata", "Riferimenti specifici: Art. 26 c. 4 D.Lgs. 33/2013 e Art. 5.1.c GDPR (Minimizzazione).")
        ],
        notes="Scendendo nel report vediamo la potenza del nostro motore di Explainable AI: "
              "Il sistema isola la frase esatta che vìola la legge e a destra richiama dalla nostra knowledge base il precedente reale: "
              "'Attenzione, per un caso analogo il Comune di Tricase è stato sanzionato dal Garante per 15.000 euro'. "
              "Sotto, la tabella 'Decisioni per entità' elenca ogni singola azione da compiere e la specifica norma violata. "
              "Questo azzera i dubbi interpretativi del funzionario e del DPO."
    )

    # ==========================================
    # SLIDE 8: LIVE DEMO 4 — CASO CONFORME ZERO FALSI POSITIVI (04_report_conforme.jpg)
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, C_BG_LIGHT)
    add_screenshot_slide(
        slide=s8,
        title="Live Demo: Distinzione Intelligente — Zero Falsi Positivi",
        category="DEMO SCREENSHOT 4 — ATTO CONFORME (GRADUATORIA CONCORSO)",
        img_filename="04_report_conforme.jpg",
        window_title="Report Atto Conforme",
        right_title="Intelligenza di Contesto:",
        right_subtitle="ZERO FALSI POSITIVI NELLA TRASPARENZA",
        bullets=[
            ("Graduatoria di Concorso Pubblico", "Analisi di una graduatoria di merito con nomi, cognomi e punteggi dei candidati ammessi."),
            ("Riconoscimento di Conformità", "Verdetto istantaneo '✓ Conforme': l'atto rispetta pienamente le Linee Guida Garante 2014."),
            ("Nessuna Redazione Inutile", "Spunta verde: 'Documento conforme - Nessuna redazione necessaria'. L'atto resta integro."),
            ("Trasparenza Amministrativa Salva", "Dimostra che Albo Sicuro non oscura a caso, ma distingue la trasparenza lecita dalle violazioni.")
        ],
        notes="Un timore tipico della PA è che l'IA sia troppo zelante e oscuri atti che per legge devono essere pubblici. "
              "Ecco la prova contraria: analizzando una graduatoria di concorso, Albo Sicuro la riconosce come lecita. "
              "Secondo le Linee Guida del Garante, pubblicare nomi e punteggi di concorsi pubblici è doveroso. "
              "Il sistema emette verdetto 'Conforme' con spunta verde e non tocca il documento, garantendo zero falsi positivi."
    )

    # ==========================================
    # SLIDE 9: MODELLO ECONOMICO & VALORE PA
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, C_BG_LIGHT)
    add_header(s9, "Valore Operativo, Modello di Pricing & ROI per la PA", "SOSTENIBILITÀ ECONOMICA & IMPATTO OPERATIVO")
    
    tiers = [
        ("Tier Small", "€ 1.800 – € 2.400 / anno", "~150 – 200 € / mese", "Piccoli Comuni (< 5.000 ab.)", "Fino a 1.000 atti/anno • Demone H24 attivo • Supporto standard", C_BLUE),
        ("Tier Medium", "€ 4.500 – € 6.000 / anno", "~400 – 500 € / mese", "Comuni Medi (5.000 – 40.000 ab.)", "Fino a 5.000 atti/anno • Utenti illimitati • API per gestionali", C_GREEN),
        ("Tier Enterprise", "€ 12.000 – € 18.000 / anno", "Grandi Capoluoghi & ASL", "Grandi Enti (> 40.000 ab. & Sanità)", "Atti illimitati • Multi-settore (Sociale/Sanità) • Audit DPO", C_NAVY)
    ]
    for idx, (t_name, t_price, t_sub, t_target, t_desc, t_col) in enumerate(tiers):
        tcard = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 4.0), Inches(1.55), Inches(3.7), Inches(2.4))
        tcard.fill.solid()
        tcard.fill.fore_color.rgb = C_CARD_BG
        tcard.line.color.rgb = t_col
        tcard.line.width = Pt(1.5)
        
        bar = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8 + idx * 4.0), Inches(1.55), Inches(3.7), Inches(0.35))
        bar.fill.solid()
        bar.fill.fore_color.rgb = t_col
        bar.line.fill.background()
        tf_bar = bar.text_frame
        p_bar = tf_bar.paragraphs[0]
        p_bar.text = t_name.upper()
        p_bar.font.size = Pt(10)
        p_bar.font.bold = True
        p_bar.font.color.rgb = C_WHITE
        p_bar.alignment = PP_ALIGN.CENTER
        
        tf_tc = tcard.text_frame
        tf_tc.margin_top = Inches(0.42)
        tf_tc.margin_left = Inches(0.2)
        tf_tc.margin_right = Inches(0.2)
        tf_tc.word_wrap = True
        
        p1 = tf_tc.paragraphs[0]
        p1.text = t_price
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = C_TEXT_MAIN
        p1.space_after = Pt(2)
        
        p2 = tf_tc.add_paragraph()
        p2.text = f"{t_sub}  •  {t_target}"
        p2.font.size = Pt(9.5)
        p2.font.bold = True
        p2.font.color.rgb = t_col
        p2.space_after = Pt(6)
        
        p3 = tf_tc.add_paragraph()
        p3.text = t_desc
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = C_TEXT_MUTED
        
    pillars_b2g = [
        ("Azzeramento Sanzioni", "ROI Matematico Immediato", "Evitare anche una singola sanzione del Garante (€ 10k–50k) ripaga da 3 a 5 anni di canone dell'ente, azzerando le spese legali e tutelando i dirigenti dal danno erariale della Corte dei Conti.", C_GREEN),
        ("90% Risparmio di Tempo", "Automazione per il Personale", "I funzionari comunali non devono più rileggere a mano parola per parola centinaia di pagine: l'IA evidenzia solo le criticità e genera la versione conforme in 3 clic.", C_BLUE),
        ("Zero Burocrazia MePA", "Affidamento Diretto & Leggerezza", "Acquisto immediato sotto soglia D.Lgs. 36/2023 (< € 140k) senza bandire gare d'appalto. Web app leggera integrabile via API nei gestionali già in uso (Maggioli, Halley).", C_AMBER)
    ]
    for idx, (p_t, p_sub, p_d, p_c) in enumerate(pillars_b2g):
        pcard = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 4.0), Inches(4.15), Inches(3.7), Inches(2.8))
        pcard.fill.solid()
        pcard.fill.fore_color.rgb = C_CARD_BG
        pcard.line.color.rgb = C_CARD_BORDER
        pcard.line.width = Pt(1)
        
        bar_b = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8 + idx * 4.0), Inches(4.15), Inches(3.7), Inches(0.12))
        bar_b.fill.solid()
        bar_b.fill.fore_color.rgb = p_c
        bar_b.line.fill.background()
        
        tf_pc = pcard.text_frame
        tf_pc.margin_top = Inches(0.25)
        tf_pc.margin_left = Inches(0.22)
        tf_pc.margin_right = Inches(0.22)
        tf_pc.word_wrap = True
        
        pp1 = tf_pc.paragraphs[0]
        pp1.text = p_t
        pp1.font.size = Pt(14)
        pp1.font.bold = True
        pp1.font.color.rgb = p_c
        pp1.space_after = Pt(2)
        
        pp2 = tf_pc.add_paragraph()
        pp2.text = p_sub
        pp2.font.size = Pt(10)
        pp2.font.bold = True
        pp2.font.color.rgb = C_TEXT_MAIN
        pp2.space_after = Pt(8)
        
        pp3 = tf_pc.add_paragraph()
        pp3.text = p_d
        pp3.font.size = Pt(9.5)
        pp3.font.color.rgb = C_TEXT_MUTED
        
    add_speaker_notes(s9,
        "Quanto vale e quanto costa Albo Sicuro alla Pubblica Amministrazione? "
        "Abbiamo integrato efficienza operativa e sostenibilità economica: "
        "Sul piano operativo, facciamo risparmiare fino al 90% del tempo al personale comunale, evitando di dover controllare a mano centinaia di pagine di atti. "
        "Sul piano economico, offriamo un modello SaaS a canone annuale all-inclusive scalabile per dimensione dell'ente: "
        "da circa 1.800 €/anno per i piccoli Comuni, a 4.500 €/anno per i Comuni medi, fino a 12.000-18.000 €/anno per capoluoghi e ASL. "
        "Per la PA l'acquisto è immediato: rientra negli affidamenti diretti sotto soglia sul MePA (< 140k €), "
        "e una singola sanzione del Garante evitata ripaga il servizio per oltre 4 anni, tutelando i dirigenti dal danno erariale.")

    # ==========================================
    # SLIDE 10: ROADMAP, VISION & TEAM
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, C_BG_DARK)
    
    t10_box = s10.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(1.0))
    tf10 = t10_box.text_frame
    p10 = tf10.paragraphs[0]
    p10.text = "Rendere la Trasparenza Finalmente Sicura"
    p10.font.size = Pt(32)
    p10.font.bold = True
    p10.font.color.rgb = C_WHITE
    
    r_steps = [
        ("Q3 2026", "OCR Locale Privacy-Preserving", "Integrazione OCR on-premise per analizzare atti cartacei storici e scansioni senza inviare immagini all'esterno."),
        ("Q4 2026", "Estensione Smart City & IoT", "Auditing dei flussi di telemetria urbana, log di smart meter e registri videosorveglianza urbana (Traccia Hackathon)."),
        ("Conformità", "Qualificazione Cloud ACN", "Ospitalità su infrastrutture cloud conformi ai requisiti dell'Agenzia per la Cybersicurezza Nazionale.")
    ]
    for idx, (time_b, r_title, r_desc) in enumerate(r_steps):
        rcard = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 4.0), Inches(2.2), Inches(3.7), Inches(3.2))
        rcard.fill.solid()
        rcard.fill.fore_color.rgb = RGBColor(30, 41, 59)
        rcard.line.color.rgb = C_BLUE
        rcard.line.width = Pt(1)
        
        tf_rc = rcard.text_frame
        tf_rc.margin_top = Inches(0.3)
        tf_rc.margin_left = Inches(0.25)
        tf_rc.margin_right = Inches(0.25)
        tf_rc.word_wrap = True
        
        pr1 = tf_rc.paragraphs[0]
        pr1.text = time_b
        pr1.font.size = Pt(14)
        pr1.font.bold = True
        pr1.font.color.rgb = C_BLUE
        pr1.space_after = Pt(6)
        
        pr2 = tf_rc.add_paragraph()
        pr2.text = r_title
        pr2.font.size = Pt(13)
        pr2.font.bold = True
        pr2.font.color.rgb = C_WHITE
        pr2.space_after = Pt(10)
        
        pr3 = tf_rc.add_paragraph()
        pr3.text = r_desc
        pr3.font.size = Pt(11)
        pr3.font.color.rgb = RGBColor(203, 213, 225)
        
    tcard = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.8), Inches(11.7), Inches(1.1))
    tcard.fill.solid()
    tcard.fill.fore_color.rgb = RGBColor(30, 41, 59)
    tcard.line.color.rgb = C_GREEN
    tf_tc = tcard.text_frame
    tf_tc.margin_left = Inches(0.3)
    tf_tc.margin_top = Inches(0.2)
    ptc1 = tf_tc.paragraphs[0]
    ptc1.text = "Team di Sviluppo Albo Sicuro — Campionato Universitario AI (DIGITA Academy / AI2B)"
    ptc1.font.size = Pt(14)
    ptc1.font.bold = True
    ptc1.font.color.rgb = C_GREEN
    ptc2 = tf_tc.add_paragraph()
    ptc2.text = "Sviluppato con Python, FastAPI, PyMuPDF, spaCy, python-stdnum e LLM locale. Grazie per l'attenzione!"
    ptc2.font.size = Pt(11)
    ptc2.font.color.rgb = RGBColor(203, 213, 225)
    
    add_speaker_notes(s10,
        "La digitalizzazione della Pubblica Amministrazione non deve mai avvenire a spese della dignità e della privacy dei cittadini. "
        "Con Albo Sicuro la trasparenza diventa finalmente sicura, garantita e conforme per tutti. "
        "Grazie per l'attenzione, siamo pronti per le vostre domande!")

    # Save to file
    out_path = os.path.join(os.getcwd(), "Albo_Sicuro_Pitch_Completo_Screenshots.pptx")
    prs.save(out_path)
    print(f"Presentation saved successfully to: {out_path}")
    
    try:
        alt_path = os.path.join(os.getcwd(), "Albo_Sicuro_Pitch_Finale.pptx")
        prs.save(alt_path)
        print(f"Also updated: {alt_path}")
    except Exception as e:
        print(f"Could not update Albo_Sicuro_Pitch_Finale.pptx (likely open in PowerPoint): {e}")

if __name__ == '__main__':
    create_presentation_with_screenshots()
