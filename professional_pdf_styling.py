# query-to-pdf copy/professional_pdf_styling.py

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle, KeepTogether, Flowable
from typing import Dict, List, Any
import base64
from io import BytesIO
from PIL import Image as PILImage
from datetime import datetime
import os
import re

class PremiumReportStyling:
    """Styling system with a professional color palette and typography."""
    def __init__(self, brand_colors: Dict[str, str]):
        self.brand_colors = brand_colors
        self.styles = getSampleStyleSheet()
        self._setup_premium_colors()
        self._setup_premium_styles()
    
    def _setup_premium_colors(self):
        self.colors = {
            'primary': colors.HexColor(self.brand_colors.get("primary", "#0D203D")),
            'accent': colors.HexColor(self.brand_colors.get("accent", "#4A90E2")),
            'text': colors.HexColor("#333333"),
            'light_gray': colors.HexColor("#F4F7F9"),
            'medium_gray': colors.HexColor("#B0B0B0"),
            'dark_gray': colors.HexColor("#555555"),
            'white': colors.white,
            'gradient_start': colors.HexColor("#FFFFFF"),
            'gradient_end': colors.HexColor("#E9F2FF"),
        }

    def _setup_premium_styles(self):
        self.styles.add(ParagraphStyle(name='PremiumSectionTitle', fontName='Helvetica-Bold', fontSize=22, textColor=self.colors['primary'], spaceBefore=18, spaceAfter=10))
        self.styles.add(ParagraphStyle(name='PremiumBodyText', fontName='Helvetica', fontSize=11, leading=16, textColor=self.colors['text'], spaceAfter=8, alignment=TA_JUSTIFY))
        self.styles.add(ParagraphStyle(name='PremiumHighlightBox', fontName='Helvetica-Oblique', fontSize=11, leading=16, textColor=self.colors['primary'], borderPadding=12, borderColor=self.colors['accent'], borderWidth=0.5, backColor=self.colors['light_gray'], spaceBefore=10, spaceAfter=10))
        self.styles.add(ParagraphStyle(name='PremiumKeyInsight', fontName='Helvetica', fontSize=11, leading=16, textColor=self.colors['dark_gray'], leftIndent=18, bulletIndent=6))
        self.styles.add(ParagraphStyle(name='PremiumCaption', fontName='Helvetica-Oblique', fontSize=9, textColor=self.colors['dark_gray'], alignment=TA_CENTER, spaceAfter=16))
        self.styles.add(ParagraphStyle(name='PremiumTOCTitle', fontName='Helvetica-Bold', fontSize=22, textColor=self.colors['primary'], alignment=TA_LEFT, spaceAfter=20))
        self.styles.add(ParagraphStyle(name='TOCEntry', fontName='Helvetica', fontSize=11, leading=16, textColor=self.colors['text']))

class PremiumCanvasDrawer:
    """Handles direct drawing on the canvas for backgrounds, headers, footers, and the cover page."""
    def __init__(self, config, styling):
        self.config = config
        self.styling = styling
        self.width, self.height = A4

    def _draw_gradient_background(self, canvas):
        """Draws a subtle full-page vertical gradient using the correct ReportLab method."""
        canvas.saveState()
        start_color = self.styling.colors['gradient_start']
        end_color = self.styling.colors['gradient_end']
        canvas.linearGradient(0, self.height, 0, 0, (start_color, end_color))
        canvas.restoreState()

    def draw_cover_page(self, canvas, doc):
        """Draws the entire cover page with a gradient background."""
        self._draw_gradient_background(canvas)
        canvas.saveState()
        canvas.setFillColor(self.styling.colors['primary'])
        canvas.setFont('Helvetica-Bold', 34)
        canvas.drawCentredString(self.width / 2.0, self.height - 3.5 * inch, self.config.title)
        
        canvas.setFillColor(self.styling.colors['accent'])
        subtitle_para = Paragraph(self.config.subtitle, ParagraphStyle(name='Sub', fontSize=16, fontName='Helvetica', textColor=self.styling.colors['accent'], alignment=TA_CENTER, leading=20))
        w, h = subtitle_para.wrapOn(canvas, self.width - 2*inch, self.height)
        subtitle_para.drawOn(canvas, 1*inch, self.height - 4.2 * inch - h)

        canvas.setStrokeColor(self.styling.colors['accent'])
        canvas.setLineWidth(2)
        canvas.line(1.5*inch, self.height - 4.8*inch, self.width - 1.5*inch, self.height - 4.8*inch)
        canvas.restoreState()

    def draw_header_footer(self, canvas, doc):
        """Draws the header and footer on content pages with a gradient background."""
        if doc.page == 1: return
        self._draw_gradient_background(canvas)
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(self.styling.colors['dark_gray'])
        canvas.drawRightString(self.width - 1 * inch, 0.75 * inch, f"Page {doc.page}")
        canvas.drawString(1 * inch, 0.75 * inch, self.config.title)
        canvas.setStrokeColor(self.styling.colors['medium_gray'])
        canvas.line(1 * inch, 1 * inch, self.width - 1 * inch, 1 * inch)
        canvas.restoreState()

class PremiumPDFGenerator:
    """Generates the final PDF by assembling components."""
    def __init__(self, config, styling: PremiumReportStyling):
        self.config = config
        self.styling = styling

    def _clean_and_mark_bullets(self, text: str) -> str:
        """Cleans markdown and marks list items with a unique prefix for later styling."""
        if not text or not isinstance(text, str): return ""
        text = re.sub(r'^\s*[\*•-]\s*(.*)', r'__BULLET__\1', text, flags=re.MULTILINE)
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        return text.strip()

    def _create_flowables_from_content(self, content_str: str) -> list:
        """Converts a block of text into a list of styled Paragraph flowables."""
        flowables = []
        marked_content = self._clean_and_mark_bullets(content_str)
        paragraphs = marked_content.split('\n')
        
        for para in paragraphs:
            para = para.strip()
            if not para: continue
            
            if para.startswith('__BULLET__'):
                clean_para = para.replace('__BULLET__', '', 1)
                flowables.append(Paragraph(clean_para, self.styling.styles['PremiumKeyInsight'], bulletText='•'))
            else:
                flowables.append(Paragraph(para, self.styling.styles['PremiumBodyText']))
            flowables.append(Spacer(1, 4))
        return flowables

    def _create_premium_visualization(self, base64_data: str, caption: str) -> Flowable:
        if not base64_data: return Spacer(0, 0)
        try:
            image_data = base64.b64decode(base64_data)
            img = Image(BytesIO(image_data))
            page_width = A4[0] - (2.5 * inch)
            aspect = img.imageHeight / float(img.imageWidth)
            img.drawWidth = page_width
            img.drawHeight = page_width * aspect
            table = Table([
                [img]], 
                colWidths=[img.drawWidth + 10], 
                rowHeights=[img.drawHeight + 10],
                style=TableStyle([
                    ('BOX', (0,0), (-1,-1), 1, self.styling.colors['accent']),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ])
            )
            return KeepTogether([Spacer(1, 0.2*inch), table, Paragraph(caption, self.styling.styles['PremiumCaption'])])
        except Exception as e:
            print(f"⚠️  Error creating visualization '{caption}': {e}")
            return Spacer(0, 0)

    def generate_complete_pdf(self, content: Dict[str, Any], visualizations: Dict[str, str]) -> str:
        sanitized_title = re.sub(r'[\\/*?:"<>|]', "", self.config.title)
        filename = f"./generated_reports/{sanitized_title[:50]}.pdf"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=1*inch, leftMargin=1*inch, topMargin=1*inch, bottomMargin=1*inch)

        story = []
        story.append(PageBreak())

        # ... (Table of contents logic can be added here if desired) ...
        story.append(PageBreak())

        sections = [
            ("Executive Summary", "executive_summary", "executive_dashboard"),
            ("Research Methodology", "methodology", "methodology_visualization"),
            ("Key Findings", "key_findings", "market_growth_trends"),
            ("Detailed Market Analysis", "detailed_analysis", "customer_segmentation"),
            ("Strategic Recommendations", "recommendations", "implementation_roadmap")
        ]
        for title, content_key, viz_key in sections:
            story.append(Paragraph(title, self.styling.styles['PremiumSectionTitle']))
            section_content = content.get(content_key, {}).get('content', 'Content could not be generated.')
            story.extend(self._create_flowables_from_content(section_content))
            if visualizations and viz_key in visualizations:
                story.append(self._create_premium_visualization(visualizations[viz_key], f"{title} Visualization"))
            story.append(PageBreak())

        drawer = PremiumCanvasDrawer(self.config, self.styling)
        doc.build(story, onFirstPage=drawer.draw_cover_page, onLaterPages=drawer.draw_header_footer)
        return filename