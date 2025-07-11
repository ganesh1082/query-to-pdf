# Deprecated: All main logic is now in index.py using EnhancedPDFGenerator.
# This file is retained for reference only and is no longer used.

import os
import re
import json
import time
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the content and visualization generators
from report_planner import ReportPlanner, ReportType
from advanced_content_generator import ReportConfig
from enhanced_visualization_generator import PremiumVisualizationGenerator

# Import the Typst renderer
from typst_renderer import render_to_pdf_with_typst

# Import Firecrawl integration
from firecrawl_integration import FirecrawlReportGenerator
from enhanced_firecrawl_integration import EnhancedFirecrawlReportGenerator

class ProfessionalReportGenerator:
    """Orchestrates the AI-driven report generation with Typst following the new workflow."""

    def __init__(self, gemini_api_key: str):
        self.report_planner = ReportPlanner(api_key=gemini_api_key)
        self.data_visualizer = PremiumVisualizationGenerator(brand_colors={"primary": "#0D203D", "accent": "#4A90E2"})
        
        # Initialize Firecrawl generators
        self.firecrawl_generator: Optional[FirecrawlReportGenerator] = None
        self.enhanced_firecrawl_generator: Optional[EnhancedFirecrawlReportGenerator] = None
        try:
            # Try enhanced generator first
            self.enhanced_firecrawl_generator = EnhancedFirecrawlReportGenerator(gemini_api_key)
            print("✅ Enhanced Firecrawl generator initialized successfully")
        except Exception as e:
            print(f"⚠️ Enhanced Firecrawl generator initialization failed: {e}")
            try:
                # Fallback to original generator
                self.firecrawl_generator = FirecrawlReportGenerator(gemini_api_key)
                print("✅ Original Firecrawl generator initialized successfully")
            except Exception as e2:
                print(f"⚠️ Original Firecrawl generator initialization failed: {e2}")
                self.firecrawl_generator = None

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

    async def _collect_learnings_from_firecrawl(self, query: str) -> Dict[str, Any]:
        """Step 1: Collect learnings from Firecrawl URL"""
        print("\n🔍 Step 1: Collecting learnings from Firecrawl...")
        
        # Try enhanced generator first, then fallback to original
        generator = self.enhanced_firecrawl_generator or self.firecrawl_generator
        
        if not generator:
            print("❌ No Firecrawl generator available")
            return {"learnings": [], "sources": [], "success": False}
        
        try:
            if self.enhanced_firecrawl_generator:
                print("🚀 Using enhanced Firecrawl research...")
                research_result = await self.enhanced_firecrawl_generator.collect_learnings_only(query)
                
                learnings = research_result.get("learnings", [])
                sources = research_result.get("sources", [])
                comprehensive_report = research_result.get("comprehensive_report", "")
                
                print(f"📊 Enhanced Firecrawl research completed:")
                print(f"   - Learnings found: {len(learnings)}")
                print(f"   - Sources found: {len(sources)}")
                print(f"   - Comprehensive report: {len(comprehensive_report)} characters")
                
            else:
                print("🔄 Using original Firecrawl research...")
                if self.firecrawl_generator and self.firecrawl_generator.firecrawl_research:
                    research_result = await self.firecrawl_generator.firecrawl_research.deep_research(query)
                    
                    learnings = research_result.get("learnings", [])
                    sources = research_result.get("source_metadata", [])
                    comprehensive_report = ""
                    
                    print(f"📊 Original Firecrawl research completed:")
                    print(f"   - Learnings found: {len(learnings)}")
                    print(f"   - Sources found: {len(sources)}")
                else:
                    print("❌ Original Firecrawl generator not properly initialized")
                    return {"learnings": [], "sources": [], "success": False}
            
            # Check if we have meaningful learnings
            if not learnings or len(learnings) == 0:
                print("⚠️ No learnings found from Firecrawl")
                return {"learnings": [], "sources": [], "success": False}
            
            # Filter out learnings that are empty or just whitespace
            filtered_learnings = [learning for learning in learnings if learning and learning.strip()]
            
            if not filtered_learnings:
                print("⚠️ All learnings were empty or invalid")
                return {"learnings": [], "sources": [], "success": False}
            
            print(f"✅ Successfully collected {len(filtered_learnings)} valid learnings")
            return {
                "learnings": filtered_learnings,
                "sources": sources,
                "success": True,
                "requests_used": research_result.get("requests_used", 0),
                "comprehensive_report": comprehensive_report,
                "method": research_result.get("method", "unknown")
            }
            
        except Exception as e:
            print(f"❌ Error collecting learnings from Firecrawl: {e}")
            return {"learnings": [], "sources": [], "success": False}

    async def _generate_report_from_learnings(self, query: str, learnings: List[str], sources: List[Dict], page_count: int, template: str) -> Dict[str, Any]:
        """Step 2: Use learnings with Gemini to generate titles, descriptions, and charts"""
        print("\n🤖 Step 2: Generating report from learnings using Gemini...")
        
        if not learnings:
            print("❌ No learnings available for report generation")
            return {"success": False, "error": "No learnings available"}
        
        try:
            # Use the report planner with learnings to generate the blueprint
            blueprint = await self.report_planner.generate_report_blueprint(
                query=query,
                page_count=page_count,
                report_type=ReportType.MARKET_RESEARCH,
                learnings=learnings,
                source_metadata=sources
            )
            
            if not blueprint or "sections" not in blueprint:
                print("❌ Failed to generate report blueprint from learnings")
                return {"success": False, "error": "Failed to generate blueprint"}
            
            # Get template-specific colors and update the visualizer
            template_colors = self._get_template_colors(template)
            self.data_visualizer = PremiumVisualizationGenerator(brand_colors=template_colors)
            
            # Use Firecrawl integration for chart generation if available
            if self.enhanced_firecrawl_generator:
                print("\n📊 Generating visualizations using enhanced Firecrawl integration...")
                await self.enhanced_firecrawl_generator._generate_visualizations(blueprint)
            elif self.firecrawl_generator:
                print("\n📊 Generating visualizations using original Firecrawl integration...")
                await self.firecrawl_generator._generate_visualizations(blueprint)
            else:
                print("\n📊 Generating visualizations using direct chart creation...")
                for section in blueprint.get("sections", []):
                    # Convert content to Typst format
                    if "content" in section:
                        section["content"] = self._convert_content_to_typst(section["content"])

                    chart_type = section.get("chart_type")
                    if chart_type and chart_type != "none":
                        print(f"  🎨 Generating '{chart_type}' chart for: {section['title']}...")
                        try:
                            # Use the PDF-specific chart creation method
                            chart_path = self.data_visualizer.create_chart_for_pdf(section)
                            section["chart_path"] = chart_path
                        except Exception as e:
                            print(f"  ⚠️ Error generating chart for '{section['title']}': {e}")
                            section["chart_path"] = ""
                    else:
                        section["chart_path"] = ""
            
            return {
                "success": True,
                "blueprint": blueprint
            }
            
        except Exception as e:
            print(f"❌ Error generating report from learnings: {e}")
            return {"success": False, "error": str(e)}

    async def _generate_pdf_and_json(self, config: ReportConfig, blueprint: Dict[str, Any], learnings: List[str], sources: List[Dict], template: str) -> Dict[str, Any]:
        """Step 3: Generate PDF and create JSON with all data including PDF path"""
        print("\n📄 Step 3: Generating PDF and JSON...")
        
        try:
            # Generate PDF
            timestamp = int(time.time())
            safe_title = "".join(c for c in config.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')[:50]
            
            reports_dir = os.getenv("REPORTS_OUTPUT_DIR", "generated_reports")
            os.makedirs(reports_dir, exist_ok=True)
            pdf_filename = f"{reports_dir}/{timestamp}_{safe_title}.pdf"
            
            # Prepare report data for PDF generation
            report_data = {
                "title": config.title,
                "subtitle": config.subtitle,
                "author": config.author,
                "company": config.company,
                "logo_path": config.logo_path,
                "date": datetime.now().strftime('%B %d, %Y'),
                "sections": blueprint.get("sections", [])
            }
            
            # Generate PDF using Typst
            template_path = f"templates/{template}.typ"
            
            # Adjust chart paths to be relative to the template directory
            sections = report_data.get("sections", []) or []
            for section in sections:
                if isinstance(section, dict):
                    chart_path = section.get("chart_path")
                    if chart_path and isinstance(chart_path, str) and chart_path != "":
                        # Charts are now saved in assets directory, so use relative path
                        if chart_path.startswith("assets/"):
                            section["chart_path"] = f"../{chart_path}"
                        elif os.path.isabs(chart_path):
                            # If it's an absolute path, make it relative to template directory
                            template_dir = os.path.dirname(template_path) if template_path else "templates"
                            rel_path = os.path.relpath(chart_path, template_dir)
                            section["chart_path"] = rel_path
            
            success = render_to_pdf_with_typst(report_data, template_path, pdf_filename)
            
            if not success:
                raise RuntimeError("Failed to generate PDF using Typst")
            
            # Create comprehensive JSON with all data
            json_data = {
                "title": config.title,
                "subtitle": config.subtitle,
                "author": config.author,
                "company": config.company,
                "logo_path": config.logo_path,
                "date": datetime.now().strftime('%B %d, %Y'),
                "sections": blueprint.get("sections", []),
                "firecrawl_research": {
                    "key_findings": learnings,
                    "sources": sources,
                    "research_metrics": {
                        "total_sources": len(sources),
                        "high_quality_sources": len([s for s in sources if s.get("reliability_score", 0) > 0.7]),
                        "average_reliability": sum(s.get("reliability_score", 0) for s in sources) / len(sources) if sources else 0
                    },
                    "credits_used": 0,  # Firecrawl URL doesn't use credits
                    "total_sources": len(sources),
                    "high_quality_sources": len([s for s in sources if s.get("reliability_score", 0) > 0.7])
                },
                "pdf_path": pdf_filename  # Add PDF path to JSON
            }
            
            # Save JSON report
            json_dir = os.getenv("JSON_REPORTS_DIR", "json_reports")
            os.makedirs(json_dir, exist_ok=True)
            json_filename = f"{json_dir}/{timestamp}_{safe_title}.json"
            
            with open(json_filename, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            print(f"✅ Successfully generated:")
            print(f"   - PDF: {pdf_filename}")
            print(f"   - JSON: {json_filename}")
            
            return {
                "success": True,
                "pdf_path": pdf_filename,
                "json_path": json_filename,
                "report_data": json_data
            }
            
        except Exception as e:
            print(f"❌ Error generating PDF and JSON: {e}")
            return {"success": False, "error": str(e)}

    async def generate_comprehensive_report(self, config: ReportConfig, query: str, page_count: int, template: str = "template_1", use_web_research: bool = True) -> Dict[str, Any]:
        """Main method following the new workflow - Uses template_1 by default"""
        print(f"🚀 Starting comprehensive report generation for: {query}")
        print(f"📊 Configuration: {page_count} pages, template: {template}, web research: {use_web_research}")
        
        if use_web_research and self.firecrawl_generator:
            # Use the Firecrawl integration for web research
            print("🌐 Using Firecrawl integration for web research...")
            try:
                result = await self.firecrawl_generator.generate_report_from_web_research(
                    query=query,
                    page_count=page_count,
                    report_type=ReportType.MARKET_RESEARCH,
                    template=template
                )
                
                if result["success"]:
                    print(f"✅ Firecrawl report generation completed successfully!")
                    print(f"📄 PDF: {result['pdf_path']}")
                    return {
                        "success": True,
                        "pdf_path": result["pdf_path"],
                        "json_path": "",
                        "report_data": result.get("blueprint", {}),
                        "requests_used": result.get("requests_used", 0),
                        "learnings_count": result.get("learnings_count", 0),
                        "sources_count": result.get("sources_count", 0)
                    }
                else:
                    print(f"❌ Firecrawl report generation failed: {result.get('error', 'Unknown error')}")
                    # Fall back to AI-only generation
                    print("🔄 Falling back to AI-only generation...")
                    
            except Exception as e:
                print(f"❌ Firecrawl integration error: {e}")
                print("🔄 Falling back to AI-only generation...")
        
        # Fallback to AI generation without web research
        print("⚠️ Using AI generation only (no web research)")
        
        # Step 1: Collect learnings from Firecrawl (if available)
        learnings = []
        sources = []
        if use_web_research:
            firecrawl_result = await self._collect_learnings_from_firecrawl(query)
            if firecrawl_result["success"]:
                learnings = firecrawl_result["learnings"]
                sources = firecrawl_result["sources"]
                
                # Check for halfway point with 0 learnings
                halfway_point = len(learnings) // 2
                if halfway_point > 0:
                    # Check if learnings after halfway are 0 or empty
                    later_learnings = learnings[halfway_point:]
                    if all(not learning or learning.strip() == "" for learning in later_learnings):
                        print(f"⚠️ Found 0 learnings after halfway point, using first {halfway_point} learnings")
                        learnings = learnings[:halfway_point]
                        # Also filter sources accordingly if needed
                        sources = sources[:halfway_point] if len(sources) > halfway_point else sources
        
        # Step 2: Generate report from learnings using Gemini
        report_result = await self._generate_report_from_learnings(query, learnings, sources, page_count, template)
        
        if not report_result["success"]:
            print("❌ Failed to generate report from learnings")
            return {
                "success": False,
                "error": report_result.get("error", "Failed to generate report"),
                "pdf_path": "",
                "json_path": "",
                "report_data": {}
            }
        
        # Step 3: Generate PDF and JSON
        final_result = await self._generate_pdf_and_json(config, report_result["blueprint"], learnings, sources, template)
        
        if final_result["success"]:
            print(f"✅ Report generation completed successfully!")
            print(f"📄 PDF: {final_result['pdf_path']}")
            print(f"📋 JSON: {final_result['json_path']}")
        
        return final_result

    def _export_to_pdf(self, config: ReportConfig, blueprint: Dict[str, Any], template: str = "template_1", learnings: Optional[List[str]] = None, sources: Optional[List[Dict[str, Any]]] = None) -> str:
        """Legacy method - kept for backward compatibility - Uses template_1 by default"""
        sanitized_title = re.sub(r'[\\/*?:"<>|]', "", config.title)
        reports_dir = os.getenv("REPORTS_OUTPUT_DIR", "generated_reports")
        filename = f"{reports_dir}/{sanitized_title[:50]}.pdf"
        
        # Ensure reports directory exists
        os.makedirs(reports_dir, exist_ok=True)
        
        # Prepare the data dictionary for Typst
        sections = blueprint.get("sections", []) or []
        
        template_path = f"templates/{template}.typ"
        
        # Adjust logo path to be relative to the template directory
        logo_path = ""
        if config.logo_path and os.path.exists(str(config.logo_path)):
            if config.logo_path.startswith("assets/"):
                logo_path = f"../{config.logo_path}"
            elif config.logo_path.startswith("templates/"):
                logo_path = os.path.basename(config.logo_path)
            elif os.path.isabs(config.logo_path):
                template_dir = os.path.dirname(template_path)
                logo_path = os.path.relpath(config.logo_path, template_dir)
            else:
                logo_path = f"../{config.logo_path}"
        
        report_data = {
            "title": config.title,
            "subtitle": config.subtitle,
            "author": config.author,
            "company": config.company,
            "logo_path": logo_path,
            "date": datetime.now().strftime('%B %d, %Y'),
            "sections": sections,
            "learnings": learnings or [],
            "sources": sources or []
        }
        
        # Get temp directory from environment
        temp_dir = os.getenv("TEMP_DIR", "temp_charts")
        
        # Adjust chart paths to be relative to the template directory
        for section in sections:
            if isinstance(section, dict):
                chart_path = section.get("chart_path")
                if chart_path and isinstance(chart_path, str) and chart_path != "":
                    if chart_path.startswith(f"{temp_dir}/"):
                        section["chart_path"] = f"../{chart_path}"
                    elif os.path.isabs(chart_path):
                        template_dir = os.path.dirname(template_path)
                        rel_path = os.path.relpath(chart_path, template_dir)
                        section["chart_path"] = rel_path
        
        success = render_to_pdf_with_typst(report_data, template_path, filename)
        
        if success:
            print(f"✅ Successfully generated final PDF: {filename}")
            return filename
        else:
            raise RuntimeError("Failed to generate PDF using Typst. Check the logs for details.")