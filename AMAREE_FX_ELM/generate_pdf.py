#!/usr/bin/env python3
"""
AMAREE FX ELM PDF Generator
Creates a professional PDF document from the master text file
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

# Configuration
INPUT_TXT = "AMAREE_FX_ELM_MASTER.txt"
OUTPUT_PDF = "AMAREE_FX_ELM_MASTER.pdf"
PAGESIZE = A4

# Custom colors
GOLD = colors.Color(0.85, 0.65, 0.13, 1)  # Gold color
DARK_BLUE = colors.Color(0.1, 0.2, 0.4, 1)
MEDIUM_BLUE = colors.Color(0.2, 0.3, 0.5, 1)
LIGHT_GRAY = colors.Color(0.9, 0.9, 0.9, 1)

# Custom styles
styles = getSampleStyleSheet()

# Title style
TitleStyle = ParagraphStyle(
    name='Title',
    parent=styles['Heading1'],
    fontSize=24,
    leading=28,
    textColor=GOLD,
    spaceAfter=20,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

# Subtitle style
SubtitleStyle = ParagraphStyle(
    name='Subtitle',
    parent=styles['Heading2'],
    fontSize=14,
    leading=18,
    textColor=colors.white,
    spaceAfter=20,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

# Heading styles
H1Style = ParagraphStyle(
    name='H1',
    parent=styles['Heading1'],
    fontSize=18,
    leading=22,
    textColor=DARK_BLUE,
    spaceBefore=24,
    spaceAfter=12,
    alignment=TA_LEFT,
    fontName='Helvetica-Bold'
)

H2Style = ParagraphStyle(
    name='H2',
    parent=styles['Heading2'],
    fontSize=14,
    leading=18,
    textColor=DARK_BLUE,
    spaceBefore=18,
    spaceAfter=8,
    alignment=TA_LEFT,
    fontName='Helvetica-Bold'
)

H3Style = ParagraphStyle(
    name='H3',
    parent=styles['Heading3'],
    fontSize=12,
    leading=15,
    textColor=MEDIUM_BLUE,
    spaceBefore=12,
    spaceAfter=6,
    alignment=TA_LEFT,
    fontName='Helvetica-Bold'
)

# Body text styles
BodyStyle = ParagraphStyle(
    name='Body',
    parent=styles['Normal'],
    fontSize=10,
    leading=13,
    textColor=colors.black,
    spaceAfter=6,
    alignment=TA_LEFT,
    fontName='Helvetica'
)

BodyBold = ParagraphStyle(
    name='BodyBold',
    parent=BodyStyle,
    fontName='Helvetica-Bold'
)

# Code/monospace style
CodeStyle = ParagraphStyle(
    name='Code',
    parent=styles['Code'],
    fontSize=9,
    leading=11,
    textColor=colors.Color(0.2, 0.2, 0.6, 1),
    spaceAfter=6,
    alignment=TA_LEFT,
    fontName='Courier'
)

# Table styles
TableHeaderStyle = ParagraphStyle(
    name='TableHeader',
    parent=styles['Normal'],
    fontSize=9,
    leading=11,
    textColor=colors.white,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

TableCellStyle = ParagraphStyle(
    name='TableCell',
    parent=styles['Normal'],
    fontSize=8,
    leading=10,
    textColor=colors.black,
    alignment=TA_LEFT,
    fontName='Helvetica'
)


def parse_text_file(filepath):
    """Parse the text file into structured sections"""
    sections = []
    current_section = None
    current_subsection = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Check for main document separator
        if line.startswith('=' * 80) or line.startswith('=' * 70):
            continue
            
        # Title line
        if 'AMAREE FX ACADEMY' in line and 'ECCENTRIC LIQUIDATION' in line:
            if current_section:
                sections.append(current_section)
            current_section = {
                'type': 'title',
                'content': line
            }
            sections.append(current_section)
            current_section = None
            continue
        
        # Core principle
        if 'Core Principle:' in line:
            if current_section:
                sections.append(current_section)
            current_section = {
                'type': 'principle',
                'content': line
            }
            sections.append(current_section)
            current_section = None
            continue
        
        # Part headers (PART A, PART B, etc.)
        if line.startswith('PART ') and ':' in line:
            if current_section:
                sections.append(current_section)
            part_info = line.split(':')
            part_name = part_info[0].strip()
            part_title = part_info[1].strip() if len(part_info) > 1 else ""
            current_section = {
                'type': 'part',
                'name': part_name,
                'title': part_title,
                'content': []
            }
            continue
        
        # Section headers (A1, A2, etc.)
        if line.startswith('A') and '.' in line and line[1].isdigit():
            if current_section and current_section['type'] == 'part':
                current_subsection = {
                    'type': 'section',
                    'name': line.split(' ')[0],
                    'title': line.split(' ', 1)[1] if ' ' in line else line,
                    'content': []
                }
                current_section['content'].append(current_subsection)
            continue
        
        # Sub-subsection headers (like C1, C2, etc.)
        if line and line[0].isupper() and line[1].isdigit() and '.' in line:
            if current_subsection:
                sub_sub = {
                    'type': 'subsection',
                    'name': line.split(' ')[0],
                    'title': line.split(' ', 1)[1] if ' ' in line else line,
                    'content': []
                }
                current_subsection['content'].append(sub_sub)
            continue
        
        # Regular content
        if current_subsection:
            current_subsection['content'].append(line)
        elif current_section and current_section['type'] == 'part':
            if 'content' in current_section:
                if isinstance(current_section['content'], list):
                    current_section['content'].append(line)
                else:
                    current_section['content'] = [current_section['content'], line]
            else:
                current_section['content'] = line
    
    if current_section:
        sections.append(current_section)
    
    return sections


def create_pdf():
    """Create the PDF document"""
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=PAGESIZE,
        leftMargin=25*mm,
        rightMargin=25*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    story = []
    
    # Parse the text file
    sections = parse_text_file(INPUT_TXT)
    
    # Add title page
    add_title_page(story)
    
    # Add document header
    story.append(PageBreak())
    add_header(story)
    
    # Process sections
    for section in sections:
        if section['type'] == 'title':
            story.append(Spacer(1, 12))
            story.append(Paragraph(section['content'], TitleStyle))
        elif section['type'] == 'principle':
            story.append(Spacer(1, 6))
            story.append(Paragraph(section['content'], SubtitleStyle))
            story.append(Spacer(1, 24))
        elif section['type'] == 'part':
            # Part title
            story.append(PageBreak())
            story.append(Paragraph(f"{section['name']}: {section['title']}", H1Style))
            story.append(Spacer(1, 6))
            
            # Process part content
            if isinstance(section['content'], list):
                for item in section['content']:
                    if isinstance(item, dict):
                        if item['type'] == 'section':
                            # Section header
                            story.append(Paragraph(f"{item['name']}. {item['title']}", H2Style))
                            story.append(Spacer(1, 4))
                            
                            # Section content
                            if isinstance(item['content'], list):
                                for content_item in item['content']:
                                    if isinstance(content_item, dict):
                                        if content_item['type'] == 'subsection':
                                            story.append(Paragraph(f"{content_item['name']}. {content_item['title']}", H3Style))
                                            story.append(Spacer(1, 2))
                                            
                                            # Subsection content
                                            for text in content_item['content']:
                                                story.append(Paragraph(text, BodyStyle))
                                        else:
                                            story.append(Paragraph(content_item, BodyStyle))
                                    else:
                                        story.append(Paragraph(content_item, BodyStyle))
                            else:
                                story.append(Paragraph(item['content'], BodyStyle))
                        else:
                            story.append(Paragraph(str(item), BodyStyle))
                    else:
                        story.append(Paragraph(item, BodyStyle))
            else:
                story.append(Paragraph(section['content'], BodyStyle))
    
    # Add footer
    story.append(Spacer(1, 24))
    story.append(Paragraph("This is a proprietary trading framework. For educational purposes only.", 
                          ParagraphStyle(name='Footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
    
    # Build the PDF
    doc.build(story)
    print(f"PDF generated: {OUTPUT_PDF}")


def add_title_page(story):
    """Add the title page to the document"""
    # Background rectangle for title page
    # This is a simple approach - for better results, we'd need a custom canvas
    
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("AMAREE FX ACADEMY", 
                          ParagraphStyle(name='MainTitle', fontSize=32, leading=38, 
                                        textColor=GOLD, alignment=TA_CENTER, 
                                        fontName='Helvetica-Bold', spaceAfter=16)))
    
    story.append(Paragraph("ECCENTRIC LIQUIDATION MODEL (ELM)", 
                          ParagraphStyle(name='SubTitle', fontSize=24, leading=28,
                                        textColor=colors.white, alignment=TA_CENTER,
                                        fontName='Helvetica-Bold', spaceAfter=8)))
    
    story.append(Paragraph("Multi-Timeframe AI Analysis & Execution Framework", 
                          ParagraphStyle(name='FrameTitle', fontSize=16, leading=20,
                                        textColor=colors.Color(0.9, 0.9, 0.9, 1), alignment=TA_CENTER,
                                        fontName='Helvetica', spaceAfter=40)))
    
    story.append(Paragraph("Core Principle:", 
                          ParagraphStyle(name='PrincipleLabel', fontSize=14, leading=18,
                                        textColor=GOLD, alignment=TA_CENTER,
                                        fontName='Helvetica-Bold', spaceAfter=8)))
    
    story.append(Paragraph("PRECISION IN EXECUTION. PATIENCE IN PRICE ACTION.", 
                          ParagraphStyle(name='PrincipleText', fontSize=14, leading=18,
                                        textColor=colors.white, alignment=TA_CENTER,
                                        fontName='Helvetica-Bold', spaceAfter=40)))
    
    story.append(Paragraph("Version 1.0.0", 
                          ParagraphStyle(name='Version', fontSize=12, leading=16,
                                        textColor=colors.Color(0.8, 0.8, 0.8, 1), alignment=TA_CENTER,
                                        fontName='Helvetica')))
    
    story.append(Spacer(1, 3*inch))
    
    # Add document info table
    info_data = [
        ["Classification", "PROPRIETARY STRATEGY FRAMEWORK"],
        ["Author", "AMAREE FX ACADEMY"],
        ["Target Audience", "Professional Traders & AI Analysts"],
        ["Document Type", "Technical Specification & Training Manual"]
    ]
    
    info_table = Table(info_data, colWidths=[100*mm, 100*mm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_GRAY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.7, 0.7, 0.7, 1))
    ]))
    
    story.append(info_table)


def add_header(story):
    """Add the document header"""
    story.append(Paragraph("AMAREE FX ACADEMY", 
                          ParagraphStyle(name='Header', fontSize=14, leading=18,
                                        textColor=DARK_BLUE, alignment=TA_LEFT,
                                        fontName='Helvetica-Bold', spaceAfter=4)))
    story.append(Paragraph("ECCENTRIC LIQUIDATION MODEL (ELM)", 
                          ParagraphStyle(name='Header2', fontSize=12, leading=15,
                                        textColor=MEDIUM_BLUE, alignment=TA_LEFT,
                                        fontName='Helvetica-Bold', spaceAfter=12)))
    story.append(Paragraph("Multi-Timeframe AI Analysis & Execution Framework", 
                          ParagraphStyle(name='Header3', fontSize=10, leading=13,
                                        textColor=colors.grey, alignment=TA_LEFT,
                                        fontName='Helvetica', spaceAfter=20)))


if __name__ == "__main__":
    # Check if input file exists
    if not os.path.exists(INPUT_TXT):
        print(f"Error: Input file {INPUT_TXT} not found")
        exit(1)
    
    create_pdf()
