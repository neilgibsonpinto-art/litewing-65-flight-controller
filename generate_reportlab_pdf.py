import os
import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print 'Page X of Y' 
    and running headers across all pages (except cover & certificate).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if self._pageNumber > 2:  # Skip cover and certificate
                self.saveState()
                self.setFont("Helvetica", 8)
                self.setFillColor(colors.HexColor("#64748B"))
                # Running Header
                self.drawString(54, 842 - 36, "Dept. of ECE, SCEM | Swarm-Based Search and Reconnaissance System (Phase 1)")
                self.setStrokeColor(colors.HexColor("#CBD5E1"))
                self.setLineWidth(0.5)
                self.line(54, 842 - 40, 595 - 54, 842 - 40)
                # Running Footer
                self.line(54, 45, 595 - 54, 45)
                page_str = f"Page {self._pageNumber} of {num_pages}"
                self.drawRightString(595 - 54, 32, page_str)
                self.drawString(54, 32, "Confidential - Academic Project Report - VTU Belagavi")
                self.restoreState()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

def build_pdf():
    pdf_filename = "Project_Report_Swarm_Search_Reconnaissance.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=50,
        rightMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    NAVY = colors.HexColor("#1E3A8A")
    DARK = colors.HexColor("#0F172A")
    TEAL = colors.HexColor("#0D9488")
    TEXT = colors.HexColor("#1E293B")
    MUTED = colors.HexColor("#64748B")
    BG_LIGHT = colors.HexColor("#F8FAFC")
    BORDER = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=DARK,
        alignment=1, # Center
        spaceAfter=8
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=TEAL,
        alignment=1,
        spaceAfter=15
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=NAVY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=DARK,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    h3_style = ParagraphStyle(
        'Heading3_Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=TEAL,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=14,
        textColor=TEXT,
        alignment=4, # Justify
        spaceAfter=6
    )
    body_bold = ParagraphStyle(
        'Body_Bold',
        parent=body_style,
        fontName='Times-Bold'
    )
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        spaceAfter=3
    )
    caption_style = ParagraphStyle(
        'Caption_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        textColor=MUTED,
        alignment=1,
        spaceBefore=4,
        spaceAfter=8
    )
    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    # Header Logos
    logo_left = "assets/logo_3.png" if os.path.exists("assets/logo_3.png") else None
    logo_right = "assets/logo_4.png" if os.path.exists("assets/logo_4.png") else None

    im_l = Image(logo_left, width=1.1*inch, height=0.9*inch) if logo_left else ""
    im_r = Image(logo_right, width=1.1*inch, height=0.95*inch) if logo_right else ""

    inst_text = Paragraph(
        "<para align='center'>"
        "<b><font size=12 color='#1E3A8A'>SAHYADRI COLLEGE OF ENGINEERING & MANAGEMENT</font></b><br/>"
        "<font size=8.5 color='#64748B'>Affiliated to Visvesvaraya Technological University (VTU), Belagavi</font><br/>"
        "<b><font size=9.5 color='#0D9488'>DEPARTMENT OF ELECTRONICS & COMMUNICATION ENGINEERING</font></b>"
        "</para>",
        styles['Normal']
    )
    
    hdr_table = Table([[im_l, inst_text, im_r]], colWidths=[1.2*inch, 4.4*inch, 1.2*inch])
    hdr_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(hdr_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=NAVY, spaceAfter=20))

    story.append(Paragraph("<font size=9 color='#64748B'><b>A MINI-PROJECT REPORT ON</b></font>", ParagraphStyle('HdrSub', alignment=1, spaceAfter=12)))
    story.append(Paragraph("SWARM-BASED SEARCH AND RECONNAISSANCE SYSTEM", title_style))
    story.append(Paragraph("Phase 1: Ultra-Low SWaP Micro-Avionics, Monolithic Flight Controller & Dual-Tier Telemetry Validation", subtitle_style))

    box_p = Paragraph(
        "<para align='center'><font size=9.5 color='#1E293B'>"
        "Submitted in partial fulfillment of the requirements for the award of the degree of<br/>"
        "<b>BACHELOR OF ENGINEERING IN ELECTRONICS & COMMUNICATION ENGINEERING</b><br/>"
        "of Visvesvaraya Technological University, Belagavi"
        "</font></para>",
        styles['Normal']
    )
    box_tbl = Table([[box_p]], colWidths=[6.8*inch])
    box_tbl.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, NAVY),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(box_tbl)
    story.append(Spacer(1, 20))

    # Team & Guide Table
    team_p = Paragraph(
        "<b><font size=9.5 color='#1E3A8A'>SUBMITTED BY:</font></b><br/><br/>"
        "<b>Neil Gibson Pinto</b> (4SF22EC...)<br/>"
        "<b>Team Member 2</b> (4SF22EC...)<br/>"
        "<b>Team Member 3</b> (4SF22EC...)<br/>"
        "<b>Team Member 4</b> (4SF22EC...)",
        body_style
    )
    guide_p = Paragraph(
        "<b><font size=9.5 color='#1E3A8A'>UNDER THE GUIDANCE OF:</font></b><br/><br/>"
        "<b>Faculty Guide Name</b>, M.Tech., (Ph.D.)<br/>"
        "<i>Assistant Professor</i><br/>"
        "Department of ECE, SCEM<br/>"
        "Mangaluru - 575007",
        body_style
    )
    info_table = Table([[team_p, guide_p]], colWidths=[3.4*inch, 3.4*inch])
    info_table.setStyle(TableStyle([
        ('BOX', (0,0), (0,0), 1, BORDER),
        ('BOX', (1,0), (1,0), 1, BORDER),
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 35))

    footer_p = Paragraph(
        "<para align='center'><b><font size=9.5 color='#1E3A8A'>"
        "SAHYADRI COLLEGE OF ENGINEERING & MANAGEMENT, MANGALURU - 575007<br/>"
        "<font size=8.5 color='#64748B'>ACADEMIC YEAR: 2026 – 2027</font>"
        "</font></b></para>",
        styles['Normal']
    )
    story.append(footer_p)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: CERTIFICATE & DECLARATION
    # =========================================================================
    story.append(Paragraph("<para align='center'><b><font size=14 color='#1E3A8A'>CERTIFICATE</font></b></para>", styles['Normal']))
    story.append(HRFlowable(width="60%", thickness=1, color=TEAL, spaceBefore=4, spaceAfter=14))
    
    cert_text = (
        "This is to certify that the Mini-Project work titled <b>'SWARM-BASED SEARCH AND RECONNAISSANCE SYSTEM "
        "(Phase 1: Ultra-Low SWaP Micro-Avionics, Monolithic Flight Controller & Dual-Tier Telemetry Validation)'</b> "
        "is a bonafide work carried out by <b>Neil Gibson Pinto</b> and project team members in partial fulfillment "
        "for the award of Bachelor of Engineering in Electronics and Communication Engineering of the "
        "Visvesvaraya Technological University, Belagavi during the academic year 2026–2027. It is certified that "
        "all corrections and suggestions indicated during internal evaluations have been incorporated into this report."
    )
    story.append(Paragraph(cert_text, body_style))
    story.append(Spacer(1, 40))

    sigs = Table([
        [Paragraph("<b>____________________________</b><br/><b>Faculty Guide Name</b><br/>Assistant Professor, Dept. of ECE<br/>SCEM, Mangaluru", body_style),
         Paragraph("<b>____________________________</b><br/><b>Head of Department</b><br/>Professor & Head, Dept. of ECE<br/>SCEM, Mangaluru", body_style)]
    ], colWidths=[3.4*inch, 3.4*inch])
    sigs.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(sigs)
    story.append(Spacer(1, 30))

    story.append(Paragraph("<b>External Viva-Voce Examination:</b>", body_style))
    story.append(Spacer(1, 8))
    viva_table = Table([
        [Paragraph("<b>Name of Examiners:</b>", body_style), Paragraph("<b>Signature with Date:</b>", body_style)],
        [Paragraph("1. ____________________________________", body_style), Paragraph("________________________", body_style)],
        [Paragraph("2. ____________________________________", body_style), Paragraph("________________________", body_style)]
    ], colWidths=[4.2*inch, 2.6*inch])
    viva_table.setStyle(TableStyle([('PADDING', (0,0), (-1,-1), 4)]))
    story.append(viva_table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("<para align='center'><b><font size=12 color='#1E3A8A'>CANDIDATES' DECLARATION</font></b></para>", styles['Normal']))
    story.append(Spacer(1, 4))
    decl_text = (
        "We hereby declare that the entire project work presented herein—including custom KiCad schematics, "
        "4-layer PCB layout (TCE_rev1), deterministic 250 Hz control algorithms, ExpressLRS protocol decoders, "
        "and experimental bench characterization—has been independently executed by our team under faculty supervision. "
        "This work has not been submitted previously to any institution for any academic degree."
    )
    story.append(Paragraph(decl_text, body_style))
    story.append(Spacer(1, 15))

    decl_sigs = Table([
        [Paragraph("1. Neil Gibson Pinto", body_style), Paragraph("3. Team Member 3", body_style)],
        [Paragraph("2. Team Member 2", body_style), Paragraph("4. Team Member 4", body_style)]
    ], colWidths=[3.4*inch, 3.4*inch])
    story.append(decl_sigs)
    story.append(PageBreak())

    # =========================================================================
    # ABSTRACT
    # =========================================================================
    story.append(Paragraph("ABSTRACT", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    abs_p1 = (
        "In emergency search-and-rescue (SAR) operations following structural collapses or industrial accidents, "
        "rapid reconnaissance is paramount to locate trapped survivors within the critical 72-hour 'Golden Window'. "
        "While unmanned aerial vehicles (UAVs) provide vital aerial scouting, existing micro-UAV swarms exhibit severe "
        "engineering bottlenecks: they rely on centralized Ground Control Stations (GCS) routing inter-agent packets across "
        "standard Wi-Fi access points, creating an acute Single Point of Failure (SPOF) vulnerable to structural attenuation "
        "and packet dropouts. Furthermore, existing research platforms mount heavy companion computers (Raspberry Pi/Jetson) "
        "onto commercial flight controllers, yielding an excessive Size, Weight, Power, and Cost (SWaP-C) footprint (>150g, >$400/node) "
        "that prevents expendable multi-agent deployment."
    )
    story.append(Paragraph(abs_p1, body_style))

    abs_p2 = (
        "To resolve these fundamental challenges, this project presents an <b>indigenous, ultra-low SWaP-C decentralized "
        "micro-UAV swarm system</b> engineered for GPS-denied reconnaissance. The architecture introduces three core innovations: "
        "<b>(1) Decentralized Dual-Tier Heterogeneous Communication:</b> combining connectionless, sub-millisecond inter-agent "
        "ad-hoc meshing via <b>ESP-NOW</b> (Tier 1) for routerless flocking with deep-penetration, long-range <b>ExpressLRS (CRSF)</b> "
        "2.4 GHz / 915 MHz LoRa packet telemetry (Tier 2) for operator command and failsafe geofence broadcasts; "
        "<b>(2) Dynamic Self-Healing Voronoi Area Partitioning:</b> a distributed algorithm wherein nodes autonomously compute "
        "Voronoi spatial polygon boundaries based on neighbor state vectors, enabling surviving agents to instantly re-tessellate "
        "and absorb the abandoned sector upon any node loss (<500 ms) without ground station intervention; and "
        "<b>(3) Monolithic Ultra-Low SWaP-C Micro-Avionics (TCE_rev1):</b> a custom 65mm 4-layer PCB powered by an ESP32-S3 dual-core "
        "MCU (240 MHz). Real-time task isolation guarantees deterministic execution: Core 0 executes a 250 Hz sensor fusion "
        "and cascaded PID flight loop with 20 kHz PWM gate switching, while Core 1 executes asynchronous CRSF decoding, ESP-NOW "
        "consensus, and MAVLink telemetry."
    )
    story.append(Paragraph(abs_p2, body_style))

    abs_p3 = (
        "In this <b>Phase 1</b> implementation, the complete avionics core (TCE_rev1) was fabricated, assembled, and characterized. "
        "Bench tests demonstrated a deterministic 250.0 Hz control loop executing in 1.60 ms with 2.40 ms idle slack (60% CPU headroom), "
        "an ultra-low CRSF latency of 4.8 ms (16x faster than Wi-Fi UDP), and seamless failsafe motor cut-off within 500 ms of signal loss. "
        "This establishes the verified avionics baseline for <b>Phase 2</b>, which incorporates micro-brushless (BLDC) motors, digital "
        "DShot ESCs, and onboard optical flow edge vision."
    )
    story.append(Paragraph(abs_p3, body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================================
    story.append(Paragraph("CHAPTER 1: INTRODUCTION", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    story.append(Paragraph("1.1 Background & Operational Motivation", h2_style))
    p_intro = (
        "In the immediate aftermath of earthquakes, structural collapses, and industrial chemical disasters, first responders "
        "face catastrophic physical hazards. Entering damaged structures directly exposes human crews and search canines to secondary "
        "roof collapses, severed high-voltage lines, and toxic airborne gases. Deploying autonomous robotic scouts is vital to establish "
        "situational awareness before human entry. However, conventional commercial quadcopters (>250mm wheelbase, >500g All-Up Weight) "
        "cannot penetrate tight voids, ventilation shafts, or debris cavities. Consequently, sub-100mm nano-scale quadcopters are essential. "
        "A single micro-drone, however, suffers from limited flight endurance (5–10 min) and represents a catastrophic single point of failure. "
        "A collaborative multi-agent swarm solves this by dividing the search grid into concurrent sectors, accelerating survivor discovery "
        "while providing fault tolerance."
    )
    story.append(Paragraph(p_intro, body_style))

    story.append(Paragraph("1.2 Problem Statement & Research Gaps", h2_style))
    story.append(Paragraph(
        "Current academic and commercial drone swarms suffer from three critical bottlenecks:<br/>"
        "<b>1. Centralized Wi-Fi Dependence:</b> Platforms like Crazyswarm require a central router. In reinforced concrete ruins, "
        "Wi-Fi signals suffer severe multi-path attenuation. If the central router disconnects, the entire swarm is paralyzed.<br/>"
        "<b>2. Excessive SWaP-C:</b> Standard research drones mount companion computers (Raspberry Pi/Jetson) onto flight controllers, "
        "adding >150g in deadweight, burning >10W of compute power, and raising per-node costs above $400, preventing expendable deployment.<br/>"
        "<b>3. Absence of Self-Healing:</b> When an individual drone crashes, its assigned search lane remains uninspected unless a human "
        "operator manually detects the loss and reconfigures mission waypoints.",
        body_style
    ))

    story.append(Paragraph("1.3 Objectives & Two-Phase Implementation Strategy", h2_style))
    story.append(Paragraph(
        "To guarantee risk-managed execution and engineering rigor, this research is structured into two distinct phases:<br/>"
        "• <b>Phase 1 (Completed & Validated in this Report):</b> Monolithic custom PCB tape-out (TCE_rev1), MPU-6050 Fast I2C sensor fusion, "
        "deterministic 250 Hz dual-core PID flight control, 420,000-baud ExpressLRS CRSF protocol parser, and bench verification.<br/>"
        "• <b>Phase 2 (Upcoming Semester Roadmap):</b> Upgrading actuation to micro-brushless (BLDC) motors with 4-in-1 DShot ESCs, "
        "integrating ESP32-CAM edge vision / optical flow for indoor odometry, and deploying a physical 3-to-5 node swarm executing dynamic Voronoi self-healing.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # CHAPTER 2: LITERATURE REVIEW & COMPARATIVE ANALYSIS
    # =========================================================================
    story.append(Paragraph("CHAPTER 2: LITERATURE REVIEW & COMPARATIVE ANALYSIS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    lit_text = (
        "Multi-agent robotic exploration has advanced rapidly over the past decade. Preiss et al. (IEEE ICRA 2017) demonstrated "
        "<i>Crazyswarm</i>, hovering dozens of nano-quadcopters simultaneously. However, Crazyswarm relies strictly on an offboard ROS computer "
        "and external motion-capture cameras. Cortés et al. (IEEE TRA 2004) derived the mathematical foundations of Voronoi coverage control, "
        "yet their formulation assumes idealized communication without packet dropouts. McGuire et al. (Science Robotics 2019) demonstrated "
        "a minimal navigation solution for swarms exploring unknown environments using optical flow, but lacked long-range operator command links. "
        "Table 2.1 contrasts existing platforms against our proposed architecture."
    )
    story.append(Paragraph(lit_text, body_style))
    story.append(Spacer(1, 4))

    # Table 2.1
    comp_headers = [Paragraph("<b>Platform / Metric</b>", body_style), Paragraph("<b>Architecture</b>", body_style), Paragraph("<b>Link Topology</b>", body_style), Paragraph("<b>SWaP-C / Cost</b>", body_style), Paragraph("<b>Critical Limitation</b>", body_style)]
    comp_rows = [
        comp_headers,
        [Paragraph("Crazyswarm (Preiss 2017)", body_style), Paragraph("Centralized (ROS)", body_style), Paragraph("Central Wi-Fi / Radio", body_style), Paragraph("$220/node (Crazyflie)", body_style), Paragraph("Single point of failure; requires central mocap/router.", body_style)],
        [Paragraph("Cortés et al. (2004)", body_style), Paragraph("Voronoi Coverage", body_style), Paragraph("Idealized Omnidirectional", body_style), Paragraph("Simulation Only", body_style), Paragraph("Ignored RF packet loss, jitter, and real-time loop deadlines.", body_style)],
        [Paragraph("McGuire et al. (2019)", body_style), Paragraph("Bug Algorithm Swarm", body_style), Paragraph("Short-range IR / Beacon", body_style), Paragraph("$180/node (Custom)", body_style), Paragraph("No long-range telemetry; cannot receive operator override.", body_style)],
        [Paragraph("<b>Proposed System</b>", body_style), Paragraph("<b>Decentralized Voronoi</b>", body_style), Paragraph("<b>Tier 1: ESP-NOW<br/>Tier 2: ExpressLRS</b>", body_style), Paragraph("<b><$10/node (8g board)</b>", body_style), Paragraph("<b>Solves single-point failure; low-latency mesh + LoRa link.</b>", body_style)]
    ]
    tbl_comp = Table(comp_rows, colWidths=[1.5*inch, 1.2*inch, 1.4*inch, 1.2*inch, 1.5*inch])
    tbl_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94A3B8")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, BG_LIGHT]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#DCFCE7")), # Highlight proposed
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(tbl_comp)
    story.append(Paragraph("<b>Table 2.1:</b> Architectural comparison of state-of-the-art multi-UAV platforms vs. proposed architecture.", caption_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # CHAPTER 3: SYSTEM ARCHITECTURE & SCIENTIFIC NOVELTY
    # =========================================================================
    story.append(Paragraph("CHAPTER 3: SYSTEM ARCHITECTURE & SCIENTIFIC NOVELTY", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    story.append(Paragraph("3.1 Dual-Tier Heterogeneous Communication Paradigm", h2_style))
    p_novel1 = (
        "The primary scientific novelty of this architecture is the resolution of the classic robotics trade-off between "
        "inter-agent coordination speed and operator command penetration. We decouple communication into two distinct tiers:<br/>"
        "• <b>Tier 1 (Inter-Drone Micro-Mesh via ESP-NOW):</b> Drones communicate peer-to-peer using connectionless IEEE 802.11 "
        "vendor-specific action frames. Handshakes, association routines, and IP routing are bypassed entirely. Nodes broadcast "
        "32-byte state vectors [ID, X, Y, Z, Vx, Vy, Vbatt, Seq] at 1 Mbps with <b>sub-millisecond latency (<1.0 ms)</b>.<br/>"
        "• <b>Tier 2 (Long-Range Operator Link via ExpressLRS CRSF):</b> A high-speed full-duplex UART link running at 420,000 baud "
        "connected to Header J3. Utilizing Semtech LoRa modulation, this channel penetrates through concrete rubble, enabling the human "
        "incident commander to issue simultaneous geofence updates and emergency aborts across kilometer ranges."
    )
    story.append(Paragraph(p_novel1, body_style))

    if os.path.exists("assets/arch_diagram.png"):
        story.append(Image("assets/arch_diagram.png", width=6.6*inch, height=3.85*inch))
        story.append(Paragraph("<b>Figure 3.1:</b> Heterogeneous Dual-Tier Swarm Architecture and Dual-Core Task Allocation.", caption_style))

    story.append(Paragraph("3.2 Decentralized Dynamic Voronoi Self-Healing", h2_style))
    p_novel2 = (
        "In conventional search missions, drones execute pre-programmed raster paths. If one drone crashes, its assigned sector "
        "remains unexplored. In our system, the environment &Omega; is dynamically partitioned into Voronoi territorial polygons:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>V<sub>i</sub> = { q &isin; &Omega; | ||q - p<sub>i</sub>|| &le; ||q - p<sub>j</sub>||, &forall; j &ne; i }</b><br/>"
        "Each drone continuously calculates its sector centroid C<sub>i</sub> and navigates toward it. Surviving nodes monitor neighbor "
        "heartbeats over ESP-NOW. If an agent fails to report for more than <b>500 ms</b>, it is purged from the neighbor set. "
        "The remaining drones instantly recalculate their Voronoi polygons, dynamically expanding their search boundaries eastward "
        "and northward to cover the abandoned sector with zero human intervention."
    )
    story.append(Paragraph(p_novel2, body_style))

    if os.path.exists("assets/voronoi_diagram.png"):
        story.append(Image("assets/voronoi_diagram.png", width=6.6*inch, height=2.85*inch))
        story.append(Paragraph("<b>Figure 3.2:</b> Dynamic Voronoi Search Partitioning: (A) Healthy 4-node grid, (B) Self-healing re-tessellation upon Node 2 failure.", caption_style))

    story.append(Paragraph("3.3 Asymmetric Dual-Core Compute Task Allocation", h2_style))
    p_novel3 = (
        "Flight control on micro-quadcopters requires hard real-time determinism. A 1 ms jitter in gyro sampling destabilizes "
        "a 65mm drone. To prevent network interrupts from jittering the attitude loop, we enforce strict hardware core affinity on the ESP32-S3:<br/>"
        "• <b>Core 0 (Flight-Critical Deterministic Core):</b> Exclusively locked to 250.0 Hz execution (&Delta;t = 4.00 ms). Handles Fast I2C "
        "DMA sensor reads, 6-DOF complementary filtering, cascaded PID stabilization, and 20 kHz PWM motor mixing.<br/>"
        "• <b>Core 1 (Networking & Consensus Core):</b> Dedicated to byte-level CRSF hardware UART parsing @ 420,000 baud, CRC-8 D5 validation, "
        "ESP-NOW swarm mesh consensus, dynamic Voronoi geometry solving, and Wi-Fi MAVLink telemetry.<br/>"
        "Inter-core data exchange is mediated via a lockless double-buffered shared memory struct, preventing core stalls."
    )
    story.append(Paragraph(p_novel3, body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # CHAPTER 4: HARDWARE DESIGN (TCE_rev1)
    # =========================================================================
    story.append(Paragraph("CHAPTER 4: HARDWARE DESIGN & ELECTRICAL CHARACTERIZATION", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    p_hw = (
        "The flight computer (TCE_rev1) was custom-designed in KiCad 10 and fabricated as a 4-layer FR4 PCB. "
        "The board measures 65mm diagonal wheelbase and weighs under 8 grams bare board (AUW ~32g with battery and motors). "
        "The hardware subsystems comprise:<br/>"
        "<b>1. Power Conditioning (AP2112K-3.3):</b> Ultra-low dropout linear regulator with 600mA output capability and high PSRR (>65dB), "
        "isolating sensitive gyro rails from battery motor switching noise down to 3.55V input.<br/>"
        "<b>2. Motor Actuation Stage (AO3400A):</b> Four logic-level N-channel power MOSFETs (30V, 5.7A, R<sub>DS(on)</sub> < 30 m&Omega;). "
        "Equipped with 1N5819 Schottky flyback diodes in anti-parallel to clamp inductive kickback spikes (V = -L di/dt).<br/>"
        "<b>3. Inertial Sensing (MPU-6050):</b> 6-DOF MEMS accelerometer and gyroscope sampled via Fast-Mode I2C (400 kHz DMA) at address 0x68.<br/>"
        "<b>4. High-Speed Radio Header (Header J3):</b> 4-pin connector routing UART0 (GPIO43 TX, GPIO44 RX) directly to the external ExpressLRS receiver @ 420,000 baud."
    )
    story.append(Paragraph(p_hw, body_style))

    if os.path.exists("assets/board_presentation_iso.png"):
        story.append(Image("assets/board_presentation_iso.png", width=6.4*inch, height=2.4*inch))
        story.append(Paragraph("<b>Figure 4.1:</b> Fabricated Monolithic Flight Computer (TCE_rev1) — KiCad 3D Raytraced Isometric View.", caption_style))

    # Pinout Table
    pin_headers = [Paragraph("<b>Subsystem</b>", body_style), Paragraph("<b>Signal</b>", body_style), Paragraph("<b>ESP32-S3 Pin</b>", body_style), Paragraph("<b>Hardware Function / Electrical Spec</b>", body_style)]
    pin_rows = [
        pin_headers,
        [Paragraph("Actuation", body_style), Paragraph("M1_PWM", body_style), Paragraph("GPIO4", body_style), Paragraph("Rear-Right (CW) — AO3400A MOSFET Gate (20 kHz PWM)", body_style)],
        [Paragraph("Actuation", body_style), Paragraph("M2_PWM", body_style), Paragraph("GPIO5", body_style), Paragraph("Front-Right (CCW) — AO3400A MOSFET Gate (20 kHz PWM)", body_style)],
        [Paragraph("Actuation", body_style), Paragraph("M3_PWM", body_style), Paragraph("GPIO6", body_style), Paragraph("Rear-Left (CCW) — AO3400A MOSFET Gate (20 kHz PWM)", body_style)],
        [Paragraph("Actuation", body_style), Paragraph("M4_PWM", body_style), Paragraph("GPIO7", body_style), Paragraph("Front-Left (CW) — AO3400A MOSFET Gate (20 kHz PWM)", body_style)],
        [Paragraph("IMU Sensing", body_style), Paragraph("I2C_SDA", body_style), Paragraph("GPIO8", body_style), Paragraph("Fast I2C Data Line (400 kHz DMA) with 2.2k pull-up", body_style)],
        [Paragraph("IMU Sensing", body_style), Paragraph("I2C_SCL", body_style), Paragraph("GPIO9", body_style), Paragraph("Fast I2C Clock Line (400 kHz DMA) with 2.2k pull-up", body_style)],
        [Paragraph("Radio Link", body_style), Paragraph("ESP_TXD0", body_style), Paragraph("GPIO43", body_style), Paragraph("UART0 TX &rarr; ExpressLRS Receiver J3 (Pin 2) @ 420kbaud", body_style)],
        [Paragraph("Radio Link", body_style), Paragraph("ESP_RXD0", body_style), Paragraph("GPIO44", body_style), Paragraph("UART0 RX &larr; ExpressLRS Receiver J3 (Pin 3) @ 420kbaud", body_style)],
        [Paragraph("Signaling", body_style), Paragraph("BASE_RGB", body_style), Paragraph("GPIO2", body_style), Paragraph("WS2812B Smart RGB LED (Status, Armed, Failsafe)", body_style)],
        [Paragraph("Signaling", body_style), Paragraph("STATUS_LED", body_style), Paragraph("GPIO3", body_style), Paragraph("Blue System Heartbeat Indicator LED", body_style)],
        [Paragraph("Signaling", body_style), Paragraph("ARM_LIGHTS", body_style), Paragraph("GPIO47", body_style), Paragraph("High-Intensity Arming Marker Corner LEDs", body_style)],
        [Paragraph("Audio", body_style), Paragraph("BUZZER", body_style), Paragraph("GPIO48", body_style), Paragraph("Low-Battery Warning Active Buzzer", body_style)],
    ]
    tbl_pin = Table(pin_rows, colWidths=[1.1*inch, 1.1*inch, 1.1*inch, 3.5*inch])
    tbl_pin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('PADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(tbl_pin)
    story.append(Paragraph("<b>Table 4.1:</b> Hardware pin mapping and electrical specifications of the TCE_rev1 flight controller.", caption_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # CHAPTER 5: FIRMWARE ARCHITECTURE & CONTROL THEORY
    # =========================================================================
    story.append(Paragraph("CHAPTER 5: FIRMWARE ARCHITECTURE & CONTROL THEORY", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    p_firmware = (
        "<b>5.1 6-DOF Complementary Attitude Estimation:</b><br/>"
        "To decouple gyro integration drift from accelerometer vibration noise, a non-linear complementary filter is used:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>&theta;(t) = &alpha; &middot; [&theta;(t - &Delta;t) + &omega;<sub>y</sub> &middot; &Delta;t] + (1 - &alpha;) &middot; &theta;<sub>acc</sub></b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>&phi;(t) = &alpha; &middot; [&phi;(t - &Delta;t) + &omega;<sub>x</sub> &middot; &Delta;t] + (1 - &alpha;) &middot; &phi;<sub>acc</sub></b><br/>"
        "with filter weighting &alpha; = 0.985 at 250 Hz, rejecting high-frequency motor vibration harmonics while eliminating long-term angle drift.<br/><br/>"
        "<b>5.2 Dual-Stage Cascaded PID Flight Control Law:</b><br/>"
        "Attitude control is executed in two stages: an outer proportional angle loop computes desired body angular rates from RC setpoints, "
        "and an inner PID rate loop computes motor torque stabilization commands:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>u(t) = K<sub>p</sub> &middot; e<sub>rate</sub>(t) + K<sub>i</sub> &int; e<sub>rate</sub>(&tau;) d&tau; + K<sub>d</sub> &middot; (de<sub>rate</sub> / dt)</b><br/>"
        "Dynamic anti-windup clamps the integrator, and total stabilization authority is dynamically constrained to &le;25% of base throttle "
        "to prevent motor saturation.<br/><br/>"
        "<b>5.3 CRSF Protocol Decoding & CRC-8 D5 Engine:</b><br/>"
        "Incoming packets from ExpressLRS follow the CRSF frame standard: <code>[Sync 0xC8] [Len] [Type 0x16] [22-Byte Payload] [CRC-8]</code>. "
        "The firmware computes the hardware CRC-8 with polynomial <code>0xD5</code> across the payload. If valid, 16 packed channels (11-bit each: "
        "172 to 1811) are mapped to 1000–2000 &mu;s. If packets cease for >500 ms, failsafe immediately disarms motors and sets RGB LED to RED."
    )
    story.append(Paragraph(p_firmware, body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # CHAPTER 6: EXPERIMENTAL RESULTS (PHASE 1)
    # =========================================================================
    story.append(Paragraph("CHAPTER 6: EXPERIMENTAL RESULTS & BENCHMARKING (PHASE 1)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    p_results = (
        "<b>6.1 Real-Time Execution Budget Profiling:</b><br/>"
        "Execution time across the 250.0 Hz control loop was profiled with hardware microsecond counters:<br/>"
        "• Fast I2C DMA Sensor Read (MPU-6050): 0.95 ms<br/>"
        "• Attitude Complementary Filter: 0.35 ms<br/>"
        "• Cascaded Angle/Rate PID Computation: 0.25 ms<br/>"
        "• LEDC 20 kHz PWM Register Output: 0.05 ms<br/>"
        "• <b>Total Active Compute: 1.60 ms</b> out of <b>4.00 ms deadline</b> &rarr; <b>2.40 ms idle slack (60.0% CPU headroom)</b>.<br/><br/>"
        "<b>6.2 Telemetry Latency Benchmarking:</b><br/>"
        "ExpressLRS CRSF clocked an average latency of <b>4.8 ms &plusmn; 0.6 ms</b>, achieving a <b>16x latency reduction</b> compared to "
        "standard Wi-Fi UDP (78.5 ms &plusmn; 25 ms), eliminating control lag.<br/><br/>"
        "<b>6.3 Power Sag Root-Cause Analysis:</b><br/>"
        "During high-throttle bench testing, the board experienced brownout resets at 84% throttle when connected via computer USB. "
        "Oscilloscope characterization revealed that four brushed motors at 84% throttle demand 3.8A of surge current, tripping the host PC "
        "USB polyfuse (capped at 500mA). Connecting a dedicated 1S 300mAh LiPo battery (30C rating = 9.0A capability) maintained complete "
        "voltage stability, allowing sustained 100% full-throttle operation with zero voltage droop on the 3.3V regulated rail."
    )
    story.append(Paragraph(p_results, body_style))

    if os.path.exists("assets/benchmarks.png"):
        story.append(Image("assets/benchmarks.png", width=6.6*inch, height=2.6*inch))
        story.append(Paragraph("<b>Figure 6.1:</b> Core 0 Real-Time Execution Budget and Telemetry Link Latency Benchmarking.", caption_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # CHAPTER 7: PHASE 2 ROADMAP
    # =========================================================================
    story.append(Paragraph("CHAPTER 7: PHASE 2 ROADMAP (BRUSHLESS & EDGE AI VISION)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    p_phase2 = (
        "With the core avionics and telemetry verified in Phase 1, the platform scales into Phase 2 for full multi-agent swarm deployment:<br/>"
        "<b>1. Micro-Brushless Propulsion (BLDC):</b> Transitioning from 716 coreless brushed motors to 0802 / 1102 (19,000 KV) outrunner "
        "brushless motors driven by 4-in-1 digital <b>DShot300</b> ESCs. Brushless actuation increases thrust-to-weight ratio to 4.5:1 and "
        "eliminates mechanical brush wear.<br/>"
        "<b>2. Edge Vision AI (ESP32-CAM):</b> Integrating an auxiliary ESP32-CAM module running Lucas-Kanade optical flow odometry for drift-free "
        "indoor hover in GPS-denied buildings, along with a quantized neural model for survivor thermal blob detection.<br/>"
        "<b>3. Multi-Node Swarm Field Test:</b> Deploying 3 to 5 physical drones running live ESP-NOW mesh to demonstrate real-time dynamic Voronoi "
        "boundary re-tessellation in an enclosed test facility."
    )
    story.append(Paragraph(p_phase2, body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # CHAPTER 8: CONCLUSION & UN SDGS
    # =========================================================================
    story.append(Paragraph("CHAPTER 8: CONCLUSION & ALIGNMENT WITH UN SDGs", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    p_conclusion = (
        "This project successfully developed and validated Phase 1 of an ultra-low SWaP-C Swarm-Based Search and Reconnaissance System. "
        "By replacing brittle, centralized Wi-Fi swarms with a dual-tier heterogeneous communication architecture (ESP-NOW mesh + ExpressLRS CRSF), "
        "the design achieves routerless, fault-tolerant operation in GPS-denied environments. The monolithic TCE_rev1 flight controller board "
        "demonstrated deterministic 250 Hz flight control, 60% CPU headroom, and sub-5ms radio responsiveness on a single sub-$10 PCB.<br/><br/>"
        "<b>Alignment with UN Sustainable Development Goals (SDGs):</b><br/>"
        "• <b>SDG 9 (Industry, Innovation & Infrastructure - Target 9.5):</b> Fosters indigenous robotics and open-hardware avionics, lowering "
        "micro-drone entry costs from $400+ to under $15 per node.<br/>"
        "• <b>SDG 11 (Sustainable Cities & Communities - Target 11.5):</b> Reduces disaster fatalities by enabling rapid structural scouting and "
        "survivor localization in collapsed urban ruins without endangering first responders.<br/>"
        "• <b>SDG 15 (Life on Land - Target 15.1):</b> Enables non-intrusive micro-drone scouting under dense forest canopies for early wildfire "
        "perimeter mapping where GPS and large drones cannot operate."
    )
    story.append(Paragraph(p_conclusion, body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # REFERENCES
    # =========================================================================
    story.append(Paragraph("REFERENCES", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    ref_list = [
        "[1] J. A. Preiss, W. Hönig, G. S. Sukhatme, and N. Ayanian, 'Crazyswarm: A large nano-quadcopter swarm,' in <i>IEEE International Conference on Robotics and Automation (ICRA)</i>, 2017, pp. 3299-3304.",
        "[2] J. Cortés, S. Martínez, T. Karatas, and F. Bullo, 'Coverage control for mobile sensing networks,' <i>IEEE Transactions on Robotics and Automation</i>, vol. 20, no. 2, pp. 243-255, Apr. 2004.",
        "[3] K. N. McGuire, C. De Wagter, K. Tuyls, and G. C. H. E. de Croon, 'Minimal navigation solution for a swarm of tiny flying robots to explore an unknown environment,' <i>Science Robotics</i>, vol. 4, no. 35, p. eaaw9710, Oct. 2019.",
        "[4] D. Palossi, A. Loquercio, F. Conti, E. Flamand, D. Scaramuzza, and L. Benini, 'A 64-mW DNN-based visual navigation engine on a 27-g autonomous quadrotor,' <i>IEEE Internet of Things Journal</i>, vol. 6, no. 5, pp. 8357-8371, Oct. 2019.",
        "[5] S. Hayat, E. Yanmaz, and R. Muzaffar, 'Surveying communication protocols and network architectures for multi-UAV systems,' <i>IEEE Communications Surveys & Tutorials</i>, vol. 18, no. 4, pp. 2614-2632, 2016.",
        "[6] D. Albani, T. Manoni, A. Arik, and D. Nardi, 'Field-deployable, resilient, distributed swarm of micro-UAVs for search and rescue operations,' in <i>IEEE International Symposium on Safety, Security, and Rescue Robotics (SSRR)</i>, 2020.",
        "[7] R. Mahony, T. Hamel, and J.-M. Pflimlin, 'Nonlinear complementary filters on the special orthogonal group,' <i>IEEE Transactions on Automatic Control</i>, vol. 53, no. 5, pp. 1203-1218, Jun. 2008.",
        "[8] M. Schwager, D. Rus, and J.-J. Slotine, 'Decentralized, adaptive coverage for networked robots,' <i>The International Journal of Robotics Research</i>, vol. 28, no. 3, pp. 357-375, Mar. 2009."
    ]
    for r in ref_list:
        story.append(Paragraph(r, ParagraphStyle('RefStyle', parent=body_style, fontSize=8.5, leading=11, spaceAfter=4)))

    # Build Document with dynamic two-pass canvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"ReportLab PDF generation complete: {pdf_filename}")

if __name__ == "__main__":
    build_pdf()
