# query-to-pdf/main_application.py

import os
import re
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

# Import the content and visualization generators
from report_planner import ReportPlanner, ReportType
from advanced_content_generator import ReportConfig
from enhanced_visualization_generator import PremiumVisualizationGenerator

# Import the Typst renderer
from typst_renderer import render_to_pdf_with_typst

# Import Firecrawl integration
from firecrawl_integration import FirecrawlReportGenerator

class ProfessionalReportGenerator:
    """Orchestrates the AI-driven report generation with Typst."""

    def __init__(self, gemini_api_key: Optional[str], firecrawl_api_key: Optional[str] = None):
        self.report_planner = ReportPlanner(api_key=gemini_api_key)
        # Initialize with default colors, will be updated based on template
        self.data_visualizer = PremiumVisualizationGenerator(brand_colors={"primary": "#0D203D", "accent": "#4A90E2"})
        
        # Initialize Firecrawl integration
        self.firecrawl_generator = FirecrawlReportGenerator(firecrawl_api_key, gemini_api_key) if firecrawl_api_key else None

    def _get_template_colors(self, template: str) -> Dict[str, str]:
        """Extract color palette from the specified template."""
        template_colors = {
            "template_0": {
                "primary": "#0D203D",    # rgb(13, 32, 61) - Deep navy blue
                "secondary": "#2D3748",  # rgb(45, 55, 72) - Dark gray
                "accent": "#4A90E2",     # rgb(74, 144, 226) - Blue accent
                "background": "#F7FAFC"  # Light background
            },
            "template_1": {
                "primary": "#1A2B42",    # Deep navy blue
                "secondary": "#4A5568",  # Medium gray
                "accent": "#D69E2E",     # Golden-amber
                "background": "#F7FAFC"  # Very light gray
            },
            "template_2": {
                "primary": "#AF3029",    # Deep red
                "secondary": "#25241C",  # Dark charcoal
                "accent": "#AF3029",     # Deep red (same as primary)
                "background": "#FFFCF0"  # Warm off-white
            }
        }
        
        return template_colors.get(template, template_colors["template_1"])

    def _convert_content_to_typst(self, content: str) -> str:
        """Converts custom markdown to Typst syntax."""
        if not content:
            return ""
            
        # Process bolding: **text** -> *text*
        content = re.sub(r'\*\*(.*?)\*\*', r'*\1*', content)
        
        # Process bullet points: "- text" -> "* text"
        content = re.sub(r'^\s*-\s+', '* ', content, flags=re.MULTILINE)
        
        return content

    async def generate_comprehensive_report(self, config: ReportConfig, query: str, page_count: int, template: str = "template_1", use_web_research: bool = False) -> str:
        
        # Check if we should use web research
        if use_web_research and self.firecrawl_generator:
            print("\n🌐 Using real-time web research with Firecrawl...")
            try:
                result = await self.firecrawl_generator.generate_report_from_web_research(
                    query=query,
                    page_count=page_count,
                    report_type=ReportType.MARKET_RESEARCH
                )
                
                if result["success"]:
                    print(f"✅ Web research report generated: {result['pdf_path']}")
                    print(f"💳 Credits used: {result['credits_used']}")
                    return result['pdf_path']
                else:
                    print("❌ Web research failed, falling back to AI generation")
            except Exception as e:
                print(f"❌ Web research error: {e}, falling back to AI generation")
        
        # Fallback to AI-generated content
        print("\n🤖 Phase 1: AI is designing the full report blueprint...")
        report_blueprint = await self.report_planner.generate_report_blueprint(query, page_count, ReportType.MARKET_RESEARCH)
        if not report_blueprint or "sections" not in report_blueprint:
            raise ValueError("AI failed to generate a valid report blueprint.")
        
        # Get template-specific colors and update the visualizer
        template_colors = self._get_template_colors(template)
        self.data_visualizer = PremiumVisualizationGenerator(brand_colors=template_colors)
        
        print("\n📊 Phase 2: Creating dynamic data visualizations...")
        for section in report_blueprint.get("sections", []):
            # Convert content to Typst format
            if "content" in section:
                section["content"] = self._convert_content_to_typst(section["content"])

            chart_type = section.get("chart_type")
            if chart_type and chart_type != "none":
                print(f"  🎨 Generating '{chart_type}' chart for: {section['title']}...")
                chart_path = self.data_visualizer.create_chart(section)
                section["chart_path"] = chart_path
            else:
                section["chart_path"] = ""
        
        print("\n🚀 Phase 3: Compiling the final PDF report with Typst...")
        output_filename = self._export_to_pdf(config, report_blueprint, template)
        
        return output_filename

    def _export_to_pdf(self, config: ReportConfig, blueprint: Dict[str, Any], template: str = "template_1") -> str:
        """Assembles data and calls the Typst renderer."""
        sanitized_title = re.sub(r'[\\/*?:"<>|]', "", config.title)
        filename = f"./generated_reports/{sanitized_title[:50]}.pdf"
        
        # Prepare the data dictionary for Typst
        sections = blueprint.get("sections", []) or []
        
        template_path = f"templates/{template}.typ"
        
        # Adjust logo path to be relative to the template directory
        logo_path = ""
        if config.logo_path and os.path.exists(str(config.logo_path)):
            if config.logo_path.startswith("assets/"):
                # Convert assets/logo.png to ../assets/logo.png relative to templates/
                logo_path = f"../{config.logo_path}"
                # Check if the adjusted path exists relative to template directory
                template_dir = os.path.dirname(template_path)
                adjusted_path_exists = os.path.exists(os.path.join(template_dir, logo_path))
            elif config.logo_path.startswith("templates/"):
                # If logo is in templates directory, use just the filename
                logo_path = os.path.basename(config.logo_path)
                template_dir = os.path.dirname(template_path)
                adjusted_path_exists = os.path.exists(os.path.join(template_dir, logo_path))
            elif os.path.isabs(config.logo_path):
                # If it's an absolute path, make it relative to template directory
                template_dir = os.path.dirname(template_path)
                logo_path = os.path.relpath(config.logo_path, template_dir)
                adjusted_path_exists = os.path.exists(os.path.join(template_dir, logo_path))
            else:
                # For other relative paths, assume they're relative to project root
                logo_path = f"../{config.logo_path}"
                template_dir = os.path.dirname(template_path)
                adjusted_path_exists = os.path.exists(os.path.join(template_dir, logo_path))
        
        report_data = {
            "title": config.title,
            "subtitle": config.subtitle,
            "author": config.author,
            "company": config.company,
            "logo_path": logo_path,
            "date": datetime.now().strftime('%B %d, %Y'),
            "sections": sections
        }
        
        # Adjust chart paths to be relative to the template directory
        for section in sections:
            if isinstance(section, dict):
                chart_path = section.get("chart_path")
                if chart_path and isinstance(chart_path, str) and chart_path != "":
                    print(f"  🔍 Debug - Original chart path: {chart_path}")
                    # Convert chart path to be relative to the template directory (like template 1)
                    if chart_path.startswith("temp_charts/"):
                        section["chart_path"] = f"../{chart_path}"  # Go up one level from templates/ to find temp_charts/
                    elif os.path.isabs(chart_path):
                        # If it's an absolute path, make it relative to template directory
                        template_dir = os.path.dirname(template_path)
                        rel_path = os.path.relpath(chart_path, template_dir)
                        section["chart_path"] = rel_path
                    
                    print(f"  🔍 Debug - Adjusted chart path: {section['chart_path']}")
                    # Check if the file actually exists
                    template_dir = os.path.dirname(template_path)
                    full_path = os.path.join(template_dir, section["chart_path"])
                    print(f"  🔍 Debug - Full path: {full_path}")
                    print(f"  🔍 Debug - File exists: {os.path.exists(full_path)}")
        
        success = render_to_pdf_with_typst(report_data, template_path, filename)
        
        if success:
            print(f"✅ Successfully generated final PDF: {filename}")
            return filename
        else:
            raise RuntimeError("Failed to generate PDF using Typst. Check the logs for details.")