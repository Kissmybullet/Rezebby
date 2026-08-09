import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def create_invoice_pdf(filename="Project_Invoice_LazyLady_Bot.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1E293B'),
        fontName='Helvetica-Bold',
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=15
    )

    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=8
    )

    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    cell_bold_style = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0F172A'),
        fontName='Helvetica-Bold'
    )

    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )

    elements = []

    # Title & Subtitle
    elements.append(Paragraph("PROJECT INVOICE & COST ANALYSIS", title_style))
    elements.append(Paragraph("Telegram Dual Voice Chat Music & Group Management Bot", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3B82F6'), spaceAfter=15))

    # Meta Info Table
    meta_data = [
        [
            Paragraph("<b>Project:</b> LazyLady Telegram Bot Engine", cell_style),
            Paragraph("<b>Date:</b> August 8, 2026", cell_style)
        ],
        [
            Paragraph("<b>Repository:</b> github.com/lazyindu/lazylady", cell_style),
            Paragraph("<b>Currency:</b> Indian Rupees (INR - Rs)", cell_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 250])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 15))

    # Itemized Breakdown Header
    elements.append(Paragraph("Itemized Feature Cost Breakdown", h2_style))

    # Items Data
    items = [
        [
            Paragraph("S.No", header_cell_style),
            Paragraph("Feature / Module Description", header_cell_style),
            Paragraph("Complexity", header_cell_style),
            Paragraph("Cost (Rs)", header_cell_style)
        ],
        [
            Paragraph("1", cell_bold_style),
            Paragraph("<b>PyTgCalls Voice Chat Music Engine</b><br/>• Voice Chat high-quality audio/video streaming<br/>• Queue system, /play, /skip, /pause, /resume, /stop<br/>• JioSaavn DES decryptor & SoundCloud stream engine", cell_style),
            Paragraph("High", cell_style),
            Paragraph("Rs 4,500", cell_bold_style)
        ],
        [
            Paragraph("2", cell_bold_style),
            Paragraph("<b>Spotify Full Track, Album & Playlist Engine</b><br/>• Public oEmbed & HTML Scraper fallback (100% working without API keys)<br/>• Spotify Playlist Queuing & 'Play Next Song' / /skip button logic<br/>• Exact song title audio matching fix for 1-3 letter titles", cell_style),
            Paragraph("High", cell_style),
            Paragraph("Rs 3,500", cell_bold_style)
        ],
        [
            Paragraph("3", cell_bold_style),
            Paragraph("<b>Interactive Romantic Social RP Engine (/kiss, /hug, /sex, /pat)</b><br/>• Reply-target check + Anime Request GIF + [ Accept ] button prompt<br/>• Target acceptance callback validation & random custom media response<br/>• In-memory aiohttp stream bytes fallback (Fixes Telegram 400 errors)", cell_style),
            Paragraph("High", cell_style),
            Paragraph("Rs 3,000", cell_bold_style)
        ],
        [
            Paragraph("4", cell_bold_style),
            Paragraph("<b>MongoDB Custom Image Management System</b><br/>• Custom image adding (/set_*_img) with atomic $addToSet<br/>• Admin PM media delivery (/view_*_img)<br/>• Media pull & bulk list clear commands (/remove, /removeall_*_img)", cell_style),
            Paragraph("Medium", cell_style),
            Paragraph("Rs 2,500", cell_bold_style)
        ],
        [
            Paragraph("5", cell_bold_style),
            Paragraph("<b>Auto-Database Channel File Logger</b><br/>• Played audio/video files auto-upload to Database Logger Channel (LOGGER_ID)", cell_style),
            Paragraph("Medium", cell_style),
            Paragraph("Rs 1,200", cell_bold_style)
        ],
        [
            Paragraph("6", cell_bold_style),
            Paragraph("<b>Group Management & /start UI Optimization</b><br/>• Single-message photo /start UI with live user & chat stats<br/>• Dependency bug fixes (pykeyboard -> Pyrogram native, google.py parser)", cell_style),
            Paragraph("Medium", cell_style),
            Paragraph("Rs 1,500", cell_bold_style)
        ],
        [
            Paragraph("7", cell_bold_style),
            Paragraph("<b>Cloud Deployment & Docker Setup</b><br/>• Custom Dockerfile (Python 3.10-slim + ffmpeg + libopus0)<br/>• apt.txt buildpack setup for Koyeb, Render, Railway, Heroku", cell_style),
            Paragraph("Medium", cell_style),
            Paragraph("Rs 1,800", cell_bold_style)
        ]
    ]

    item_table = Table(items, colWidths=[35, 335, 75, 75])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('ALIGN', (0,0), (-1,0), 'LEFT'),
        ('ALIGN', (3,1), (3,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 15))

    # Pricing Summary Box
    elements.append(Paragraph("Pricing & Commercial Quote Summary", h2_style))

    summary_data = [
        [
            Paragraph("<b>Basic Rate (Standard Features):</b>", cell_style),
            Paragraph("Rs 12,000 - Rs 15,000", cell_style)
        ],
        [
            Paragraph("<b>Itemized Development Total (Full Custom Build):</b>", cell_bold_style),
            Paragraph("<b>Rs 18,000</b>", cell_bold_style)
        ],
        [
            Paragraph("<b>Recommended Commercial Sale Price to Clients:</b>", cell_bold_style),
            Paragraph("<b>Rs 20,000 - Rs 25,000</b>", cell_bold_style)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[320, 200])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3B82F6')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor('#BFDBFE')),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
    ]))
    elements.append(summary_table)

    doc.build(elements)
    print("PDF Invoice created successfully:", filename)

if __name__ == "__main__":
    create_invoice_pdf()
