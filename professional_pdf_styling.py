from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import inch, cm, mm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle, KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle
from reportlab.graphics import renderPDF
from reportlab.platypus.flowables import Flowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from typing import Dict, List, Any
import base64
from io import BytesIO
from PIL import Image as PILImage
from datetime import datetime
import os
import re

class PremiumHeaderFooter:
    """Enhanced premium header and footer system"""
    
    def __init__(self, doc, config, styling):
        self.doc = doc
        self.config = config
        self.styling = styling
        
    def on_first_page(self, canvas, doc):
        """Clean first page - no header/footer on cover"""
        pass
        
    def on_later_pages(self, canvas, doc):
        """Premium header and footer for content pages"""
        canvas.saveState()
        
        # Premium header with gradient effect
        canvas.setFont('Helvetica-Bold', 9)
        canvas.setFillColor(self.styling.colors['primary'])
        canvas.drawString(2.5*cm, A4[1] - 2*cm, self.config.title[:50] + "..." if len(self.config.title) > 50 else self.config.title)
        
        # Date on right
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(self.styling.colors['dark_gray'])
        canvas.drawRightString(A4[0] - 2.5*cm, A4[1] - 2*cm, datetime.now().strftime('%B %Y'))
        
        # Premium header line with gradient effect
        canvas.setStrokeColor(self.styling.colors['accent'])
        canvas.setLineWidth(2)
        canvas.line(2.5*cm, A4[1] - 2.3*cm, A4[0] - 2.5*cm, A4[1] - 2.3*cm)
        
        # Secondary accent line
        canvas.setStrokeColor(self.styling.colors['primary'])
        canvas.setLineWidth(0.5)
        canvas.line(2.5*cm, A4[1] - 2.4*cm, A4[0] - 2.5*cm, A4[1] - 2.4*cm)
        
        # Premium footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(self.styling.colors['medium_gray'])
        canvas.drawString(2.5*cm, 2*cm, f"{self.config.company}")
        canvas.drawCentredText(A4[0]/2, 2*cm, "CONFIDENTIAL & PROPRIETARY")
        canvas.drawRightString(A4[0] - 2.5*cm, 2*cm, f"Page {doc.page}")
        
        # Premium footer line
        canvas.setStrokeColor(self.styling.colors['accent'])
        canvas.setLineWidth(1)
        canvas.line(2.5*cm, 2.3*cm, A4[0] - 2.5*cm, 2.3*cm)
        
        canvas.restoreState()

class PremiumCoverPage:
    """Ultra-premium cover page design"""
    
    def __init__(self, config, styling):
        self.config = config
        self.styling = styling
        
    def create_cover_elements(self, cover_image: str = None) -> List:
        """Create ultra-premium professional cover page"""
        elements = []
        
        # Top premium spacing
        elements.append(Spacer(1, 1.2*inch))
        
        # Premium company branding
        if self.config.logo_path and os.path.exists(self.config.logo_path):
            try:
                logo = Image(self.config.logo_path, width=3*inch, height=1.5*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 0.4*inch))
            except Exception:
                pass
        
        # Ultra-premium title with enhanced typography
        title_style = ParagraphStyle(
            name='PremiumCoverTitle',
            fontSize=36,
            leading=42,
            alignment=TA_CENTER,
            textColor=self.styling.colors['primary'],
            fontName='Helvetica-Bold',
            spaceAfter=0.3*inch,
            spaceBefore=0.2*inch
        )
        elements.append(Paragraph(self.config.title, title_style))
        
        # Premium subtitle with accent
        subtitle_style = ParagraphStyle(
            name='PremiumCoverSubtitle',
            fontSize=18,
            leading=24,
            alignment=TA_CENTER,
            textColor=self.styling.colors['accent'],
            fontName='Helvetica',
            spaceAfter=0.4*inch
        )
        elements.append(Paragraph(self.config.subtitle, subtitle_style))
        
        # Premium divider with gradient effect
        divider = Drawing(6*inch, 12)
        divider.add(Line(0, 6, 6*inch, 6, strokeColor=self.styling.colors['accent'], strokeWidth=4))
        divider.add(Line(0.5*inch, 3, 5.5*inch, 3, strokeColor=self.styling.colors['primary'], strokeWidth=2))
        divider.hAlign = 'CENTER'
        elements.append(divider)
        elements.append(Spacer(1, 0.5*inch))
        
        # Premium cover image - optimized size
        if cover_image:
            try:
                cover_img = self._create_premium_cover_image(cover_image)
                elements.append(cover_img)
                elements.append(Spacer(1, 0.3*inch))
            except Exception:
                pass
        
        # Ultra-premium metadata table
        metadata_table = self._create_premium_metadata_table()
        elements.append(metadata_table)
        
        # Premium spacing
        elements.append(Spacer(1, 0.6*inch))
        
        # Premium footer with enhanced design
        footer_info = self._create_premium_footer()
        elements.append(footer_info)
        
        return elements
    
    def _create_premium_cover_image(self, base64_string: str):
        """Create premium sized cover image"""
        try:
            image_data = base64.b64decode(base64_string)
            image_buffer = BytesIO(image_data)
            img = Image(image_buffer, width=5.5*inch, height=3.8*inch)
            img.hAlign = 'CENTER'
            
            # Add border effect
            border_drawing = Drawing(5.8*inch, 4.1*inch)
            border_drawing.add(Rect(0.15*inch, 0.15*inch, 5.5*inch, 3.8*inch,
                                   fillColor=None,
                                   strokeColor=self.styling.colors['accent'],
                                   strokeWidth=2))
            border_drawing.hAlign = 'CENTER'
            
            return KeepTogether([border_drawing, img])
        except:
            return self._create_premium_placeholder()
    
    def _create_premium_placeholder(self):
        """Create premium placeholder if image fails"""
        placeholder = Drawing(5.5*inch, 3.8*inch)
        placeholder.add(Rect(0, 0, 5.5*inch, 3.8*inch,
                            fillColor=self.styling.colors['light_gray'],
                            strokeColor=self.styling.colors['accent'],
                            strokeWidth=3))
        placeholder.hAlign = 'CENTER'
        return placeholder
    
    def _create_premium_metadata_table(self):
        """Create ultra-premium metadata table"""
        current_date = datetime.now().strftime('%B %d, %Y')
        report_type = self.config.report_type.value.replace('_', ' ').title()
        
        metadata_data = [
            ['PREPARED BY', self.config.author],
            ['ORGANIZATION', self.config.company],
            ['REPORT DATE', current_date],
            ['ANALYSIS TYPE', report_type],
            ['TARGET AUDIENCE', getattr(self.config, 'target_audience', 'Executive Leadership')],
            ['CLASSIFICATION', 'CONFIDENTIAL'],
            ['VERSION', '1.0']
        ]
        
        table = Table(metadata_data, colWidths=[2.2*inch, 3.2*inch])
        table.setStyle(TableStyle([
            # Header styling
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), self.styling.colors['primary']),
            ('TEXTCOLOR', (1, 0), (1, -1), self.styling.colors['secondary']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Premium spacing
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            
            # Premium borders
            ('LINEABOVE', (0, 0), (-1, 0), 2, self.styling.colors['accent']),
            ('LINEBELOW', (0, -1), (-1, -1), 2, self.styling.colors['accent']),
            ('LINEBELOW', (0, 2), (-1, 2), 1, self.styling.colors['medium_gray']),
            ('LINEBELOW', (0, 4), (-1, 4), 1, self.styling.colors['medium_gray']),
        ]))
        table.hAlign = 'CENTER'
        return table
    
    def _create_premium_footer(self):
        """Create ultra-premium footer"""
        footer_style = ParagraphStyle(
            name='PremiumFooterInfo',
            fontSize=11,
            alignment=TA_CENTER,
            textColor=self.styling.colors['dark_gray'],
            fontName='Helvetica',
            leading=16
        )
        
        footer_text = f"""
        <b>{self.config.company}</b><br/>
        <i>Professional Research &amp; Strategic Intelligence Division</i><br/>
        Advanced Market Analytics &amp; Business Intelligence<br/>
        <b>CONFIDENTIAL DOCUMENT - AUTHORIZED PERSONNEL ONLY</b>
        """
        
        return Paragraph(footer_text, footer_style)

class PremiumReportStyling:
    """Ultra-premium styling system with enhanced typography"""
    
    def __init__(self, brand_colors: Dict[str, str]):
        self.brand_colors = brand_colors
        self.styles = getSampleStyleSheet()
        self._setup_premium_colors()
        self._setup_premium_styles()
    
    def _setup_premium_colors(self):
        """Setup ultra-premium color palette"""
        self.colors = {
            'primary': Color(0.1, 0.2, 0.4),      # Deep blue
            'secondary': Color(0.8, 0.1, 0.1),    # Deep red
            'accent': Color(0.2, 0.3, 0.5),       # Medium blue
            'text': Color(0.2, 0.2, 0.2),         # Dark gray
            'light_gray': Color(0.9, 0.9, 0.9),   # Light gray
            'medium_gray': Color(0.6, 0.6, 0.6),  # Medium gray
            'dark_gray': Color(0.3, 0.3, 0.3),    # Dark gray
            'black': Color(0.0, 0.0, 0.0),        # Black
            'white': Color(1.0, 1.0, 1.0),        # White
        }
    
    def _setup_premium_styles(self):
        """Setup premium typography and styles"""
        # Ensure all premium colors are available - do not redefine, just add missing ones
        if 'medium_gray' not in self.colors:
            self.colors['medium_gray'] = Color(0.6, 0.6, 0.6)
        if 'dark_gray' not in self.colors:
            self.colors['dark_gray'] = Color(0.3, 0.3, 0.3)
        if 'black' not in self.colors:
            self.colors['black'] = Color(0.0, 0.0, 0.0)
        if 'white' not in self.colors:
            self.colors['white'] = Color(1.0, 1.0, 1.0)
        
        # Premium title style - increased size
        self.styles.add(ParagraphStyle(
            name='PremiumTitle',
            parent=self.styles['Heading1'],
            fontSize=28,  # Increased from 24
            leading=34,   # Increased from 28
            spaceAfter=24,
            alignment=1,  # Center
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold'
        ))
        
        # Premium subtitle style - increased size
        self.styles.add(ParagraphStyle(
            name='PremiumSubtitle',
            parent=self.styles['Normal'],
            fontSize=16,  # Increased from 14
            leading=20,   # Increased from 18
            spaceAfter=30,
            alignment=1,  # Center
            textColor=self.colors['secondary'],
            fontName='Helvetica-Oblique'
        ))
        
        # Premium company style - increased size
        self.styles.add(ParagraphStyle(
            name='PremiumCompany',
            parent=self.styles['Normal'],
            fontSize=14,  # Increased from 12
            leading=18,   # Increased from 16
            spaceAfter=6,
            alignment=1,  # Center
            textColor=self.colors['text'],
            fontName='Helvetica'
        ))
        
        # Premium heading style - increased size
        self.styles.add(ParagraphStyle(
            name='PremiumHeading',
            parent=self.styles['Heading1'],
            fontSize=20,  # Increased from 18
            leading=26,   # Increased from 22
            spaceAfter=16,
            spaceBefore=20,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=self.colors['accent'],
            borderPadding=0
        ))
        
        # Premium subheading style - increased size
        self.styles.add(ParagraphStyle(
            name='PremiumSubHeading',
            parent=self.styles['Heading2'],
            fontSize=16,  # Increased from 14
            leading=20,   # Increased from 18
            spaceAfter=12,
            spaceBefore=16,
            textColor=self.colors['secondary'],
            fontName='Helvetica-Bold'
        ))
        
        # Premium body text style - increased size
        self.styles.add(ParagraphStyle(
            name='PremiumBodyText',
            parent=self.styles['Normal'],
            fontSize=12,  # Increased from 10
            leading=16,   # Increased from 14
            spaceAfter=8,
            textColor=self.colors['text'],
            fontName='Helvetica',
            alignment=0,  # Left justified
            firstLineIndent=0
        ))
        
        # Premium highlight box style - increased size
        self.styles.add(ParagraphStyle(
            name='PremiumHighlightBox',
            parent=self.styles['Normal'],
            fontSize=11,  # Increased from 9
            leading=15,   # Increased from 13
            spaceAfter=12,
            spaceBefore=12,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=self.colors['accent'],
            borderPadding=8,
            backColor=Color(0.95, 0.97, 1.0)  # Very light blue
        ))
        
        # Premium bullet point style - increased size
        self.styles.add(ParagraphStyle(
            name='PremiumBulletPoint',
            parent=self.styles['Normal'],
            fontSize=11,  # Increased from 9
            leading=15,   # Increased from 13
            spaceAfter=6,
            leftIndent=20,
            textColor=self.colors['text'],
            fontName='Helvetica'
        ))
        
        # Premium caption style - increased size
        self.styles.add(ParagraphStyle(
            name='PremiumCaption',
            parent=self.styles['Normal'],
            fontSize=10,  # Increased from 8
            leading=13,   # Increased from 11
            spaceAfter=12,
            alignment=1,  # Center
            textColor=self.colors['accent'],
            fontName='Helvetica-Oblique'
        ))
        
        # Premium TOC entry style - increased size
        self.styles.add(ParagraphStyle(
            name='PremiumTOCEntry',
            parent=self.styles['Normal'],
            fontSize=11,  # Increased from 10
            leading=16,   # Increased from 14
            spaceAfter=4,
            textColor=self.colors['text'],
            fontName='Helvetica'
        ))
        
        # Premium TOC title style - increased size
        self.styles.add(ParagraphStyle(
            name='PremiumTOCTitle',
            parent=self.styles['Heading1'],
            fontSize=20,  # Increased from 18
            leading=26,   # Increased from 22
            spaceAfter=20,
            alignment=1,  # Center
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold'
        ))
        
        # Premium key insight style - increased size
        self.styles.add(ParagraphStyle(
            name='PremiumKeyInsight',
            parent=self.styles['Normal'],
            fontSize=12,  # Increased from 10
            leading=16,   # Increased from 14
            spaceAfter=10,
            spaceBefore=10,
            textColor=self.colors['secondary'],
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=self.colors['secondary'],
            borderPadding=12,
            backColor=Color(1.0, 0.98, 0.98)  # Very light red
        ))
        
        # Premium section title style - for section headers
        self.styles.add(ParagraphStyle(
            name='PremiumSectionTitle',
            parent=self.styles['Heading1'],
            fontSize=24,  # Large section title
            leading=30,   
            spaceAfter=18,
            spaceBefore=28,
            alignment=0,  # Left aligned
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=self.colors['accent'],
            borderPadding=12,
            backColor=None,
            leftIndent=0
        ))

class PremiumPDFGenerator:
    """Ultra-premium PDF generator with perfect structure"""
    
    def __init__(self, config, styling: PremiumReportStyling):
        self.config = config
        self.styling = styling
        self.story = []
        
    def _clean_markdown_content(self, content: str) -> str:
        """Enhanced markdown cleaning for premium formatting"""
        if not content:
            return ""
        
        # Remove markdown headers but preserve structure
        content = re.sub(r'^#{1,6}\s+(.+)$', r'<b>\1</b>', content, flags=re.MULTILINE)
        
        # Enhanced formatting
        content = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', content)
        content = re.sub(r'\*(.+?)\*', r'<i>\1</i>', content)
        content = re.sub(r'__(.+?)__', r'<b>\1</b>', content)
        content = re.sub(r'_(.+?)_', r'<i>\1</i>', content)
        
        # Premium bullet points
        content = re.sub(r'^[\s]*[-\*\+]\s+(.+)$', r'• \1', content, flags=re.MULTILINE)
        
        # Clean remaining markdown
        content = re.sub(r'`(.+?)`', r'<i>\1</i>', content)
        content = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', content)
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        return content.strip()
        
    def generate_complete_pdf(self, content: Dict[str, Any], images: Dict[str, str], visualizations: Dict[str, str]) -> str:
        """Generate ultra-premium PDF with perfect structure"""
        
        filename = f"./generated_reports/{self.config.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Create premium document with optimized margins
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2.2*cm,
            leftMargin=2.2*cm,
            topMargin=2.8*cm,
            bottomMargin=2.8*cm,
            title=self.config.title,
            author=self.config.author,
            subject=self.config.subtitle
        )
        
        self.story = []
        
        # PERFECT STRUCTURE - NO EMPTY PAGES
        # Page 1: Premium Cover
        self._add_premium_cover_page(images.get("cover"))
        
        # Page 2: Table of Contents (FIXED PLACEMENT)
        self._add_premium_table_of_contents()
        
        # Page 3+: Executive Summary with visuals
        self._add_premium_executive_summary(content["executive_summary"], visualizations, images)
        
        # Methodology with premium formatting
        self._add_premium_methodology_section(content["methodology"], images)
        
        # Market Overview (compact)
        self._add_premium_market_overview(content, images)
        
        # Key Findings with visualizations
        self._add_premium_findings_section(content["key_findings"], visualizations, images)
        
        # Detailed Analysis 
        self._add_premium_analysis_section(content["detailed_analysis"], images)
        
        # Competitive Analysis (compact)
        self._add_premium_competitive_section(content, images)
        
        # Strategic Recommendations
        self._add_premium_recommendations_section(content["recommendations"], images)
        
        # Risk Assessment (compact)
        self._add_premium_risk_section(content, images)
        
        # Appendices (compact)
        self._add_premium_appendices_section(content["appendices"])
        
        # Build premium PDF
        doc.build(self.story)
        return filename
    
    def _add_premium_cover_page(self, cover_image: str = None):
        """Add ultra-premium cover page"""
        cover_page = PremiumCoverPage(self.config, self.styling)
        cover_elements = cover_page.create_cover_elements(cover_image)
        self.story.extend(cover_elements)
        self.story.append(PageBreak())
    
    def _add_premium_table_of_contents(self):
        """Add premium table of contents on page 2"""
        # Premium TOC title
        self.story.append(Paragraph("Table of Contents", self.styling.styles['PremiumTOCTitle']))
        self.story.append(Spacer(1, 0.4*inch))
        
        # Premium TOC entries with better formatting
        toc_entries = [
            ("Executive Summary", "3"),
            ("Research Methodology", "5"), 
            ("Market Overview", "7"),
            ("Key Findings & Analysis", "8"),
            ("Detailed Market Analysis", "11"),
            ("Competitive Landscape", "13"),
            ("Strategic Recommendations", "14"),
            ("Risk Assessment", "16"),
            ("Appendices", "17")
        ]
        
        # Create premium TOC table
        toc_data = []
        for entry, page in toc_entries:
            dots = '.' * (50 - len(entry) - len(page))
            toc_data.append([entry, dots, page])
        
        toc_table = Table(toc_data, colWidths=[3.5*inch, 2*inch, 0.8*inch])
        toc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), self.styling.colors['primary']),
            ('TEXTCOLOR', (1, 0), (1, -1), self.styling.colors['medium_gray']),
            ('TEXTCOLOR', (2, 0), (2, -1), self.styling.colors['accent']),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, 0), 1, self.styling.colors['accent']),
        ]))
        
        self.story.append(toc_table)
        self.story.append(PageBreak())
    
    def _add_premium_executive_summary(self, summary_data: Dict[str, Any], visualizations: Dict[str, str], images: Dict[str, str]):
        """Add premium executive summary"""
        self.story.append(Paragraph("Executive Summary", self.styling.styles['PremiumSectionTitle']))
        
        # Strategic overview box
        overview = """This comprehensive analysis delivers critical market intelligence and strategic recommendations 
        for executive decision-making. Our research combines quantitative market data with qualitative insights 
        to provide actionable guidance for competitive positioning and growth strategy implementation."""
        
        self.story.append(Paragraph(overview, self.styling.styles['PremiumHighlightBox']))
        
        # Key findings highlight
        key_findings = """
        <b>Executive Highlights:</b><br/>
        • Market demonstrates robust growth potential with emerging opportunities<br/>
        • Technology disruption creates competitive differentiation possibilities<br/>
        • Strategic partnerships present immediate value creation potential<br/>
        • Regulatory landscape offers strategic positioning advantages
        """
        self.story.append(Paragraph(key_findings, self.styling.styles['PremiumKeyInsight']))
        
        # Clean and add main content
        if summary_data.get("content"):
            cleaned_content = self._clean_markdown_content(summary_data["content"])
            self._add_formatted_content(cleaned_content, max_paragraphs=8)
        
        # Add executive dashboard if available
        if "executive_dashboard" in visualizations:
            self._add_premium_visualization(self.story, visualizations["executive_dashboard"], "Executive Research Dashboard", "CENTER")
        
        # Add executive image if available
        if "executive_concept" in images:
            self._add_premium_visualization(self.story, images["executive_concept"], "Strategic Market Overview", "CENTER")
        
        self.story.append(PageBreak())
    
    def _add_premium_methodology_section(self, methodology_data: Dict[str, Any], images: Dict[str, str]):
        """Add premium methodology section"""
        self.story.append(Paragraph("Research Methodology", self.styling.styles['PremiumSectionTitle']))
        
        methodology_intro = """Our research methodology employs advanced analytical frameworks and industry-standard 
        practices to ensure data quality, analytical rigor, and strategic relevance for executive decision-making."""
        
        self.story.append(Paragraph(methodology_intro, self.styling.styles['PremiumHighlightBox']))
        
        # Clean and add methodology content
        if methodology_data.get("content"):
            cleaned_content = self._clean_markdown_content(methodology_data["content"])
            self._add_formatted_content(cleaned_content, max_paragraphs=6)
        
        # Add methodology image if available
        if "methodology_concept" in images:
            self._add_premium_visualization(self.story, images["methodology_concept"], "Research Framework", "CENTER")
        
        self.story.append(PageBreak())
    
    def _add_premium_market_overview(self, content: Dict[str, Any], images: Dict[str, str]):
        """Add compact premium market overview"""
        self.story.append(Paragraph("Market Overview", self.styling.styles['PremiumSectionTitle']))
        
        market_overview = """The market landscape demonstrates dynamic evolution with significant transformation 
        opportunities driven by technology adoption, changing customer expectations, and regulatory developments."""
        
        self.story.append(Paragraph(market_overview, self.styling.styles['PremiumBodyText']))
        
        # Add market overview image if available
        if "market_overview" in images:
            self._add_premium_visualization(self.story, images["market_overview"], "Market Ecosystem", "CENTER")
    
    def _add_premium_findings_section(self, findings_data: Dict[str, Any], visualizations: Dict[str, str], images: Dict[str, str]):
        """Add premium findings section with visualizations"""
        self.story.append(Paragraph("Key Findings & Analysis", self.styling.styles['PremiumSectionTitle']))
        
        findings_intro = """Our comprehensive analysis reveals critical market insights with strategic implications 
        for competitive positioning and growth strategy development."""
        
        self.story.append(Paragraph(findings_intro, self.styling.styles['PremiumHighlightBox']))
        
        # Clean and add findings content
        if findings_data.get("content"):
            cleaned_content = self._clean_markdown_content(findings_data["content"])
            self._add_formatted_content(cleaned_content, max_paragraphs=10)
        
        # Add findings visualization
        if "key_findings" in images:
            self._add_premium_visualization(self.story, images["key_findings"], "Key Market Insights", "CENTER")
        
        # Add trend analysis chart
        viz_count = 0
        for viz_name, viz_data in visualizations.items():
            if viz_name != "executive_dashboard" and viz_count < 2:
                self._add_premium_visualization(self.story, viz_data, f"Analysis: {viz_name.replace('_', ' ').title()}", "CENTER")
                viz_count += 1
        
        self.story.append(PageBreak())
    
    def _add_premium_analysis_section(self, analysis_data: Dict[str, Any], images: Dict[str, str]):
        """Add premium detailed analysis"""
        self.story.append(Paragraph("Detailed Market Analysis", self.styling.styles['PremiumSectionTitle']))
        
        # Clean and add analysis content
        if analysis_data.get("content"):
            cleaned_content = self._clean_markdown_content(analysis_data["content"])
            self._add_formatted_content(cleaned_content, max_paragraphs=8)
        
        # Add analysis image
        if "detailed_analysis" in images:
            self._add_premium_visualization(self.story, images["detailed_analysis"], "Market Analysis Framework", "CENTER")
        
        self.story.append(PageBreak())
    
    def _add_premium_competitive_section(self, content: Dict[str, Any], images: Dict[str, str]):
        """Add compact competitive analysis"""
        self.story.append(Paragraph("Competitive Landscape", self.styling.styles['PremiumSectionTitle']))
        
        competitive_analysis = """The competitive environment demonstrates increasing complexity with traditional 
        leaders facing disruption from innovative market entrants leveraging technology and new business models."""
        
        self.story.append(Paragraph(competitive_analysis, self.styling.styles['PremiumBodyText']))
        
        # Add competitive image
        if "competitive_landscape" in images:
            self._add_premium_visualization(self.story, images["competitive_landscape"], "Competitive Positioning", "CENTER")
    
    def _add_premium_recommendations_section(self, recommendations_data: Dict[str, Any], images: Dict[str, str]):
        """Add premium recommendations"""
        self.story.append(Paragraph("Strategic Recommendations", self.styling.styles['PremiumSectionTitle']))
        
        recommendations_intro = """Our strategic recommendations provide actionable guidance for competitive 
        positioning, growth acceleration, and operational excellence aligned with market opportunities."""
        
        self.story.append(Paragraph(recommendations_intro, self.styling.styles['PremiumHighlightBox']))
        
        # Clean and add recommendations content
        if recommendations_data.get("content"):
            cleaned_content = self._clean_markdown_content(recommendations_data["content"])
            self._add_formatted_content(cleaned_content, max_paragraphs=8)
        
        # Add recommendations image
        if "strategic_recommendations" in images:
            self._add_premium_visualization(self.story, images["strategic_recommendations"], "Implementation Framework", "CENTER")
        
        self.story.append(PageBreak())
    
    def _add_premium_risk_section(self, content: Dict[str, Any], images: Dict[str, str]):
        """Add compact risk assessment"""
        self.story.append(Paragraph("Risk Assessment", self.styling.styles['PremiumSectionTitle']))
        
        risk_assessment = """Strategic risk management integrates market intelligence with operational planning 
        to identify potential challenges and develop mitigation strategies for sustainable competitive advantage."""
        
        self.story.append(Paragraph(risk_assessment, self.styling.styles['PremiumBodyText']))
        
        # Add risk image
        if "risk_assessment" in images:
            self._add_premium_visualization(self.story, images["risk_assessment"], "Risk Management Framework", "CENTER")
    
    def _add_premium_appendices_section(self, appendices_data: Dict[str, Any]):
        """Add compact appendices"""
        self.story.append(Paragraph("Appendices", self.styling.styles['PremiumSectionTitle']))
        
        appendices_intro = """Supporting data, methodological details, and supplementary information 
        that validate our analysis and provide additional context for strategic decision-making."""
        
        self.story.append(Paragraph(appendices_intro, self.styling.styles['PremiumBodyText']))
        
        # Add compact appendices content
        if appendices_data.get("content"):
            cleaned_content = self._clean_markdown_content(appendices_data["content"])
            self._add_formatted_content(cleaned_content, max_paragraphs=4)
    
    def _add_formatted_content(self, content: str, max_paragraphs: int = 10):
        """Add formatted content with paragraph limits to avoid empty pages"""
        if not content:
            return
            
        paragraphs = content.split('\n\n')
        paragraph_count = 0
        
        for para in paragraphs:
            if para.strip() and paragraph_count < max_paragraphs:
                self.story.append(Paragraph(para.strip(), self.styling.styles['PremiumBodyText']))
                paragraph_count += 1
                
                # Add spacing only between paragraphs, not after last one
                if paragraph_count < max_paragraphs and paragraph_count < len(paragraphs):
                    self.story.append(Spacer(1, 0.1*inch))
    
    def _add_premium_visualization(self, story, viz_base64, caption, alignment='CENTER'):
        """Add a premium visualization with enhanced validation - prevents empty boxes"""
        
        # Enhanced validation - skip if visualization is empty or invalid
        if not viz_base64 or viz_base64 == "" or viz_base64 == "data:image/png;base64,":
            print(f"⚠️ Skipping empty visualization: {caption}")
            return  # Don't add anything if visualization is invalid
        
        try:
            # Remove data URL prefix if present
            if viz_base64.startswith('data:image'):
                viz_base64 = viz_base64.split(',')[1]
            
            # Validate base64 data
            import base64
            try:
                image_data = base64.b64decode(viz_base64)
                if len(image_data) < 100:  # Too small to be a valid image
                    print(f"⚠️ Skipping invalid visualization (too small): {caption}")
                    return
            except Exception as decode_error:
                print(f"⚠️ Skipping visualization with decode error: {caption} - {decode_error}")
                return
            
            # Create image from base64 and validate
            from PIL import Image as PILImage
            import io
            
            pil_image = PILImage.open(io.BytesIO(image_data))
            
            # Validate image dimensions
            if pil_image.size[0] < 50 or pil_image.size[1] < 50:
                print(f"⚠️ Skipping visualization with invalid dimensions: {caption}")
                return
            
            # Premium image sizing for A4 (optimized for readability)
            max_width_inches = 6.5  # Maximum width in inches for A4
            max_height_inches = 4.5  # Maximum height in inches
            
            # Calculate scaling to maintain aspect ratio
            original_width = pil_image.size[0]
            original_height = pil_image.size[1]
            
            # Convert to inches (assuming 96 DPI for display)
            width_inches = original_width / 96
            height_inches = original_height / 96
            
            # Scale if necessary
            if width_inches > max_width_inches or height_inches > max_height_inches:
                scale_factor = min(max_width_inches / width_inches, max_height_inches / height_inches)
                final_width_inches = width_inches * scale_factor
                final_height_inches = height_inches * scale_factor
            else:
                final_width_inches = width_inches
                final_height_inches = height_inches
            
            # Convert back to points (1 inch = 72 points)
            final_width_points = final_width_inches * 72
            final_height_points = final_height_inches * 72
            
            # Create ReportLab Image object directly from BytesIO
            from reportlab.platypus import Image
            image_buffer = io.BytesIO(image_data)
            reportlab_image = Image(image_buffer, width=final_width_points, height=final_height_points)
            
            # Set alignment
            if alignment == 'CENTER':
                reportlab_image.hAlign = 'CENTER'
            elif alignment == 'LEFT':
                reportlab_image.hAlign = 'LEFT'
            elif alignment == 'RIGHT':
                reportlab_image.hAlign = 'RIGHT'
            
            # Add premium spacing before visualization
            story.append(Spacer(1, 16))
            
            # Add the image directly to the story
            story.append(reportlab_image)
            
            # Add premium caption with larger font
            if caption:
                from reportlab.lib.styles import ParagraphStyle
                from reportlab.lib import colors
                caption_style = ParagraphStyle(
                    'PremiumCaption',
                    parent=self.styling.styles['Normal'],
                    fontSize=11,  # Increased from 9
                    leading=14,   # Increased from 11
                    alignment=1,  # Center
                    textColor=colors.Color(0.2, 0.3, 0.5),
                    fontName='Helvetica-Bold',
                    spaceAfter=16
                )
                story.append(Paragraph(f"<i>{caption}</i>", caption_style))
            
            story.append(Spacer(1, 12))
            print(f"✅ Successfully added visualization: {caption}")
            
        except Exception as e:
            print(f"❌ Error adding visualization '{caption}': {e}")
            # Don't add any placeholder - just skip the problematic visualization
            return

    def _add_safe_image(self, title: str, image_key: str, images: Dict[str, str]):
        """Safely add images with validation - NO EMPTY BOXES"""
        if not images or image_key not in images:
            print(f"⚠️ Skipping missing image: {title} ({image_key})")
            return
            
        image_data = images.get(image_key)
        if not image_data or image_data.strip() == "":
            print(f"⚠️ Skipping empty image: {title} ({image_key})")
            return
            
        # Use the existing visualization method with validation
        self._add_premium_visualization(self.story, image_data, title, "CENTER") 