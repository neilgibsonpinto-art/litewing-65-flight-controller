import os
import re
import base64
import subprocess
import markdown

def img_to_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
            ext = os.path.splitext(path)[1].replace('.', '')
            return f"data:image/{ext};base64,{b64}"
    return ""

def generate_html_report():
    with open("Project_Report_Swarm_Search_Reconnaissance.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    # Load images as base64
    logo_sahyadri = img_to_base64("assets/logo_3.png")
    logo_vtu = img_to_base64("assets/logo_4.png")
    fig_arch = img_to_base64("assets/arch_diagram.png")
    fig_voronoi = img_to_base64("assets/voronoi_diagram.png")
    fig_pcb_iso = img_to_base64("assets/board_presentation_iso.png")
    fig_pcb_top = img_to_base64("assets/board_presentation_top.png")
    fig_benchmarks = img_to_base64("assets/benchmarks.png")
    fig_schematic = img_to_base64("assets/schematic_export.png")

    # Replace markdown image / mermaid blocks with figures
    # Insert visual figures directly at appropriate locations
    fig_arch_html = f'''
    <div class="figure-container">
        <img src="{fig_arch}" style="max-width: 90%; height: auto; border: 1px solid #cbd5e1; border-radius: 6px;" />
        <div class="figure-caption"><strong>Figure 3.1:</strong> Heterogeneous Dual-Tier Swarm Architecture and Dual-Core Task Allocation</div>
    </div>
    '''
    
    fig_voronoi_html = f'''
    <div class="figure-container">
        <img src="{fig_voronoi}" style="max-width: 95%; height: auto; border: 1px solid #cbd5e1; border-radius: 6px;" />
        <div class="figure-caption"><strong>Figure 3.2:</strong> Dynamic Voronoi Search Partitioning and Autonomous Self-Healing Sector Re-Tessellation</div>
    </div>
    '''

    fig_hw_html = f'''
    <div class="figure-container">
        <img src="{fig_pcb_iso}" style="max-width: 85%; height: auto; border: 1px solid #cbd5e1; border-radius: 6px; margin-bottom: 10px;" />
        <img src="{fig_pcb_top}" style="max-width: 85%; height: auto; border: 1px solid #cbd5e1; border-radius: 6px;" />
        <div class="figure-caption"><strong>Figure 4.1:</strong> Fabricated Monolithic Flight Computer (TCE_rev1) — 3D Isometric and Top Orthographic Views</div>
    </div>
    '''

    fig_bench_html = f'''
    <div class="figure-container">
        <img src="{fig_benchmarks}" style="max-width: 95%; height: auto; border: 1px solid #cbd5e1; border-radius: 6px;" />
        <div class="figure-caption"><strong>Figure 6.1:</strong> Deterministic 250 Hz Real-Time Execution Budget and Telemetry Latency Benchmarking</div>
    </div>
    '''

    # Replace mermaid blocks
    md_text = re.sub(r'```mermaid[\s\S]*?graph TD[\s\S]*?```', fig_arch_html, md_text)
    md_text = re.sub(r'```mermaid[\s\S]*?flowchart TD[\s\S]*?```', '<div class="alert-box"><strong>Implementation Roadmap:</strong> Phase 1 (Completed Avionics & Sensor Fusion) &rarr; Phase 2 (Micro-Brushless BLDC, DShot ESCs & Edge Vision Swarm).</div>', md_text)

    # Convert Markdown to HTML
    html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'nl2br'])

    # Inject Voronoi Figure into Chapter 3
    if "As demonstrated in Figure 3.2" in html_content:
        html_content = html_content.replace("As demonstrated in Figure 3.2", fig_voronoi_html + "<p>As demonstrated in Figure 3.2")
    else:
        html_content = html_content.replace("## 3.3 Novelty 2", fig_voronoi_html + "<h2>3.3 Novelty 2")

    # Inject Hardware Figure into Chapter 4
    html_content = html_content.replace("<h2>CHAPTER 4", fig_hw_html + "<h2>CHAPTER 4")

    # Inject Benchmarks Figure into Chapter 6
    html_content = html_content.replace("<h2>CHAPTER 6", fig_bench_html + "<h2>CHAPTER 6")

    # Full Styled HTML Document
    full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Swarm-Based Search and Reconnaissance System - Mini Project Report</title>
<style>
    @page {{
        size: A4 portrait;
        margin: 22mm 18mm 22mm 18mm;
        @bottom-right {{
            content: counter(page);
            font-family: 'Times New Roman', serif;
            font-size: 10pt;
            color: #64748b;
        }}
        @bottom-left {{
            content: "Dept. of ECE, SCEM | Swarm Search & Reconnaissance System";
            font-family: 'Times New Roman', serif;
            font-size: 9pt;
            color: #64748b;
        }}
    }}

    body {{
        font-family: 'Times New Roman', Times, serif;
        font-size: 11.5pt;
        line-height: 1.6;
        color: #1e293b;
        text-align: justify;
        background: #ffffff;
    }}

    h1, h2, h3, h4 {{
        font-family: 'Arial', 'Helvetica', sans-serif;
        color: #0f172a;
        page-break-after: avoid;
    }}

    h1 {{
        font-size: 18pt;
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 6px;
        margin-top: 28px;
        margin-bottom: 14px;
        color: #1e3a8a;
        text-transform: uppercase;
    }}

    h2 {{
        font-size: 14pt;
        color: #1e40af;
        border-bottom: 1px solid #cbd5e1;
        padding-bottom: 4px;
        margin-top: 22px;
        margin-bottom: 10px;
    }}

    h3 {{
        font-size: 12pt;
        color: #0d9488;
        margin-top: 16px;
        margin-bottom: 8px;
    }}

    p {{
        margin-top: 6px;
        margin-bottom: 10px;
        text-indent: 1.5em;
    }}

    .no-indent p {{
        text-indent: 0;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
        font-size: 9.5pt;
        page-break-inside: avoid;
    }}

    th, td {{
        border: 1px solid #94a3b8;
        padding: 7px 10px;
        text-align: left;
    }}

    th {{
        background-color: #1e3a8a;
        color: #ffffff;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
    }}

    tr:nth-child(even) {{
        background-color: #f8fafc;
    }}

    code {{
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 9.5pt;
        background-color: #f1f5f9;
        padding: 2px 5px;
        border-radius: 4px;
        border: 1px solid #e2e8f0;
    }}

    pre {{
        background-color: #0f172a;
        color: #f8fafc;
        padding: 12px;
        border-radius: 6px;
        font-family: 'Consolas', monospace;
        font-size: 8.5pt;
        line-height: 1.4;
        overflow-x: auto;
        page-break-inside: avoid;
        margin: 14px 0;
    }}

    pre code {{
        background: none;
        color: inherit;
        border: none;
        padding: 0;
    }}

    .cover-page {{
        text-align: center;
        page-break-after: always;
        padding-top: 10px;
    }}

    .cover-logos {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }}

    .cover-logos img {{
        height: 85px;
    }}

    .cover-title {{
        font-family: 'Arial', sans-serif;
        font-size: 21pt;
        font-weight: bold;
        color: #0f172a;
        margin: 20px 0 10px 0;
        line-height: 1.3;
    }}

    .cover-sub {{
        font-size: 13pt;
        color: #0d9488;
        font-weight: 600;
        margin-bottom: 30px;
        font-style: italic;
    }}

    .cover-box {{
        margin: 25px auto;
        padding: 15px;
        border-top: 2px solid #1e3a8a;
        border-bottom: 2px solid #1e3a8a;
        font-size: 12pt;
    }}

    .cover-team {{
        margin: 30px 0;
        font-size: 11pt;
        line-height: 1.8;
    }}

    .cover-footer {{
        margin-top: 40px;
        font-size: 11pt;
        font-weight: bold;
        color: #1e3a8a;
    }}

    .figure-container {{
        text-align: center;
        margin: 18px 0;
        page-break-inside: avoid;
    }}

    .figure-caption {{
        font-size: 9.5pt;
        color: #475569;
        margin-top: 6px;
        font-style: italic;
    }}

    .alert-box {{
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 10px 14px;
        margin: 14px 0;
        font-size: 10pt;
        border-radius: 0 4px 4px 0;
    }}

    .page-break {{
        page-break-before: always;
    }}

    hr {{
        border: 0;
        height: 1px;
        background: #cbd5e1;
        margin: 25px 0;
    }}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page no-indent">
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #1e3a8a; padding-bottom: 12px; margin-bottom: 20px;">
        <img src="{logo_sahyadri}" style="height: 90px;" />
        <div style="flex: 1; text-align: center; padding: 0 10px;">
            <div style="font-family: 'Arial', sans-serif; font-size: 13pt; font-weight: bold; color: #1e3a8a;">SAHYADRI COLLEGE OF ENGINEERING & MANAGEMENT</div>
            <div style="font-size: 9.5pt; color: #475569;">Affiliated to Visvesvaraya Technological University (VTU), Belagavi</div>
            <div style="font-family: 'Arial', sans-serif; font-size: 10.5pt; font-weight: bold; color: #0d9488; margin-top: 4px;">DEPARTMENT OF ELECTRONICS & COMMUNICATION ENGINEERING</div>
        </div>
        <img src="{logo_vtu}" style="height: 90px;" />
    </div>

    <div style="font-size: 11pt; font-weight: bold; color: #64748b; letter-spacing: 2px; margin-top: 20px;">A MINI-PROJECT REPORT ON</div>
    
    <div class="cover-title">SWARM-BASED SEARCH AND RECONNAISSANCE SYSTEM</div>
    <div class="cover-sub">Phase 1: Ultra-Low SWaP Micro-Avionics, Monolithic Flight Controller & Dual-Tier Telemetry Validation</div>

    <div class="cover-box">
        Submitted in partial fulfillment of the requirements for the award of the degree of<br/>
        <strong>BACHELOR OF ENGINEERING IN ELECTRONICS AND COMMUNICATION ENGINEERING</strong><br/>
        of Visvesvaraya Technological University, Belagavi
    </div>

    <div style="display: flex; justify-content: space-around; margin: 30px 0; text-align: left;">
        <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px 18px; width: 42%;">
            <div style="font-family: 'Arial', sans-serif; font-size: 10.5pt; font-weight: bold; color: #1e3a8a; margin-bottom: 6px;">PROJECT TEAM MEMBERS:</div>
            <div style="font-size: 10pt; line-height: 1.6;">
                <strong>Neil Gibson Pinto</strong> (4SF22EC...)<br/>
                <strong>Team Member 2</strong> (4SF22EC...)<br/>
                <strong>Team Member 3</strong> (4SF22EC...)<br/>
                <strong>Team Member 4</strong> (4SF22EC...)
            </div>
        </div>
        <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px 18px; width: 42%;">
            <div style="font-family: 'Arial', sans-serif; font-size: 10.5pt; font-weight: bold; color: #1e3a8a; margin-bottom: 6px;">UNDER THE GUIDANCE OF:</div>
            <div style="font-size: 10pt; line-height: 1.6;">
                <strong>Faculty Guide Name</strong>, M.Tech., (Ph.D.)<br/>
                <em>Assistant Professor</em><br/>
                Department of ECE, SCEM Mangaluru
            </div>
        </div>
    </div>

    <div class="cover-footer">
        SAHYADRI COLLEGE OF ENGINEERING & MANAGEMENT, MANGALURU - 575007<br/>
        <span style="font-size: 10pt; color: #64748b;">ACADEMIC YEAR: 2026 – 2027</span>
    </div>
</div>

<div class="page-break"></div>

<!-- REPORT CONTENT -->
{html_content}

</body>
</html>
'''

    with open("Project_Report_Render.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("Rendered HTML saved to Project_Report_Render.html")

def convert_html_to_pdf():
    edge_exe = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    html_abs = os.path.abspath("Project_Report_Render.html")
    pdf_out = os.path.abspath("Project_Report_Swarm_Search_Reconnaissance.pdf")

    cmd = [
        edge_exe,
        '--headless',
        '--disable-gpu',
        '--no-pdf-header-footer',
        f'--print-to-pdf={pdf_out}',
        html_abs
    ]
    print("Running Edge PDF compilation...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Edge process completed with exit code: {res.returncode}")
    if os.path.exists(pdf_out):
        size_bytes = os.path.getsize(pdf_out)
        print(f"SUCCESS: Generated {pdf_out} ({size_bytes} bytes, {size_bytes/(1024*1024):.2f} MB)")
    else:
        print("ERROR: PDF was not generated.")

if __name__ == "__main__":
    generate_html_report()
    convert_html_to_pdf()
