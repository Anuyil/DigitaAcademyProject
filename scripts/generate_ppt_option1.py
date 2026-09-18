import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_option_1_presentation():
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Palette pulita e moderna
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
    C_FRAME_BG = RGBColor(241, 245, 249)   # #F1F5F9 Mockup window background
    
    blank_layout = prs.slide_layouts[6]
    
    def set_slide_background(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="ALBO SICURO — CAMPIONATO UNIVERSITARIO AI (TRACCIA PRIVACY)"):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.35))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        p_c = tf_c.paragraphs[0]
        p_c.text = category_text.upper()
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = C_BLUE
        
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.7))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = C_TEXT_MAIN

    def add_speaker_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    def add_browser_frame(slide, left, top, width, height, window_title="Albo Sicuro — Web App"):
        # Outer window
        win = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        win.fill.solid()
        win.fill.fore_color.rgb = C_WHITE
        win.line.color.rgb = RGBColor(203, 213, 225)
        win.line.width = Pt(1.5)
        
        # Window Header Bar
        hbar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.45))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = RGBColor(241, 245, 249)
        hbar.line.color.rgb = RGBColor(203, 213, 225)
        hbar.line.width = Pt(1)
        
        # 3 window buttons (red, yellow, green)
        for b_i, b_col in enumerate([RGBColor(239, 68, 68), RGBColor(245, 158, 11), RGBColor(16, 185, 129)]):
            dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, left + Inches(0.15 + b_i * 0.22), top + Inches(0.14), Inches(0.15), Inches(0.15))
            dot.fill.solid()
            dot.fill.fore_color.rgb = b_col
            dot.line.fill.background()
            
        # Address bar / title
        tb = slide.shapes.add_textbox(left + Inches(1.0), top + Inches(0.05), width - Inches(1.2), Inches(0.35))
        tf_tb = tb.text_frame
        p_tb = tf_tb.paragraphs[0]
        p_tb.text = f"🔒 https://albo-sicuro.local {window_title}"
        p_tb.font.size = Pt(9.5)
        p_tb.font.color.rgb = C_TEXT_MUTED

        return win

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
    # SLIDE 5: DEMO 1 — IL CONTROLLO PREVENTIVO (/upload)
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, C_BG_LIGHT)
    add_header(s5, "Demo: Il Controllo Preventivo Prima della Pubblicazione", "INTERFACCIA WEB APP — FLUSSO PREVENTIVO /UPLOAD")
    
    # Left Frame for Screenshot / Live Demo Placeholder
    add_browser_frame(s5, Inches(0.8), Inches(1.7), Inches(7.5), Inches(5.1), "/upload — Verifica Atto")
    
    # Inner Drop/Screenshot Placeholder Container
    holder5 = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.1), Inches(2.4), Inches(6.9), Inches(4.1))
    holder5.fill.solid()
    holder5.fill.fore_color.rgb = RGBColor(248, 250, 252)
    holder5.line.color.rgb = RGBColor(148, 163, 184)
    holder5.line.width = Pt(1.5)
    
    tf_h5 = holder5.text_frame
    tf_h5.margin_top = Inches(1.2)
    tf_h5.word_wrap = True
    ph5_1 = tf_h5.paragraphs[0]
    ph5_1.text = "🖼️ [ SPAZIO PER SCREENSHOT / DEMO LIVE ]"
    ph5_1.font.size = Pt(15)
    ph5_1.font.bold = True
    ph5_1.font.color.rgb = C_BLUE
    ph5_1.alignment = PP_ALIGN.CENTER
    
    ph5_2 = tf_h5.add_paragraph()
    ph5_2.text = "Schermata di Upload: Drag & Drop del PDF, Semaforo Rosso\ne Pannello 'Cosa vede l'IA' con testo pseudonimizzato"
    ph5_2.font.size = Pt(11)
    ph5_2.font.color.rgb = C_TEXT_MUTED
    ph5_2.alignment = PP_ALIGN.CENTER
    
    # Right Column: Spiegazione Punti Chiave dell'Interfaccia
    side5 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.6), Inches(1.7), Inches(3.9), Inches(5.1))
    side5.fill.solid()
    side5.fill.fore_color.rgb = C_CARD_BG
    side5.line.color.rgb = C_CARD_BORDER
    side5.line.width = Pt(1)
    
    tf_s5 = side5.text_frame
    tf_s5.margin_top = Inches(0.3)
    tf_s5.margin_left = Inches(0.25)
    tf_s5.margin_right = Inches(0.25)
    tf_s5.word_wrap = True
    
    ps5_t = tf_s5.paragraphs[0]
    ps5_t.text = "Cosa Mostra la Web App:"
    ps5_t.font.size = Pt(15)
    ps5_t.font.bold = True
    ps5_t.font.color.rgb = C_TEXT_MAIN
    ps5_t.space_after = Pt(12)
    
    bullets5 = [
        ("1. Drag & Drop Intuitivo", "Caricamento istantaneo di qualsiasi atto amministrativo in formato PDF."),
        ("2. Semaforo Decisionale", "Alert visivo immediato con la motivazione della violazione (es. dati salute o disagio economico)."),
        ("3. Trasparenza 'Cosa Vede l'IA'", "Confronto visivo tra il testo originale e il testo pseudonimizzato inviato al modello."),
        ("4. Download PDF Bonificato", "Pulsante per scaricare direttamente il PDF corretto con le diciture 'omissis'.")
    ]
    for b_t, b_d in bullets5:
        pb1 = tf_s5.add_paragraph()
        pb1.text = f"• {b_t}"
        pb1.font.size = Pt(12)
        pb1.font.bold = True
        pb1.font.color.rgb = C_BLUE
        pb1.space_before = Pt(6)
        
        pb2 = tf_s5.add_paragraph()
        pb2.text = f"  {b_d}"
        pb2.font.size = Pt(10.5)
        pb2.font.color.rgb = C_TEXT_MUTED
        pb2.space_after = Pt(4)
        
    add_speaker_notes(s5,
        "Mostriamo ora la prima funzionalità della Web App: il controllo preventivo all'indirizzo /upload. "
        "Il funzionario trascina il PDF della determina prima di pubblicarla. "
        "In pochi secondi il sistema analizza il documento, accende il semaforo rosso e mostra con trasparenza "
        "il pannello 'Cosa vede l'IA': a sinistra il testo originale, a destra il testo con i segnaposto pseudonimizzati. "
        "Con un solo clic, l'utente scarica il PDF già bonificato e conforme.")

    # ==========================================
    # SLIDE 6: DEMO 2 — LA DASHBOARD LIVE & DEMONE H24 (/)
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, C_BG_LIGHT)
    add_header(s6, "Demo: Dashboard Live & Monitoraggio H24 del Demone", "INTERFACCIA WEB APP — DASHBOARD DI CONTROLLO CONTINUO /")
    
    # Left Frame for Screenshot / Live Demo Placeholder
    add_browser_frame(s6, Inches(0.8), Inches(1.7), Inches(7.5), Inches(5.1), "/ — Dashboard Live Monitoraggio")
    
    # Inner Drop/Screenshot Placeholder Container
    holder6 = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.1), Inches(2.4), Inches(6.9), Inches(4.1))
    holder6.fill.solid()
    holder6.fill.fore_color.rgb = RGBColor(248, 250, 252)
    holder6.line.color.rgb = RGBColor(148, 163, 184)
    holder6.line.width = Pt(1.5)
    
    tf_h6 = holder6.text_frame
    tf_h6.margin_top = Inches(1.2)
    tf_h6.word_wrap = True
    ph6_1 = tf_h6.paragraphs[0]
    ph6_1.text = "🖼️ [ SPAZIO PER SCREENSHOT / DEMO LIVE ]"
    ph6_1.font.size = Pt(15)
    ph6_1.font.bold = True
    ph6_1.font.color.rgb = C_GREEN
    ph6_1.alignment = PP_ALIGN.CENTER
    
    ph6_2 = tf_h6.add_paragraph()
    ph6_2.text = "Schermata Dashboard: Card Metriche, Indicatore Demone Attivo\ne Feed degli Allarmi con giorni di esposizione rimanenti"
    ph6_2.font.size = Pt(11)
    ph6_2.font.color.rgb = C_TEXT_MUTED
    ph6_2.alignment = PP_ALIGN.CENTER
    
    # Right Column: Spiegazione Punti Chiave Dashboard
    side6 = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.6), Inches(1.7), Inches(3.9), Inches(5.1))
    side6.fill.solid()
    side6.fill.fore_color.rgb = C_CARD_BG
    side6.line.color.rgb = C_CARD_BORDER
    side6.line.width = Pt(1)
    
    tf_s6 = side6.text_frame
    tf_s6.margin_top = Inches(0.3)
    tf_s6.margin_left = Inches(0.25)
    tf_s6.margin_right = Inches(0.25)
    tf_s6.word_wrap = True
    
    ps6_t = tf_s6.paragraphs[0]
    ps6_t.text = "Punti di Forza della Dashboard:"
    ps6_t.font.size = Pt(15)
    ps6_t.font.bold = True
    ps6_t.font.color.rgb = C_TEXT_MAIN
    ps6_t.space_after = Pt(12)
    
    bullets6 = [
        ("1. Indicatore Demone Attivo", "Mostra l'orario dell'ultimo controllo in tempo reale ('Ultimo controllo 4s fa')."),
        ("2. Card Riassuntive", "Contatori immediati: Atti monitorati, Non conformi e Gravità alta aperti."),
        ("3. Feed Allarmi Live", "Ogni nuovo atto non conforme compare in cima con animazione ed evidenziazione."),
        ("4. Countdown Esposizione", "Mostra i giorni di esposizione rimanenti rispetto ai 15 giorni di affissione legale.")
    ]
    for b_t, b_d in bullets6:
        pb1 = tf_s6.add_paragraph()
        pb1.text = f"• {b_t}"
        pb1.font.size = Pt(12)
        pb1.font.bold = True
        pb1.font.color.rgb = C_GREEN
        pb1.space_before = Pt(6)
        
        pb2 = tf_s6.add_paragraph()
        pb2.text = f"  {b_d}"
        pb2.font.size = Pt(10.5)
        pb2.font.color.rgb = C_TEXT_MUTED
        pb2.space_after = Pt(4)
        
    add_speaker_notes(s6,
        "Passiamo ora alla seconda anima di Albo Sicuro: la Dashboard Live. "
        "In alto notiamo l'indicatore verde che pulsa: il demone è attivo e interroga l'albo ogni pochi secondi. "
        "Le card mostrano il quadro complessivo dell'ente. "
        "Nel feed allarmi, ogni atto a rischio viene evidenziato con la categoria di violazione e il countdown dei giorni di esposizione: "
        "questo permette al responsabile di intervenire prima che l'atto venga segnalato o indicizzato in modo irreversibile.")

    # ==========================================
    # SLIDE 7: DEMO 3 — DETTAGLIO REPORT & CONFRONTO SIDE-BY-SIDE (/reports)
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, C_BG_LIGHT)
    add_header(s7, "Demo: Dettaglio Violazione, Precedente Garante e Risoluzione", "INTERFACCIA WEB APP — GESTIONE REPORT E BONIFICA /REPORTS/{ID}")
    
    # Left Frame for Screenshot / Live Demo Placeholder
    add_browser_frame(s7, Inches(0.8), Inches(1.7), Inches(7.5), Inches(5.1), "/reports/4 — Dettaglio Report e Sanificazione")
    
    # Inner Drop/Screenshot Placeholder Container
    holder7 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.1), Inches(2.4), Inches(6.9), Inches(4.1))
    holder7.fill.solid()
    holder7.fill.fore_color.rgb = RGBColor(248, 250, 252)
    holder7.line.color.rgb = RGBColor(148, 163, 184)
    holder7.line.width = Pt(1.5)
    
    tf_h7 = holder7.text_frame
    tf_h7.margin_top = Inches(1.2)
    tf_h7.word_wrap = True
    ph7_1 = tf_h7.paragraphs[0]
    ph7_1.text = "🖼️ [ SPAZIO PER SCREENSHOT / DEMO LIVE ]"
    ph7_1.font.size = Pt(15)
    ph7_1.font.bold = True
    ph7_1.font.color.rgb = C_AMBER
    ph7_1.alignment = PP_ALIGN.CENTER
    
    ph7_2 = tf_h7.add_paragraph()
    ph7_2.text = "Schermata Report Dettaglio: Viewer PDF Affiancati (Originale vs Sanificato),\nCard del Precedente Garante e Tasti di Risoluzione Incidente"
    ph7_2.font.size = Pt(11)
    ph7_2.font.color.rgb = C_TEXT_MUTED
    ph7_2.alignment = PP_ALIGN.CENTER
    
    # Right Column: Spiegazione Punti Chiave Report
    side7 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.6), Inches(1.7), Inches(3.9), Inches(5.1))
    side7.fill.solid()
    side7.fill.fore_color.rgb = C_CARD_BG
    side7.line.color.rgb = C_CARD_BORDER
    side7.line.width = Pt(1)
    
    tf_s7 = side7.text_frame
    tf_s7.margin_top = Inches(0.3)
    tf_s7.margin_left = Inches(0.25)
    tf_s7.margin_right = Inches(0.25)
    tf_s7.word_wrap = True
    
    ps7_t = tf_s7.paragraphs[0]
    ps7_t.text = "Funzionalità di Risoluzione:"
    ps7_t.font.size = Pt(15)
    ps7_t.font.bold = True
    ps7_t.font.color.rgb = C_TEXT_MAIN
    ps7_t.space_after = Pt(12)
    
    bullets7 = [
        ("1. PDF Affiancati (Side-by-Side)", "Visualizzazione comparata: documento originale a sinistra e documento bonificato a destra."),
        ("2. Precedente Sanzionatorio Reale", "Card con Ente coinvolto, norma violata e importo storico della sanzione (es. € 15.000)."),
        ("3. Azioni sul Ciclo di Vita", "Pulsanti 'Segna Risolto', 'Falso Positivo' o 'Sostituisci Atto sull'Albo'."),
        ("4. Cronologia Eventi di Audit", "Tracciamento di ogni modifica per garantire l'accountability interna richiesta dal GDPR.")
    ]
    for b_t, b_d in bullets7:
        pb1 = tf_s7.add_paragraph()
        pb1.text = f"• {b_t}"
        pb1.font.size = Pt(12)
        pb1.font.bold = True
        pb1.font.color.rgb = C_AMBER
        pb1.space_before = Pt(6)
        
        pb2 = tf_s7.add_paragraph()
        pb2.text = f"  {b_d}"
        pb2.font.size = Pt(10.5)
        pb2.font.color.rgb = C_TEXT_MUTED
        pb2.space_after = Pt(4)
        
    add_speaker_notes(s7,
        "Cliccando su un allarme entriamo nel dettaglio del report. "
        "La schermata mostra i due PDF affiancati: a sinistra l'atto originario con i dati personali esposti, a destra la versione sanificata dal nostro algoritmo con la dicitura 'omissis'. "
        "Inoltre, una card evidenzia il precedente ufficiale del Garante: questo rende chiaro all'amministrazione perché l'atto è illecito e quale sarebbe la sanzione. "
        "Con un clic l'atto viene sostituito all'albo e l'incidente viene marcato come risolto nell'audit trail.")

    # ==========================================
    # SLIDE 8: VALORE OPERATIVO, MODELLO DI PRICING & ROI PER LA PA
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, C_BG_LIGHT)
    add_header(s8, "Valore Operativo, Modello di Pricing & ROI per la PA", "SOSTENIBILITÀ ECONOMICA & IMPATTO OPERATIVO")
    
    # TOP ROW: 3 Pricing Tiers (Inches 1.55 to 3.95)
    tiers = [
        ("Tier Small", "€ 1.800 – € 2.400 / anno", "~150 – 200 € / mese", "Piccoli Comuni (< 5.000 ab.)", "Fino a 1.000 atti/anno • Demone H24 attivo • Supporto standard", C_BLUE),
        ("Tier Medium", "€ 4.500 – € 6.000 / anno", "~400 – 500 € / mese", "Comuni Medi (5.000 – 40.000 ab.)", "Fino a 5.000 atti/anno • Utenti illimitati • API per gestionali", C_GREEN),
        ("Tier Enterprise", "€ 12.000 – € 18.000 / anno", "Grandi Capoluoghi & ASL", "Grandi Enti (> 40.000 ab. & Sanità)", "Atti illimitati • Multi-settore (Sociale/Sanità) • Audit DPO", C_NAVY)
    ]
    for idx, (t_name, t_price, t_sub, t_target, t_desc, t_col) in enumerate(tiers):
        tcard = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 4.0), Inches(1.55), Inches(3.7), Inches(2.4))
        tcard.fill.solid()
        tcard.fill.fore_color.rgb = C_CARD_BG
        tcard.line.color.rgb = t_col
        tcard.line.width = Pt(1.5)
        
        # Color bar
        bar = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8 + idx * 4.0), Inches(1.55), Inches(3.7), Inches(0.35))
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
        
    # BOTTOM ROW: 3 Operational & Strategic Pillars (Inches 4.15 to 6.95)
    pillars_b2g = [
        ("Azzeramento Sanzioni", "ROI Matematico Immediato", "Evitare anche una singola sanzione del Garante (€ 10k–50k) ripaga da 3 a 5 anni di canone dell'ente, azzerando le spese legali e tutelando i dirigenti dal danno erariale della Corte dei Conti.", C_GREEN),
        ("90% Risparmio di Tempo", "Automazione per il Personale", "I funzionari comunali non devono più rileggere a mano parola per parola centinaia di pagine: l'IA evidenzia solo le criticità e genera la versione conforme in 3 clic.", C_BLUE),
        ("Zero Burocrazia MePA", "Affidamento Diretto & Leggerezza", "Acquisto immediato sotto soglia D.Lgs. 36/2023 (< € 140k) senza bandire gare d'appalto. Web app leggera integrabile via API nei gestionali già in uso (Maggioli, Halley).", C_AMBER)
    ]
    for idx, (p_t, p_sub, p_d, p_c) in enumerate(pillars_b2g):
        pcard = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 4.0), Inches(4.15), Inches(3.7), Inches(2.8))
        pcard.fill.solid()
        pcard.fill.fore_color.rgb = C_CARD_BG
        pcard.line.color.rgb = C_CARD_BORDER
        pcard.line.width = Pt(1)
        
        bar_b = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8 + idx * 4.0), Inches(4.15), Inches(3.7), Inches(0.12))
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
        
    add_speaker_notes(s8,
        "Quanto vale e quanto costa Albo Sicuro alla Pubblica Amministrazione? "
        "Abbiamo integrato efficienza operativa e sostenibilità economica: "
        "Sul piano operativo, facciamo risparmiare fino al 90% del tempo al personale comunale, evitando di dover controllare a mano centinaia di pagine di atti. "
        "Sul piano economico, offriamo un modello SaaS a canone annuale all-inclusive scalabile per dimensione dell'ente: "
        "da circa 1.800 €/anno per i piccoli Comuni, a 4.500 €/anno per i Comuni medi, fino a 12.000-18.000 €/anno per capoluoghi e ASL. "
        "Per la PA l'acquisto è immediato: rientra negli affidamenti diretti sotto soglia sul MePA (< 140k €), "
        "e una singola sanzione del Garante evitata ripaga il servizio per oltre 4 anni, tutelando i dirigenti dal danno erariale.")

    # ==========================================
    # SLIDE 9: ROADMAP, VISION & TEAM
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, C_BG_DARK)
    
    t9_box = s9.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(1.0))
    tf9 = t9_box.text_frame
    p9 = tf9.paragraphs[0]
    p9.text = "Rendere la Trasparenza Finalmente Sicura"
    p9.font.size = Pt(32)
    p9.font.bold = True
    p9.font.color.rgb = C_WHITE
    
    r_steps = [
        ("Q3 2026", "OCR Locale Privacy-Preserving", "Integrazione OCR on-premise per analizzare atti cartacei storici e scansioni senza inviare immagini all'esterno."),
        ("Q4 2026", "Estensione Smart City & IoT", "Auditing dei flussi di telemetria urbana, log di smart meter e registri videosorveglianza urbana (Traccia Hackathon)."),
        ("Conformità", "Qualificazione Cloud ACN", "Ospitalità su infrastrutture cloud conformi ai requisiti dell'Agenzia per la Cybersicurezza Nazionale.")
    ]
    for idx, (time_b, r_title, r_desc) in enumerate(r_steps):
        rcard = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 4.0), Inches(2.2), Inches(3.7), Inches(3.2))
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
        
    tcard = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.8), Inches(11.7), Inches(1.1))
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
    
    add_speaker_notes(s9,
        "La digitalizzazione della Pubblica Amministrazione non deve mai avvenire a spese della dignità e della privacy dei cittadini. "
        "Con Albo Sicuro la trasparenza diventa finalmente sicura, garantita e conforme per tutti. "
        "Grazie per l'attenzione, siamo pronti per le vostre domande!")

    # Save to finale
    out_path = os.path.join(os.getcwd(), "Albo_Sicuro_Pitch_Finale.pptx")
    prs.save(out_path)
    print(f"Presentation saved successfully to: {out_path}")
    
    # Also try saving to Albo_Sicuro_Pitch_Con_Demo.pptx if not locked
    try:
        alt_path = os.path.join(os.getcwd(), "Albo_Sicuro_Pitch_Con_Demo.pptx")
        prs.save(alt_path)
    except Exception:
        pass

if __name__ == '__main__':
    create_option_1_presentation()
