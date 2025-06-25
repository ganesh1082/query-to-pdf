# query-to-pdf copy/main_application.py

import os
import re
from typing import Dict, Any, Optional
from weasyprint import HTML
import traceback
import asyncio

from advanced_content_generator import AdvancedContentGenerator, ReportConfig
from enhanced_visualization_generator import PremiumVisualizationGenerator
from html_renderer import generate_html_from_blueprint

class ProfessionalReportGenerator:
    """Orchestrates the AI-driven report generation from a single, unified blueprint."""

    def __init__(self, gemini_api_key: Optional[str]):
        self.content_generator = AdvancedContentGenerator(api_key=gemini_api_key)
        self.data_visualizer = PremiumVisualizationGenerator(brand_colors={"primary": "#0D203D", "accent": "#4A90E2"})

    async def generate_comprehensive_report(self, config: ReportConfig, query: str, page_count: int) -> str:
        
        print("\n🤖 Phase 1: AI is designing the full report blueprint...")
        report_blueprint = await self.content_generator.generate_full_report_blueprint(query, page_count)
        if not report_blueprint or "sections" not in report_blueprint:
            raise ValueError("AI failed to generate a valid report blueprint.")
        
        # --- THIS IS THE NEW, CORRECTED VISUALIZATION LOGIC ---
        print("\n📊 Phase 2: Creating dynamic visualizations based on the blueprint...")
        visualizations = {}
        for section in report_blueprint.get("sections", []):
            title = section.get("title")
            chart_type = section.get("chart_type")

            if title and chart_type and chart_type != "none":
                print(f"  🎨 Generating '{chart_type}' chart for section: {title}...")
                # Create chart details with proper structure
                chart_details = {
                    "chart_type": chart_type,
                    "data": section.get("chart_data", {}),
                    "title": title,
                    "color_palette": "viridis"  # Use default palette
                }
                # Call the public create_chart method - now returns file path
                chart_file_path = self.data_visualizer.create_chart(chart_details)
                visualizations[title] = chart_file_path
        print(f"  ✅ Successfully generated {len(visualizations)} charts.")
        # -----------------------------------------------------------
        
        print("\n📄 Phase 3: Rendering Final HTML from the blueprint...")
        final_html = generate_html_from_blueprint(config, report_blueprint, visualizations)

        with open("debug_report.html", "w", encoding="utf-8") as f:
            f.write(final_html)
        print("  ✅ Final dynamic HTML saved to 'debug_report.html' for inspection.")
        
        print("\n🚀 Phase 4: Exporting HTML to Professional PDF...")
        output_filename = self._export_to_pdf(config, final_html)
        
        return output_filename

    def _export_to_pdf(self, config: ReportConfig, html_content: str) -> str:
        """Converts the final HTML string to a PDF file."""
        sanitized_title = re.sub(r'[\\/*?:"<>|]', "", config.title)
        filename = f"./generated_reports/{sanitized_title[:50]}.pdf"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if not html_content.strip() or "<body></body>" in html_content:
            raise ValueError("Cannot generate PDF from empty HTML content. Check debug_report.html.")
            
        try:
            HTML(string=html_content).write_pdf(filename)
            print(f"✅ Successfully generated final PDF: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Critical Error: WeasyPrint could not write final PDF file. {e}")
            traceback.print_exc()
            raise