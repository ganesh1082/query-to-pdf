#!/usr/bin/env python3
"""
WebSocket-Ready Main Application
Enhanced version with real-time progress updates for future websocket integration
"""

import os
import re
import json
import time
from typing import Dict, Any, Optional, List, Callable
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

class ProgressCallback:
    """Progress callback interface for websocket integration"""
    
    def __init__(self, websocket_callback: Optional[Callable] = None):
        self.websocket_callback = websocket_callback
        self.start_time = datetime.now()
    
    async def update_progress(self, stage: str, message: str, progress: float = 0.0, data: Optional[Dict] = None):
        """Update progress and send to websocket if available"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        progress_data = {
            "stage": stage,
            "message": message,
            "progress": progress,
            "elapsed_seconds": elapsed,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        # Print to console
        print(f"🔄 [{stage}] {message} ({progress:.1f}%) - {elapsed:.1f}s")
        
        # Send to websocket if available
        if self.websocket_callback:
            try:
                await self.websocket_callback(progress_data)
            except Exception as e:
                print(f"⚠️ WebSocket callback failed: {e}")

class WebSocketReadyReportGenerator:
    """WebSocket-ready report generator with real-time progress updates"""

    def __init__(self, gemini_api_key: str, websocket_callback: Optional[Callable] = None):
        self.report_planner = ReportPlanner(api_key=gemini_api_key)
        self.data_visualizer = PremiumVisualizationGenerator(brand_colors={"primary": "#0D203D", "accent": "#4A90E2"})
        self.progress_callback = ProgressCallback(websocket_callback)
        
        # Initialize Firecrawl generator
        self.firecrawl_generator: Optional[FirecrawlReportGenerator] = None
        try:
            self.firecrawl_generator = FirecrawlReportGenerator(gemini_api_key)
            print("✅ Firecrawl generator initialized successfully")
        except Exception as e:
            print(f"⚠️ Firecrawl generator initialization failed: {e}")
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
        """Step 1: Collect learnings from Firecrawl URL with progress updates"""
        await self.progress_callback.update_progress(
            "research", 
            "Starting web research...", 
            5.0
        )
        
        if not self.firecrawl_generator:
            await self.progress_callback.update_progress(
                "research", 
                "Firecrawl generator not available", 
                100.0,
                {"error": "Firecrawl generator not available"}
            )
            return {"learnings": [], "sources": [], "success": False}
        
        try:
            await self.progress_callback.update_progress(
                "research", 
                "Collecting learnings from web sources...", 
                15.0
            )
            
            research_result = await self.firecrawl_generator.firecrawl_research.deep_research(query)
            
            learnings = research_result.get("learnings", [])
            sources = research_result.get("source_metadata", [])
            
            await self.progress_callback.update_progress(
                "research", 
                f"Research completed: {len(learnings)} learnings from {len(sources)} sources", 
                50.0,
                {
                    "learnings_count": len(learnings),
                    "sources_count": len(sources),
                    "requests_used": research_result.get("requests_used", 0)
                }
            )
            
            # Check if we have meaningful learnings
            if not learnings or len(learnings) == 0:
                await self.progress_callback.update_progress(
                    "research", 
                    "No learnings found from Firecrawl", 
                    100.0,
                    {"error": "No learnings found"}
                )
                return {"learnings": [], "sources": [], "success": False}
            
            # Filter out learnings that are empty or just whitespace
            filtered_learnings = [learning for learning in learnings if learning and learning.strip()]
            
            if not filtered_learnings:
                await self.progress_callback.update_progress(
                    "research", 
                    "All learnings were empty or invalid", 
                    100.0,
                    {"error": "All learnings were empty"}
                )
                return {"learnings": [], "sources": [], "success": False}
            
            await self.progress_callback.update_progress(
                "research", 
                f"Successfully collected {len(filtered_learnings)} valid learnings", 
                100.0,
                {
                    "learnings_count": len(filtered_learnings),
                    "sources_count": len(sources),
                    "requests_used": research_result.get("requests_used", 0)
                }
            )
            
            return {
                "learnings": filtered_learnings,
                "sources": sources,
                "success": True,
                "requests_used": research_result.get("requests_used", 0)
            }
            
        except Exception as e:
            await self.progress_callback.update_progress(
                "research", 
                f"Error collecting learnings: {e}", 
                100.0,
                {"error": str(e)}
            )
            return {"learnings": [], "sources": [], "success": False}

    async def _generate_report_from_learnings(self, query: str, learnings: List[str], sources: List[Dict], page_count: int, template: str) -> Dict[str, Any]:
        """Step 2: Use learnings with Gemini to generate titles, descriptions, and charts"""
        await self.progress_callback.update_progress(
            "planning", 
            "Generating report blueprint from learnings...", 
            60.0
        )
        
        if not learnings:
            await self.progress_callback.update_progress(
                "planning", 
                "No learnings available for report generation", 
                100.0,
                {"error": "No learnings available"}
            )
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
                await self.progress_callback.update_progress(
                    "planning", 
                    "Failed to generate report blueprint from learnings", 
                    100.0,
                    {"error": "Failed to generate blueprint"}
                )
                return {"success": False, "error": "Failed to generate blueprint"}
            
            await self.progress_callback.update_progress(
                "planning", 
                f"Blueprint generated with {len(blueprint.get('sections', []))} sections", 
                75.0,
                {"sections_count": len(blueprint.get('sections', []))}
            )
            
            # Get template-specific colors and update the visualizer
            template_colors = self._get_template_colors(template)
            self.data_visualizer = PremiumVisualizationGenerator(brand_colors=template_colors)
            
            await self.progress_callback.update_progress(
                "visualization", 
                "Generating visualizations from learnings...", 
                80.0
            )
            
            sections = blueprint.get("sections", [])
            for i, section in enumerate(sections):
                # Convert content to Typst format
                if "content" in section:
                    section["content"] = self._convert_content_to_typst(section["content"])

                chart_type = section.get("chart_type")
                if chart_type and chart_type != "none":
                    progress = 80 + (i / len(sections)) * 15  # 80-95%
                    await self.progress_callback.update_progress(
                        "visualization", 
                        f"Generating '{chart_type}' chart for: {section['title']}", 
                        progress
                    )
                    try:
                        # Use the PDF-specific chart creation method
                        chart_path = self.data_visualizer.create_chart_for_pdf(section)
                        section["chart_path"] = chart_path
                    except Exception as e:
                        print(f"  ⚠️ Error generating chart for '{section['title']}': {e}")
                        section["chart_path"] = ""
                else:
                    section["chart_path"] = ""
            
            await self.progress_callback.update_progress(
                "visualization", 
                "All visualizations generated successfully", 
                95.0
            )
            
            return {
                "success": True,
                "blueprint": blueprint
            }
            
        except Exception as e:
            await self.progress_callback.update_progress(
                "planning", 
                f"Error generating report from learnings: {e}", 
                100.0,
                {"error": str(e)}
            )
            return {"success": False, "error": str(e)}

    async def _generate_pdf_and_json(self, config: ReportConfig, blueprint: Dict[str, Any], learnings: List[str], sources: List[Dict], template: str) -> Dict[str, Any]:
        """Step 3: Generate PDF and create JSON with all data including PDF path"""
        await self.progress_callback.update_progress(
            "pdf_generation", 
            "Generating PDF and JSON...", 
            95.0
        )
        
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
                await self.progress_callback.update_progress(
                    "pdf_generation", 
                    "Failed to generate PDF using Typst", 
                    100.0,
                    {"error": "PDF generation failed"}
                )
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
            
            await self.progress_callback.update_progress(
                "complete", 
                "Report generation completed successfully!", 
                100.0,
                {
                    "pdf_path": pdf_filename,
                    "json_path": json_filename,
                    "sections_count": len(blueprint.get("sections", [])),
                    "learnings_count": len(learnings),
                    "sources_count": len(sources)
                }
            )
            
            return {
                "success": True,
                "pdf_path": pdf_filename,
                "json_path": json_filename,
                "report_data": json_data
            }
            
        except Exception as e:
            await self.progress_callback.update_progress(
                "pdf_generation", 
                f"Error generating PDF and JSON: {e}", 
                100.0,
                {"error": str(e)}
            )
            return {"success": False, "error": str(e)}

    async def generate_comprehensive_report(self, config: ReportConfig, query: str, page_count: int, template: str = "template_1", use_web_research: bool = True) -> Dict[str, Any]:
        """Main method following the new workflow with real-time progress updates"""
        await self.progress_callback.update_progress(
            "start", 
            f"Starting comprehensive report generation for: {query}", 
            0.0,
            {
                "query": query,
                "page_count": page_count,
                "template": template,
                "use_web_research": use_web_research
            }
        )
        
        # Step 1: Collect learnings from Firecrawl
        if use_web_research:
            firecrawl_result = await self._collect_learnings_from_firecrawl(query)
            
            if not firecrawl_result["success"]:
                await self.progress_callback.update_progress(
                    "error", 
                    "Could not find useful/trustworthy data on internet", 
                    100.0,
                    {"error": "No useful data found"}
                )
                return {
                    "success": False,
                    "error": "Could not find useful/trustworthy data on internet",
                    "pdf_path": "",
                    "json_path": "",
                    "report_data": {}
                }
            
            learnings = firecrawl_result["learnings"]
            sources = firecrawl_result["sources"]
            
            # Check for halfway point with 0 learnings
            halfway_point = len(learnings) // 2
            if halfway_point > 0:
                # Check if learnings after halfway are 0 or empty
                later_learnings = learnings[halfway_point:]
                if all(not learning or learning.strip() == "" for learning in later_learnings):
                    await self.progress_callback.update_progress(
                        "research", 
                        f"Found 0 learnings after halfway point, using first {halfway_point} learnings", 
                        50.0
                    )
                    learnings = learnings[:halfway_point]
                    # Also filter sources accordingly if needed
                    sources = sources[:halfway_point] if len(sources) > halfway_point else sources
        else:
            # Fallback to AI generation without web research
            await self.progress_callback.update_progress(
                "research", 
                "Web research disabled, using AI generation only", 
                50.0
            )
            learnings = []
            sources = []
        
        # Step 2: Generate report from learnings using Gemini
        report_result = await self._generate_report_from_learnings(query, learnings, sources, page_count, template)
        
        if not report_result["success"]:
            await self.progress_callback.update_progress(
                "error", 
                "Failed to generate report from learnings", 
                100.0,
                {"error": report_result.get("error", "Failed to generate report")}
            )
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
            await self.progress_callback.update_progress(
                "complete", 
                "Report generation completed successfully!", 
                100.0,
                {
                    "pdf_path": final_result['pdf_path'],
                    "json_path": final_result['json_path'],
                    "sections_count": len(report_result["blueprint"].get("sections", [])),
                    "learnings_count": len(learnings),
                    "sources_count": len(sources)
                }
            )
        
        return final_result

# Example usage for testing
async def test_websocket_ready_generator():
    """Test the websocket-ready generator"""
    
    # Mock websocket callback
    async def mock_websocket_callback(progress_data):
        print(f"📡 WebSocket: {progress_data['stage']} - {progress_data['message']} ({progress_data['progress']:.1f}%)")
    
    # Initialize generator
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    generator = WebSocketReadyReportGenerator(gemini_api_key, mock_websocket_callback)
    
    # Create test config
    config = ReportConfig(
        title="WebSocket Test Report",
        subtitle="Testing real-time progress updates",
        author="Test User",
        company="Test Company",
        report_type=ReportType.MARKET_RESEARCH,
        target_audience="Test audience",
        logo_path="assets/logo.png"
    )
    
    # Generate report
    result = await generator.generate_comprehensive_report(
        config=config,
        query="Tesla electric vehicle market analysis 2024",
        page_count=8,
        template="template_1",
        use_web_research=True
    )
    
    print(f"\n✅ Test completed: {result.get('success', False)}")
    if result.get('success'):
        print(f"📄 PDF: {result.get('pdf_path')}")
        print(f"📋 JSON: {result.get('json_path')}")

if __name__ == "__main__":
    asyncio.run(test_websocket_ready_generator()) 