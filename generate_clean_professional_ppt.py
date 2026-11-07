import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = 9144000   # 10 inches (16:9 widescreen)
    prs.slide_height = 5143500  # 5.625 inches

    blank_layout = prs.slide_layouts[6]

    # Professional Color Palette
    NAVY_PRIMARY = RGBColor(30, 58, 138)    # #1E3A8A - Deep Corporate Navy
    NAVY_DARK    = RGBColor(15, 23, 42)     # #0F172A - Slate Dark
    TEAL_ACCENT  = RGBColor(13, 148, 136)   # #0D9488 - Modern Teal
    GREEN_ACCENT = RGBColor(16, 185, 129)   # #10B981 - Emerald Green
    ORANGE_WARN  = RGBColor(234, 88, 12)    # #EA580C - Warm Accent
    TEXT_MAIN    = RGBColor(30, 41, 59)     # #1E293B - Crisp Slate Text
    TEXT_MUTED   = RGBColor(100, 116, 139)  # #64748B - Muted Grey
    BG_CARD      = RGBColor(248, 250, 252)  # #F8FAFC - Soft Off-White
    BORDER_CARD  = RGBColor(226, 232, 240)  # #E2E8F0 - Subtle Border
    WHITE        = RGBColor(255, 255, 255)

    def add_slide_header(slide, title_text, section_number=None, slide_num=1):
        # Header banner bar
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, 9144000, 680000)
        banner.fill.solid()
        banner.fill.fore_color.rgb = NAVY_PRIMARY
        banner.line.color.rgb = NAVY_PRIMARY

        # Slim accent bottom line
        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 660000, 9144000, 35000)
        accent.fill.solid()
        accent.fill.fore_color.rgb = TEAL_ACCENT
        accent.line.color.rgb = TEAL_ACCENT

        # Title text
        txBox = slide.shapes.add_textbox(450000, 110000, 7500000, 480000)
        tf = txBox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        if section_number:
            p.text = f"{section_number}. {title_text}"
        else:
            p.text = title_text
        p.font.size = Pt(21)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.font.name = 'Calibri'

        # Slide number
        numBox = slide.shapes.add_textbox(8200000, 150000, 650000, 350000)
        np = numBox.text_frame.paragraphs[0]
        np.text = f"{slide_num}"
        np.alignment = PP_ALIGN.RIGHT
        np.font.size = Pt(13)
        np.font.bold = True
        np.font.color.rgb = RGBColor(203, 213, 225)
        np.font.name = 'Calibri'

        # Bottom footer
        footerBox = slide.shapes.add_textbox(450000, 4850000, 8244000, 250000)
        fp = footerBox.text_frame.paragraphs[0]
        fp.text = "Dept. of ECE, Sahyadri College of Engineering & Management (SCEM) | VTU Belagavi"
        fp.font.size = Pt(9)
        fp.font.color.rgb = TEXT_MUTED
        fp.font.name = 'Calibri'

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (Clean, Official, Professional)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    
    # White background
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, 9144000, 5143500)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = WHITE
    bg1.line.color.rgb = WHITE

    # Top institution header strip
    strip = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, 9144000, 1450000)
    strip.fill.solid()
    strip.fill.fore_color.rgb = RGBColor(241, 245, 249)
    strip.line.color.rgb = RGBColor(226, 232, 240)

    # Logos
    if os.path.exists("assets/logo_3.png"):
        s1.shapes.add_picture("assets/logo_3.png", 350000, 130000, 1300000, 1180000)
    if os.path.exists("assets/logo_4.png"):
        s1.shapes.add_picture("assets/logo_4.png", 7494000, 110000, 1300000, 1230000)

    # Header Text
    c_box = s1.shapes.add_textbox(1750000, 180000, 5600000, 1000000)
    ctf = c_box.text_frame
    ctf.word_wrap = True
    cp1 = ctf.paragraphs[0]
    cp1.text = "SAHYADRI COLLEGE OF ENGINEERING & MANAGEMENT"
    cp1.alignment = PP_ALIGN.CENTER
    cp1.font.size = Pt(13.5)
    cp1.font.bold = True
    cp1.font.color.rgb = NAVY_PRIMARY
    cp1.font.name = 'Calibri'

    cp2 = ctf.add_paragraph()
    cp2.text = "Affiliated to Visvesvaraya Technological University (VTU), Belagavi"
    cp2.alignment = PP_ALIGN.CENTER
    cp2.font.size = Pt(10)
    cp2.font.color.rgb = TEXT_MUTED
    cp2.font.name = 'Calibri'

    cp3 = ctf.add_paragraph()
    cp3.text = "DEPARTMENT OF ELECTRONICS AND COMMUNICATION ENGINEERING"
    cp3.alignment = PP_ALIGN.CENTER
    cp3.font.size = Pt(11)
    cp3.font.bold = True
    cp3.font.color.rgb = TEAL_ACCENT
    cp3.font.name = 'Calibri'

    # Badge: Mini-Project Presentation
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 3322000, 1600000, 2500000, 360000)
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(238, 242, 255)
    badge.line.color.rgb = RGBColor(199, 210, 254)
    bp = badge.text_frame.paragraphs[0]
    bp.text = "MINI-PROJECT PRESENTATION"
    bp.alignment = PP_ALIGN.CENTER
    bp.font.size = Pt(11)
    bp.font.bold = True
    bp.font.color.rgb = NAVY_PRIMARY
    bp.font.name = 'Calibri'

    # Project Title
    t_box = s1.shapes.add_textbox(600000, 2050000, 7944000, 950000)
    ttf = t_box.text_frame
    ttf.word_wrap = True
    tp1 = ttf.paragraphs[0]
    tp1.text = "SWARM-BASED SEARCH AND RECONNAISSANCE SYSTEM"
    tp1.alignment = PP_ALIGN.CENTER
    tp1.font.size = Pt(22)
    tp1.font.bold = True
    tp1.font.color.rgb = NAVY_DARK
    tp1.font.name = 'Calibri'

    tp2 = ttf.add_paragraph()
    tp2.text = "Phase 1: Custom Micro-Avionics, Monolithic Flight Controller & Dual-Tier Telemetry"
    tp2.alignment = PP_ALIGN.CENTER
    tp2.font.size = Pt(13)
    tp2.font.italic = True
    tp2.font.color.rgb = TEAL_ACCENT
    tp2.font.name = 'Calibri'

    # Team Box (Left)
    team_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 600000, 3150000, 3800000, 1550000)
    team_card.fill.solid()
    team_card.fill.fore_color.rgb = BG_CARD
    team_card.line.color.rgb = BORDER_CARD
    tt_box = s1.shapes.add_textbox(750000, 3230000, 3500000, 1400000)
    tt_tf = tt_box.text_frame
    p = tt_tf.paragraphs[0]
    p.text = "PROJECT TEAM MEMBERS:"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = NAVY_PRIMARY
    p.font.name = 'Calibri'
    members = [
        "• Neil Gibson Pinto  -  4SF22EC...",
        "• Team Member 2     -  4SF22EC...",
        "• Team Member 3     -  4SF22EC...",
        "• Team Member 4     -  4SF22EC..."
    ]
    for m in members:
        mp = tt_tf.add_paragraph()
        mp.text = m
        mp.font.size = Pt(10.5)
        mp.font.color.rgb = TEXT_MAIN
        mp.font.name = 'Calibri'

    # Guide Box (Right)
    guide_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 4744000, 3150000, 3800000, 1550000)
    guide_card.fill.solid()
    guide_card.fill.fore_color.rgb = BG_CARD
    guide_card.line.color.rgb = BORDER_CARD
    gt_box = s1.shapes.add_textbox(4894000, 3230000, 3500000, 1400000)
    gt_tf = gt_box.text_frame
    gp = gt_tf.paragraphs[0]
    gp.text = "UNDER THE GUIDANCE OF:"
    gp.font.size = Pt(11)
    gp.font.bold = True
    gp.font.color.rgb = NAVY_PRIMARY
    gp.font.name = 'Calibri'

    gp2 = gt_tf.add_paragraph()
    gp2.text = "Faculty Guide Name"
    gp2.font.size = Pt(12)
    gp2.font.bold = True
    gp2.font.color.rgb = TEXT_MAIN
    gp2.font.name = 'Calibri'

    gp3 = gt_tf.add_paragraph()
    gp3.text = "Assistant Professor\nDept. of Electronics & Communication Engineering\nSahyadri College of Engineering & Management"
    gp3.font.size = Pt(10)
    gp3.font.color.rgb = TEXT_MUTED
    gp3.font.name = 'Calibri'

    s1.notes_slide.notes_text_frame.text = (
        "Good morning respected evaluators, professors, and guide. Today, our team presents Phase 1 of our mini-project titled: "
        "'Swarm-Based Search and Reconnaissance System'. We designed, fabricated, and tested a custom monolithic micro-flight "
        "controller board engineered specifically for decentralized drone swarms."
    )

    # =========================================================================
    # SLIDE 2: CONTENTS (Clean 12-Item University Standard)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_header(s2, "Presentation Contents", None, slide_num=2)

    col1_items = [
        "1. Introduction & Problem Context",
        "2. Literature Review & Comparisons",
        "3. Research Gaps & Problem Statement",
        "4. Objectives (Two-Phase Strategy)",
        "5. Methodology & System Architecture",
        "6. Circuit Design & Hardware Implementation"
    ]
    col2_items = [
        "7. Pilot Study & Experimental Results (Phase 1)",
        "8. Scientific Novelty (Why Our System is Unique)",
        "9. Alignment with UN Sustainable Goals (SDGs)",
        "10. Research Time Plan & Work Breakdown",
        "11. Key Academic References",
        "12. Publication Status & Phase 2 Roadmap"
    ]

    # Column 1 Card
    card_c1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 500000, 850000, 3950000, 3800000)
    card_c1.fill.solid()
    card_c1.fill.fore_color.rgb = BG_CARD
    card_c1.line.color.rgb = BORDER_CARD
    t1 = s2.shapes.add_textbox(650000, 950000, 3650000, 3600000)
    tf1 = t1.text_frame
    for idx, item in enumerate(col1_items):
        p = tf1.paragraphs[0] if idx == 0 else tf1.add_paragraph()
        p.text = item
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = NAVY_PRIMARY
        p.font.name = 'Calibri'
        p.space_after = Pt(14)

    # Column 2 Card
    card_c2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 4694000, 850000, 3950000, 3800000)
    card_c2.fill.solid()
    card_c2.fill.fore_color.rgb = BG_CARD
    card_c2.line.color.rgb = BORDER_CARD
    t2 = s2.shapes.add_textbox(4844000, 950000, 3650000, 3600000)
    tf2 = t2.text_frame
    for idx, item in enumerate(col2_items):
        p = tf2.paragraphs[0] if idx == 0 else tf2.add_paragraph()
        p.text = item
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = NAVY_PRIMARY
        p.font.name = 'Calibri'
        p.space_after = Pt(14)

    s2.notes_slide.notes_text_frame.text = (
        "Here is the outline of our presentation, structured across 12 clear sections following the university evaluation format."
    )

    # =========================================================================
    # SLIDE 3: 1. INTRODUCTION & PROBLEM CONTEXT
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_header(s3, "Introduction & Problem Context", "1", slide_num=3)

    intro_cards = [
        ("Disaster Search & Rescue",
         "• In collapsed buildings, toxic leaks, or earthquakes, human entry is lethally hazardous.\n\n"
         "• Rapid scouting during the first 72 hours ('Golden Window') is vital to locate trapped survivors.",
         NAVY_PRIMARY, RGBColor(238, 242, 255)),
        ("Why Micro-Scale Drones?",
         "• Standard commercial drones (>500g, >250mm) cannot enter tight structural cavities or broken windows.\n\n"
         "• Micro-quadcopters (<65mm wheelbase, <35g) can navigate confined indoor voids with agility.",
         TEAL_ACCENT, RGBColor(240, 253, 250)),
        ("The Swarm Necessity",
         "• A single micro-drone has limited battery life (5–8 minutes) and represents a single point of failure.\n\n"
         "• A decentralized swarm divides the search grid in parallel, accelerating discovery and providing redundancy.",
         GREEN_ACCENT, RGBColor(236, 253, 245))
    ]

    for idx, (title, body, border_c, bg_c) in enumerate(intro_cards):
        x = 500000 + idx * 2750000
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, 900000, 2600000, 3750000)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_c
        card.line.color.rgb = border_c
        card.line.width = Pt(1.5)

        t = s3.shapes.add_textbox(x + 120000, 1020000, 2360000, 3500000)
        tf = t.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = border_c
        p.font.name = 'Calibri'
        p.space_after = Pt(12)

        bp = tf.add_paragraph()
        bp.text = body
        bp.font.size = Pt(11)
        bp.font.color.rgb = TEXT_MAIN
        bp.font.name = 'Calibri'

    s3.notes_slide.notes_text_frame.text = (
        "In disaster zones, sending human rescuers into unstable rubble is dangerous. Large drones cannot fit into narrow voids. "
        "Micro-drones are ideal, but a single micro-drone has short battery life and if it crashes, the mission is over. "
        "A swarm solves this by searching collaboratively and providing redundancy."
    )

    # =========================================================================
    # SLIDE 4: 2. RESEARCH GAPS & PROBLEM STATEMENT
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_header(s4, "Research Gaps & Problem Statement", "2", slide_num=4)

    gaps = [
        ("GAP 1: Centralized Wi-Fi Bottleneck",
         "Existing swarms rely on a central Wi-Fi router. In concrete rubble, Wi-Fi drops out, causing the entire swarm to fail.",
         RGBColor(254, 242, 242), RGBColor(239, 68, 68)),
        ("GAP 2: Excessive Weight & Cost (SWaP-C)",
         "Standard research drones mount heavy companion PCs (Raspberry Pi), adding >150g deadweight and costing >$400 per node.",
         RGBColor(255, 251, 235), RGBColor(245, 158, 11)),
        ("GAP 3: No Autonomous Self-Healing",
         "If an individual drone is lost or battery depleted, its search sector is abandoned unless an operator manually reconfigures it.",
         RGBColor(238, 242, 255), NAVY_PRIMARY)
    ]

    for idx, (title, desc, bg_c, border_c) in enumerate(gaps):
        y = 850000 + idx * 1050000
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 500000, y, 8144000, 920000)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_c
        card.line.color.rgb = border_c
        card.line.width = Pt(1.5)

        t = s4.shapes.add_textbox(650000, y + 80000, 7844000, 800000)
        tf = t.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = border_c
        p.font.name = 'Calibri'

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MAIN
        p2.font.name = 'Calibri'

    # Problem Statement Highlight Box
    ps = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 500000, 4050000, 8144000, 680000)
    ps.fill.solid()
    ps.fill.fore_color.rgb = NAVY_DARK
    ps.line.color.rgb = NAVY_DARK
    pst = s4.shapes.add_textbox(600000, 4100000, 7944000, 600000)
    ptf = pst.text_frame
    ptf.word_wrap = True
    pp = ptf.paragraphs[0]
    pp.text = "PROBLEM STATEMENT: To engineer an ultra-compact (<65mm, <35g AUW), sub-$15 monolithic flight computer executing deterministic 250Hz stabilization, peer-to-peer ad-hoc mesh networking, and autonomous self-healing search grid re-allocation."
    pp.font.bold = True
    pp.font.size = Pt(10.5)
    pp.font.color.rgb = WHITE
    pp.font.name = 'Calibri'

    s4.notes_slide.notes_text_frame.text = (
        "Existing solutions fail for three clear reasons: First, centralized Wi-Fi dependence. Second, high cost and weight. "
        "Third, lack of self-healing. Our problem statement directly addresses these limitations."
    )

    # =========================================================================
    # SLIDE 5: 3. OBJECTIVES & TWO-PHASE STRATEGY
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_header(s5, "Objectives & Two-Phase Implementation Strategy", "3", slide_num=5)

    # Phase 1 Box (Left) - COMPLETED
    p1 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 500000, 880000, 3950000, 3800000)
    p1.fill.solid()
    p1.fill.fore_color.rgb = RGBColor(240, 253, 244)
    p1.line.color.rgb = RGBColor(34, 197, 94)
    p1.line.width = Pt(2)

    t1 = s5.shapes.add_textbox(650000, 980000, 3650000, 3600000)
    tf1 = t1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "PHASE 1: AVIONICS & FLIGHT CORE\n[VERIFIED & DEFENDED TODAY]"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p.font.color.rgb = RGBColor(22, 101, 52)
    p.font.name = 'Calibri'
    p.space_after = Pt(10)

    p1_points = [
        ("✔ Custom Monolithic PCB (TCE_rev1):", "Designed and taped out 4-layer PCB integrating ESP32-S3, MPU-6050, and 4-channel MOSFET drivers."),
        ("✔ Deterministic 250 Hz Loop:", "Engineered hard real-time PID attitude flight control on Core 0 with zero task jitter."),
        ("✔ ExpressLRS (CRSF) Protocol:", "Decoded 420,000-baud serial RC packets with sub-5ms latency and failsafe auto-disarm."),
        ("✔ Live Telemetry Streaming:", "Streamed MAVLink attitude & heartbeat data to Mission Planner HUD via Wi-Fi UDP.")
    ]
    for head, body in p1_points:
        hp = tf1.add_paragraph()
        hp.text = head
        hp.font.bold = True
        hp.font.size = Pt(11)
        hp.font.color.rgb = NAVY_PRIMARY
        hp.font.name = 'Calibri'
        bp = tf1.add_paragraph()
        bp.text = body
        bp.font.size = Pt(10)
        bp.font.color.rgb = TEXT_MAIN
        bp.font.name = 'Calibri'
        bp.space_after = Pt(6)

    # Phase 2 Box (Right) - SCALE UP
    p2 = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 4694000, 880000, 3950000, 3800000)
    p2.fill.solid()
    p2.fill.fore_color.rgb = RGBColor(238, 242, 255)
    p2.line.color.rgb = RGBColor(99, 102, 241)
    p2.line.width = Pt(2)

    t2 = s5.shapes.add_textbox(4844000, 980000, 3650000, 3600000)
    tf2 = t2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "PHASE 2: SWARM SCALING & VISION\n[NEXT PHASE ROADMAP]"
    p.font.bold = True
    p.font.size = Pt(12.5)
    p.font.color.rgb = NAVY_PRIMARY
    p.font.name = 'Calibri'
    p.space_after = Pt(10)

    p2_points = [
        ("→ Micro-Brushless Propulsion (BLDC):", "Upgrading to 0802 motors with 4-in-1 DShot ESCs for higher power-to-weight ratio (4.5:1)."),
        ("→ Edge AI Vision & Optical Flow:", "Integrating ESP32-CAM module for indoor drift-free hover and survivor detection in GPS-denied voids."),
        ("→ Decentralized Swarm Mesh:", "Deploying multi-node peer-to-peer ESP-NOW mesh executing dynamic Voronoi self-healing."),
        ("→ Multi-Drone Flight Trials:", "Conducting live indoor search demonstrations in an obstacle testbed facility.")
    ]
    for head, body in p2_points:
        hp = tf2.add_paragraph()
        hp.text = head
        hp.font.bold = True
        hp.font.size = Pt(11)
        hp.font.color.rgb = NAVY_PRIMARY
        hp.font.name = 'Calibri'
        bp = tf2.add_paragraph()
        bp.text = body
        bp.font.size = Pt(10)
        bp.font.color.rgb = TEXT_MAIN
        bp.font.name = 'Calibri'
        bp.space_after = Pt(6)

    s5.notes_slide.notes_text_frame.text = (
        "In engineering, phased development mitigates risk. Phase 1 validates the hardest part: custom PCB tape-out, "
        "250Hz real-time PID loops, and low-latency radio communication. Phase 2 scales this verified avionics core into "
        "brushless propulsion, camera vision, and multi-agent swarm flight."
    )

    # =========================================================================
    # SLIDE 6: 4. METHODOLOGY & SYSTEM ARCHITECTURE
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_header(s6, "Methodology: System Architecture & Dual-Core Operation", "4", slide_num=6)

    # Diagram (Left 58%)
    if os.path.exists("assets/arch_diagram.png"):
        s6.shapes.add_picture("assets/arch_diagram.png", 450000, 850000, 5200000, 3850000)

    # 3 Clear Highlights Card (Right 42%)
    rc = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 5800000, 850000, 2894000, 3850000)
    rc.fill.solid()
    rc.fill.fore_color.rgb = BG_CARD
    rc.line.color.rgb = BORDER_CARD

    rt = s6.shapes.add_textbox(5900000, 950000, 2694000, 3650000)
    rtf = rt.text_frame
    rtf.word_wrap = True
    rp = rtf.paragraphs[0]
    rp.text = "CORE ARCHITECTURAL PILLARS"
    rp.font.bold = True
    rp.font.size = Pt(12)
    rp.font.color.rgb = NAVY_PRIMARY
    rp.font.name = 'Calibri'
    rp.space_after = Pt(10)

    arch_highlights = [
        ("1. Dual-Tier Radio Links:", "• Tier 1: ESP-NOW inter-agent mesh (<1ms latency, routerless).\n• Tier 2: ExpressLRS LoRa for long-range operator command override."),
        ("2. Asymmetric Dual-Core:", "• Core 0: 250Hz hard real-time PID & 20kHz PWM (Zero Jitter).\n• Core 1: Serial CRSF, mesh consensus & telemetry."),
        ("3. Monolithic Avionics:", "• Consolidated MCU, IMU, LDO, and gate drivers on a single 65mm PCB (<$10).")
    ]
    for title, desc in arch_highlights:
        tp = rtf.add_paragraph()
        tp.text = title
        tp.font.bold = True
        tp.font.size = Pt(11)
        tp.font.color.rgb = TEAL_ACCENT
        tp.font.name = 'Calibri'
        dp = rtf.add_paragraph()
        dp.text = desc
        dp.font.size = Pt(9.5)
        dp.font.color.rgb = TEXT_MAIN
        dp.font.name = 'Calibri'
        dp.space_after = Pt(8)

    s6.notes_slide.notes_text_frame.text = (
        "Here is our system architecture. Flight control requires hard real-time determinism—if Wi-Fi network traffic interrupts "
        "the gyro loop, the drone crashes. We solve this by pinning the 250Hz flight stabilization loop to Core 0, while Core 1 "
        "handles all asynchronous radio and mesh networking."
    )

    # =========================================================================
    # SLIDE 7: 5. CIRCUIT DESIGN & HARDWARE IMPLEMENTATION
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_slide_header(s7, "Circuit Design & Hardware Implementation (TCE_rev1)", "5", slide_num=7)

    # Schematic (Top Left)
    if os.path.exists("assets/schematic_export.png"):
        s7.shapes.add_picture("assets/schematic_export.png", 450000, 850000, 4800000, 2350000)

    # PCB 3D Render (Bottom Left)
    if os.path.exists("assets/board_presentation_iso.png"):
        s7.shapes.add_picture("assets/board_presentation_iso.png", 450000, 3300000, 4800000, 1400000)

    # Hardware Specs Card (Right)
    hc = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 5400000, 850000, 3294000, 3850000)
    hc.fill.solid()
    hc.fill.fore_color.rgb = BG_CARD
    hc.line.color.rgb = BORDER_CARD

    ht = s7.shapes.add_textbox(5500000, 950000, 3094000, 3650000)
    htf = ht.text_frame
    htf.word_wrap = True
    hp = htf.paragraphs[0]
    hp.text = "HARDWARE SUBSYSTEMS"
    hp.font.bold = True
    hp.font.size = Pt(12)
    hp.font.color.rgb = NAVY_PRIMARY
    hp.font.name = 'Calibri'
    hp.space_after = Pt(8)

    hw_items = [
        ("1. Power Stage (AP2112K-3.3):", "Ultra-low dropout (250mV @ 600mA) with high PSRR (>65dB) to isolate IMU gyro rails from motor voltage spikes."),
        ("2. Motor Actuation (AO3400A):", "4x N-MOSFETs (30V, 5.7A, R_DS < 30mΩ) driven by 20kHz PWM with 1N5819 Schottky flyback protection."),
        ("3. IMU Sensor (MPU-6050):", "6-DOF gyro & accelerometer on Fast I2C (400kHz DMA) at 0x68 (SDA: GPIO8, SCL: GPIO9)."),
        ("4. Receiver Header (Header J3):", "High-speed UART0 @ 420,000 baud (TXD0: GPIO43, RXD0: GPIO44) connecting ExpressLRS CRSF.")
    ]
    for head, body in hw_items:
        tp = htf.add_paragraph()
        tp.text = head
        tp.font.bold = True
        tp.font.size = Pt(10.5)
        tp.font.color.rgb = TEAL_ACCENT
        tp.font.name = 'Calibri'
        dp = htf.add_paragraph()
        dp.text = body
        dp.font.size = Pt(9.5)
        dp.font.color.rgb = TEXT_MAIN
        dp.font.name = 'Calibri'
        dp.space_after = Pt(6)

    s7.notes_slide.notes_text_frame.text = (
        "This slide shows our custom KiCad schematic and the fabricated 3D board. "
        "The power circuit uses an AP2112K LDO chosen for its high noise rejection. "
        "The motor stage uses four AO3400A MOSFETs capable of 5.7A with Schottky flyback diodes clamping back-EMF spikes."
    )

    # =========================================================================
    # SLIDE 8: 6. PILOT STUDY: EXPERIMENTAL RESULTS (PHASE 1)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_slide_header(s8, "Pilot Study: Phase 1 Experimental Results & Validation", "6", slide_num=8)

    # Top Render (Left 38%)
    if os.path.exists("assets/board_presentation_top.png"):
        s8.shapes.add_picture("assets/board_presentation_top.png", 450000, 850000, 3500000, 3850000)

    # Benchmarks (Top Right 62%)
    if os.path.exists("assets/benchmarks.png"):
        s8.shapes.add_picture("assets/benchmarks.png", 4100000, 850000, 4644000, 2300000)

    # Quantitative Verification Metrics (Bottom Right)
    qc = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 4100000, 3250000, 4644000, 1450000)
    qc.fill.solid()
    qc.fill.fore_color.rgb = BG_CARD
    qc.line.color.rgb = BORDER_CARD

    qt = s8.shapes.add_textbox(4200000, 3320000, 4444000, 1300000)
    qtf = qt.text_frame
    qtf.word_wrap = True
    qp = qtf.paragraphs[0]
    qp.text = "KEY MEASURED BENCHMARKS (PILOT STUDY)"
    qp.font.bold = True
    qp.font.size = Pt(11)
    qp.font.color.rgb = NAVY_PRIMARY
    qp.font.name = 'Calibri'

    results = [
        "• Deterministic 250 Hz Loop: 1.60 ms active execution out of 4.00 ms budget (60% idle CPU headroom, zero jitter).",
        "• Ultra-Low CRSF Latency: 4.8 ms average response @ 420kbaud (16x faster than standard Wi-Fi UDP at 78.5 ms).",
        "• Failsafe Protection: Auto-disarm and motor cut-off strictly within 500ms of packet loss.",
        "• High-Throttle Stability: Sustained 100% full throttle on 1S LiPo (30C rating) with zero brownout resets."
    ]
    for r in results:
        p = qtf.add_paragraph()
        p.text = r
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MAIN
        p.font.name = 'Calibri'
        p.space_after = Pt(2)

    s8.notes_slide.notes_text_frame.text = (
        "Here are the hard bench test results. Our 250Hz loop executes in 1.60 ms, leaving 60% idle headroom on Core 0. "
        "ExpressLRS latency clocked at 4.8 ms—16 times faster than typical Wi-Fi. Failsafe auto-disarm works reliably within 500 ms."
    )

    # =========================================================================
    # SLIDE 9: 7. SCIENTIFIC NOVELTY (Why Unique)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_slide_header(s9, "Scientific Novelty & Unique Contributions", "7", slide_num=9)

    # Voronoi Diagram (Left 58%)
    if os.path.exists("assets/voronoi_diagram.png"):
        s9.shapes.add_picture("assets/voronoi_diagram.png", 450000, 850000, 5200000, 3850000)

    # 3 Clear USPs (Right 42%)
    nc = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 5800000, 850000, 2894000, 3850000)
    nc.fill.solid()
    nc.fill.fore_color.rgb = BG_CARD
    nc.line.color.rgb = BORDER_CARD

    nt = s9.shapes.add_textbox(5900000, 950000, 2694000, 3650000)
    ntf = nt.text_frame
    ntf.word_wrap = True
    np = ntf.paragraphs[0]
    np.text = "WHAT MAKES OUR SYSTEM UNIQUE?"
    np.font.bold = True
    np.font.size = Pt(11.5)
    np.font.color.rgb = NAVY_PRIMARY
    np.font.name = 'Calibri'
    np.space_after = Pt(8)

    novelty_points = [
        ("1. Dynamic Voronoi Self-Healing:", "Unlike static flight paths, if Drone 2 fails (Figure B), surviving drones detect heartbeat loss (<500ms) and dynamically expand their search boundaries autonomously."),
        ("2. Routerless ESP-NOW Mesh:", "Completely eliminates the central Wi-Fi router. Drones communicate peer-to-peer at 1 Mbps with sub-millisecond latency."),
        ("3. Monolithic Extreme SWaP-C:", "Consolidates flight control, RF mesh, sensor fusion, and gate drivers on a single $10 board under 8 grams.")
    ]
    for head, body in novelty_points:
        tp = ntf.add_paragraph()
        tp.text = head
        tp.font.bold = True
        tp.font.size = Pt(10.5)
        tp.font.color.rgb = GREEN_ACCENT
        tp.font.name = 'Calibri'
        dp = ntf.add_paragraph()
        dp.text = body
        dp.font.size = Pt(9.5)
        dp.font.color.rgb = TEXT_MAIN
        dp.font.name = 'Calibri'
        dp.space_after = Pt(6)

    s9.notes_slide.notes_text_frame.text = (
        "This answers the evaluators' core question on novelty: First, dynamic self-healing via Voronoi re-tessellation. "
        "If a drone drops out, surviving drones absorb its sector without human intervention. "
        "Second, we eliminate central Wi-Fi routers entirely. Third, the monolithic $10 board eliminates heavy companion computers."
    )

    # =========================================================================
    # SLIDE 10: 8. ALIGNMENT WITH UN SDGs
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_slide_header(s10, "Alignment with UN Sustainable Development Goals (SDGs)", "8", slide_num=10)

    sdg_cards = [
        ("SDG 9: Industry, Innovation & Infrastructure",
         "Target 9.5: Domestic Technology Innovation",
         "• Lowers micro-avionics cost from $400+ to under $15 per node.\n\n"
         "• Promotes indigenous, open-hardware aerial robotics for disaster preparedness in developing nations.",
         RGBColor(245, 158, 11), RGBColor(255, 251, 235)),
        ("SDG 11: Sustainable Cities & Communities",
         "Target 11.5: Disaster Risk Reduction",
         "• Enables rapid-response survivor search in collapsed buildings and industrial hazard sites.\n\n"
         "• Maps structural voids without endangering human first responders and search canines.",
         RGBColor(234, 88, 12), RGBColor(255, 247, 237)),
        ("SDG 15: Life on Land & Forest Conservation",
         "Target 15.1: Terrestrial Forest Monitoring",
         "• Enables micro-scale autonomous scouting under dense forest canopies where GPS is blocked.\n\n"
         "• Detects early smoldering wildfire perimeters without disturbing natural wildlife habitats.",
         RGBColor(22, 163, 74), RGBColor(240, 253, 244))
    ]

    for idx, (title, target, desc, border_c, bg_c) in enumerate(sdg_cards):
        x = 500000 + idx * 2750000
        card = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, 900000, 2600000, 3750000)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_c
        card.line.color.rgb = border_c
        card.line.width = Pt(1.5)

        t = s10.shapes.add_textbox(x + 120000, 1020000, 2360000, 3500000)
        tf = t.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = border_c
        p.font.name = 'Calibri'
        p.space_after = Pt(4)

        tp2 = tf.add_paragraph()
        tp2.text = target
        tp2.font.size = Pt(10)
        tp2.font.bold = True
        tp2.font.color.rgb = TEXT_MUTED
        tp2.font.name = 'Calibri'
        tp2.space_after = Pt(10)

        bp = tf.add_paragraph()
        bp.text = desc
        bp.font.size = Pt(10.5)
        bp.font.color.rgb = TEXT_MAIN
        bp.font.name = 'Calibri'

    s10.notes_slide.notes_text_frame.text = (
        "Our project aligns directly with three United Nations SDGs: SDG 9 for indigenous robotics innovation, "
        "SDG 11 for disaster-resilient cities, and SDG 15 for under-canopy forest fire reconnaissance."
    )

    # =========================================================================
    # SLIDE 11: 9. RESEARCH TIME PLAN & MILESTONES
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_slide_header(s11, "Research Time Plan & Work Breakdown Structure", "9", slide_num=11)

    table_shape = s11.shapes.add_table(7, 5, 450000, 900000, 8244000, 3750000)
    tbl = table_shape.table
    tbl.columns[0].width = 1200000
    tbl.columns[1].width = 2500000
    tbl.columns[2].width = 1600000
    tbl.columns[3].width = 1300000
    tbl.columns[4].width = 1644000

    headers = ["Milestone", "Task Description", "Subsystem", "Timeline", "Status"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY_PRIMARY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = WHITE
        p.font.name = 'Calibri'

    gantt_data = [
        ("M1 (Phase 1)", "KiCad Schematic Design & Component Selection", "Avionics Hardware", "Weeks 1 - 3", "COMPLETED [100%]"),
        ("M2 (Phase 1)", "4-Layer PCB Routing & DRC Verification", "PCB Tape-Out", "Weeks 4 - 6", "COMPLETED [100%]"),
        ("M3 (Phase 1)", "SMT Assembly, Power Bring-up & Gate Verification", "Hardware Assembly", "Weeks 7 - 9", "COMPLETED [100%]"),
        ("M4 (Phase 1)", "250Hz Real-Time PID Loop & CRSF Protocol Parser", "Firmware (Core 0/1)", "Weeks 10 - 12", "COMPLETED [100%]"),
        ("M5 (Phase 2)", "Micro-Brushless (BLDC) & 4-in-1 DShot ESC Integration", "Propulsion Upgrade", "Weeks 13 - 16", "SCHEDULED"),
        ("M6 (Phase 2)", "ESP32-CAM Edge AI Vision & Swarm Mesh Flight Test", "Swarm Deployment", "Weeks 17 - 20", "SCHEDULED")
    ]

    for row_idx, row in enumerate(gantt_data):
        for col_idx, val in enumerate(row):
            cell = tbl.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            if "COMPLETED" in row[4]:
                cell.fill.fore_color.rgb = RGBColor(240, 253, 244) if row_idx % 2 == 0 else WHITE
            else:
                cell.fill.fore_color.rgb = BG_CARD
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(9.5)
            p.font.name = 'Calibri'
            if col_idx == 4:
                p.font.bold = True
                p.font.color.rgb = RGBColor(22, 101, 52) if "COMPLETED" in val else NAVY_PRIMARY
            else:
                p.font.color.rgb = TEXT_MAIN

    s11.notes_slide.notes_text_frame.text = (
        "Milestones 1 through 4 represent Phase 1, and all four have been 100% completed and bench-verified. "
        "Milestones 5 and 6 form our Phase 2 roadmap for the upcoming term."
    )

    # =========================================================================
    # SLIDE 12: 10. REFERENCES (High-Impact IEEE / Science)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_slide_header(s12, "Key Academic & Scientific References", "10", slide_num=12)

    rc = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 500000, 900000, 8144000, 3750000)
    rc.fill.solid()
    rc.fill.fore_color.rgb = BG_CARD
    rc.line.color.rgb = BORDER_CARD

    rt = s12.shapes.add_textbox(650000, 1000000, 7844000, 3550000)
    rtf = rt.text_frame
    rtf.word_wrap = True
    rp = rtf.paragraphs[0]
    rp.text = "FOUNDATIONAL LITERATURE CITATIONS"
    rp.font.bold = True
    rp.font.size = Pt(12)
    rp.font.color.rgb = NAVY_PRIMARY
    rp.font.name = 'Calibri'
    rp.space_after = Pt(10)

    refs = [
        "[1] J. A. Preiss, W. Hönig, G. S. Sukhatme, and N. Ayanian, 'Crazyswarm: A large nano-quadcopter swarm,' in IEEE International Conference on Robotics and Automation (ICRA), 2017, pp. 3299-3304.",
        "[2] J. Cortés, S. Martínez, T. Karatas, and F. Bullo, 'Coverage control for mobile sensing networks,' IEEE Transactions on Robotics and Automation, vol. 20, no. 2, pp. 243-255, Apr. 2004.",
        "[3] K. N. McGuire, C. De Wagter, K. Tuyls, and G. C. H. E. de Croon, 'Minimal navigation solution for a swarm of tiny flying robots to explore an unknown environment,' Science Robotics, vol. 4, no. 35, p. eaaw9710, Oct. 2019.",
        "[4] D. Palossi, A. Loquercio, F. Conti, E. Flamand, D. Scaramuzza, and L. Benini, 'A 64-mW DNN-based visual navigation engine on a 27-g autonomous quadrotor,' IEEE Internet of Things Journal, vol. 6, no. 5, pp. 8357-8371, 2019.",
        "[5] S. Hayat, E. Yanmaz, and R. Muzaffar, 'Surveying communication protocols and network architectures for multi-UAV systems,' IEEE Communications Surveys & Tutorials, vol. 18, no. 4, pp. 2614-2632, 2016."
    ]
    for r in refs:
        p = rtf.add_paragraph()
        p.text = r
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MAIN
        p.font.name = 'Calibri'
        p.space_after = Pt(8)

    s12.notes_slide.notes_text_frame.text = (
        "Our design builds upon peer-reviewed literature in IEEE ICRA, IEEE Transactions on Robotics, and Science Robotics."
    )

    # =========================================================================
    # SLIDE 13: 11. PUBLICATION STATUS & PHASE 2 ROADMAP
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_slide_header(s13, "Paper Publication Status & Phase 2 Scalability", "11", slide_num=13)

    # Left: Publication Status
    pc = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 500000, 900000, 3950000, 3750000)
    pc.fill.solid()
    pc.fill.fore_color.rgb = RGBColor(238, 242, 255)
    pc.line.color.rgb = RGBColor(129, 140, 248)
    pc.line.width = Pt(1.5)

    pt = s13.shapes.add_textbox(650000, 1000000, 3650000, 3550000)
    ptf = pt.text_frame
    ptf.word_wrap = True
    p = ptf.paragraphs[0]
    p.text = "RESEARCH PUBLICATION TRACK"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = NAVY_PRIMARY
    p.font.name = 'Calibri'
    p.space_after = Pt(10)

    pub_body = [
        ("• Manuscript Title:", "'Decentralized Heterogeneous Communication & Self-Healing Coverage for Micro-UAV Search Swarms'"),
        ("• Target Track:", "Prepared for submission to IEEE International Conference on Robotics & Automation (ICRA) / IEEE DroneCom (Scopus-Indexed Track)."),
        ("• Current Stage:", "Phase 1 hardware characterization, PID loop timing, and CRSF latency benchmarks compiled in camera-ready format."),
        ("• Open-Source Hardware:", "Complete KiCad schematics, Gerber files, and firmware repository made available for academic reproducibility.")
    ]
    for head, body in pub_body:
        tp = ptf.add_paragraph()
        tp.text = head
        tp.font.bold = True
        tp.font.size = Pt(10.5)
        tp.font.color.rgb = TEAL_ACCENT
        tp.font.name = 'Calibri'
        dp = ptf.add_paragraph()
        dp.text = body
        dp.font.size = Pt(9.5)
        dp.font.color.rgb = TEXT_MAIN
        dp.font.name = 'Calibri'
        dp.space_after = Pt(6)

    # Right: Phase 2 Upgrade
    mc = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 4694000, 900000, 3950000, 3750000)
    mc.fill.solid()
    mc.fill.fore_color.rgb = RGBColor(240, 253, 244)
    mc.line.color.rgb = RGBColor(74, 222, 128)
    mc.line.width = Pt(1.5)

    mt = s13.shapes.add_textbox(4844000, 1000000, 3650000, 3550000)
    mtf = mt.text_frame
    mtf.word_wrap = True
    p = mtf.paragraphs[0]
    p.text = "PHASE 2 UPGRADE SPECIFICATIONS"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(22, 101, 52)
    p.font.name = 'Calibri'
    p.space_after = Pt(10)

    mig_specs = [
        ("1. Brushless Propulsion (BLDC):", "0802 19,000KV brushless motors with 4-in-1 DShot300 ESCs for 4.5:1 thrust-to-weight ratio and long motor lifespan."),
        ("2. Edge Vision AI (ESP32-CAM):", "Lucas-Kanade optical flow odometry for GPS-denied position hold and lightweight CNN survivor detection."),
        ("3. Swarm Field Demonstration:", "Deploying 3 to 5 physical drones executing live ESP-NOW mesh and Voronoi self-healing in an indoor obstacle facility.")
    ]
    for head, body in mig_specs:
        tp = mtf.add_paragraph()
        tp.text = head
        tp.font.bold = True
        tp.font.size = Pt(10.5)
        tp.font.color.rgb = NAVY_PRIMARY
        tp.font.name = 'Calibri'
        dp = mtf.add_paragraph()
        dp.text = body
        dp.font.size = Pt(9.5)
        dp.font.color.rgb = TEXT_MAIN
        dp.font.name = 'Calibri'
        dp.space_after = Pt(6)

    s13.notes_slide.notes_text_frame.text = (
        "We are preparing our findings for submission to an IEEE conference track, and our Phase 2 roadmap smoothly migrates "
        "this proven avionics core to brushless motors and edge AI vision."
    )

    # =========================================================================
    # SLIDE 14: THANK YOU & DEFENSE Q&A
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)

    # Deep Navy Background
    bg14 = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, 9144000, 5143500)
    bg14.fill.solid()
    bg14.fill.fore_color.rgb = NAVY_DARK
    bg14.line.color.rgb = NAVY_DARK

    # Logos on dark background
    if os.path.exists("assets/logo_3.png"):
        s14.shapes.add_picture("assets/logo_3.png", 600000, 350000, 1400000, 1250000)
    if os.path.exists("assets/logo_4.png"):
        s14.shapes.add_picture("assets/logo_4.png", 7144000, 350000, 1400000, 1320000)

    # Center Thank You Text
    ty_box = s14.shapes.add_textbox(1000000, 1750000, 7144000, 1400000)
    tyf = ty_box.text_frame
    tyf.word_wrap = True
    tp = tyf.paragraphs[0]
    tp.text = "THANK YOU"
    tp.alignment = PP_ALIGN.CENTER
    tp.font.bold = True
    tp.font.size = Pt(42)
    tp.font.color.rgb = WHITE
    tp.font.name = 'Calibri'

    tp2 = tyf.add_paragraph()
    tp2.text = "Swarm-Based Search and Reconnaissance System (Phase 1)"
    tp2.alignment = PP_ALIGN.CENTER
    tp2.font.size = Pt(14)
    tp2.font.color.rgb = TEAL_ACCENT
    tp2.font.name = 'Calibri'

    tp3 = tyf.add_paragraph()
    tp3.text = "\nDepartment of Electronics & Communication Engineering\nSahyadri College of Engineering & Management, Mangaluru"
    tp3.alignment = PP_ALIGN.CENTER
    tp3.font.size = Pt(11)
    tp3.font.color.rgb = RGBColor(203, 213, 225)
    tp3.font.name = 'Calibri'

    # Questions Badge
    qbadge = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 3072000, 3750000, 3000000, 600000)
    qbadge.fill.solid()
    qbadge.fill.fore_color.rgb = NAVY_PRIMARY
    qbadge.line.color.rgb = TEAL_ACCENT
    qbadge.line.width = Pt(1.5)
    qp = qbadge.text_frame.paragraphs[0]
    qp.text = "QUESTIONS & DEFENSE"
    qp.alignment = PP_ALIGN.CENTER
    qp.font.bold = True
    qp.font.size = Pt(14)
    qp.font.color.rgb = WHITE
    qp.font.name = 'Calibri'

    s14.notes_slide.notes_text_frame.text = (
        "Thank you, respected evaluators and professors. We are now open for questions and technical defense."
    )

    output_path = "Swarm_Search_Reconnaissance_Presentation.pptx"
    prs.save(output_path)
    print(f"Professional presentation saved to {output_path} with {len(prs.slides)} slides.")

if __name__ == "__main__":
    create_presentation()
