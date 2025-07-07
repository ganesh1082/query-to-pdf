#!/usr/bin/env python3
"""
Firecrawl Integration - Connects real-time web research with report generation
Uses FIRECRAWL_API_URL from .env for direct URL access (no API key required)
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from firecrawl_research import FirecrawlResearch
from report_planner import ReportPlanner, ReportType
from enhanced_visualization_generator import PremiumVisualizationGenerator
from typst_renderer import render_to_pdf_with_typst
import traceback

# Load environment variables from .env file
load_dotenv()


class FirecrawlReportGenerator:
    """Generate reports using real-time web data from Firecrawl URL"""
    
    def __init__(self, gemini_api_key: str):
        """Initialize the report generator with Gemini API key only"""
        self.gemini_api_key = gemini_api_key
        
        # Initialize Firecrawl research (no API key needed)
        try:
            self.firecrawl_research = FirecrawlResearch(gemini_api_key)
            print("✅ Firecrawl research initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Firecrawl research: {e}")
            raise
        
        self.report_planner = ReportPlanner(gemini_api_key)
        
        # Brand colors for visualizations
        self.brand_colors = {
            "primary": "#0D203D",
            "secondary": "#666666", 
            "accent": "#4A90E2",
            "background": "#F7FAFC"
        }
        
        self.visualization_generator = PremiumVisualizationGenerator(self.brand_colors)
        
        # Use the Gemini model from firecrawl_research instead of creating a new one
        self.gemini_model = self.firecrawl_research.gemini_model
    
    async def generate_report_from_web_research(self, query: str, page_count: int = 8, 
                                               report_type: ReportType = ReportType.MARKET_RESEARCH,
                                               template: str = "template_1") -> Dict[str, Any]:
        """Generate a complete report using real-time web research"""
        print(f"🌐 Starting web research for: {query}")
        print(f"📊 Report configuration:")
        print(f"   - Page count: {page_count}")
        print(f"   - Report type: {report_type}")
        print(f"   - Template: {template}")
        
        # Check if Firecrawl URL is available
        firecrawl_url = os.getenv('FIRECRAWL_API_URL')
        if not firecrawl_url:
            print("❌ ERROR: FIRECRAWL_API_URL not configured")
            print("   Please set FIRECRAWL_API_URL in your .env file")
            return await self._fallback_report_generation(query, page_count, report_type, template)
        
        print(f"🌐 Using Firecrawl URL: {firecrawl_url}")
        
        # Run Firecrawl research
        try:
            print("🔍 Starting deep research...")
            research_result = await self.firecrawl_research.deep_research(query)
            
            learnings = research_result.get("learnings", [])
            source_metadata = research_result.get("source_metadata", [])
            requests_used = research_result.get("requests_used", 0)
            
            print(f"📈 Research completed:")
            print(f"   - Learnings found: {len(learnings)}")
            print(f"   - Sources found: {len(source_metadata)}")
            print(f"   - Requests used: {requests_used}")
            
            # Check if research was successful (found learnings and sources)
            if not learnings or not source_metadata:
                print(f"⚠️ Firecrawl research returned no learnings or sources, falling back to AI generation")
                return await self._fallback_report_generation(query, page_count, report_type, template)
            
            # Use ReportPlanner to generate the report blueprint using learnings and sources
            print("📋 Generating report blueprint...")
            blueprint = await self.report_planner.generate_report_blueprint(
                query, page_count, report_type, learnings=learnings, source_metadata=source_metadata
            )
            
            print("📊 Generating visualizations...")
            await self._generate_visualizations(blueprint)
            
            # Convert source metadata to the format expected by template
            sources = []
            for source in source_metadata:
                if isinstance(source, dict):
                    sources.append({
                        "url": source.get("url", ""),
                        "domain": source.get("domain", ""),
                        "reliability_score": source.get("reliability_score", 0.5),
                        "reliability_reasoning": source.get("reliability_reasoning", ""),
                        "title": source.get("title", ""),
                        "content_length": source.get("content_length", 0)
                    })
            
            # Generate PDF with learnings and sources
            print("📄 Generating PDF report...")
            pdf_path = await self._generate_pdf(blueprint, query, template, learnings, sources)
            
            return {
                "success": True,
                "pdf_path": pdf_path,
                "blueprint": blueprint,
                "method": "web_research",
                "requests_used": requests_used,
                "learnings_count": len(learnings),
                "sources_count": len(source_metadata),
                "learnings": learnings,
                "sources": sources
            }
        except Exception as e:
            print(f"❌ Web research failed: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            # Fallback to AI generation
            return await self._fallback_report_generation(query, page_count, report_type, template)
    
    def _progress_callback(self, progress):
        """Progress callback for research"""
        print(f"📊 Research Progress: {progress.completed_queries}/{progress.total_queries} queries completed")
    
    async def _generate_visualizations(self, blueprint: Dict[str, Any]) -> None:
        """Generate visualizations for the blueprint based on content"""
        print("📊 Generating visualizations based on content...")
        
        sections = blueprint.get("sections", [])
        
        for i, section in enumerate(sections):
            chart_type = section.get("chart_type", "none")
            chart_data = section.get("chart_data", {})
            content = section.get("content", "")
            
            # If no chart data but content exists, generate chart data based on content
            if chart_type != "none" and not chart_data and content:
                chart_data = await self._generate_chart_data_from_content(content, chart_type, section["title"])
                section["chart_data"] = chart_data
            
            if chart_type != "none" and chart_data:
                try:
                    chart_path = self.visualization_generator.create_chart({
                        "title": section["title"],
                        "chart_type": chart_type,
                        "chart_data": chart_data
                    })
                    # Fix chart path to be relative to templates/ directory
                    # The template is in templates/ directory, so we need to go up one level to reach temp_charts/
                    if chart_path.startswith("./temp_charts/"):
                        relative_chart_path = "../temp_charts/" + chart_path.split("/")[-1]
                    elif chart_path.startswith("temp_charts/"):
                        relative_chart_path = "../temp_charts/" + chart_path.split("/")[-1]
                    else:
                        relative_chart_path = "../" + chart_path
                    
                    section["chart_path"] = relative_chart_path
                    print(f"✅ Generated chart for section {i+1}: {chart_path}")
                except Exception as e:
                    print(f"❌ Failed to generate chart for section {i+1}: {e}")
                    section["chart_path"] = ""
    
    async def _generate_chart_data_from_content(self, content: str, chart_type: str, title: str) -> Dict[str, Any]:
        """Generate chart data based on content using Gemini"""
        if not self.gemini_model:
            return {}
        
        try:
            prompt = f"""Based on the following content, generate appropriate chart data for a {chart_type} chart.

Content: {content[:1000]}...

Title: {title}

Generate chart data in JSON format that matches the content. For example:
- If content mentions percentages, create pie/donut chart data
- If content mentions trends over time, create line chart data  
- If content mentions comparisons, create bar chart data
- If content mentions correlations, create scatter plot data

Return only valid JSON:
{{
  "labels": ["label1", "label2", "label3"],
  "values": [value1, value2, value3]
}}"""

            response = await self.gemini_model.generate_content_async(prompt)
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return {}
            
        except Exception as e:
            print(f"❌ Error generating chart data: {e}")
            return {}
    
    async def _generate_pdf(self, blueprint: Dict[str, Any], query: str, template: str = "template_1", learnings: Optional[List[str]] = None, sources: Optional[List[Dict[str, Any]]] = None) -> str:
        """Generate PDF using Typst"""
        print("📄 Generating PDF...")
        
        # Save blueprint to JSON with required fields for Typst template
        blueprint_path = "templates/report_data.json"
        
        # Add required fields for Typst template
        report_data = {
            "title": query,
            "subtitle": f"Research Report: {query}",
            "author": os.getenv("AUTHOR", "AI Research Assistant"),
            "company": os.getenv("ORGANIZATION", "Research Division"),
            "logo_path": "assets/logo.png",  # Relative to project root (--root argument)
            "date": datetime.now().strftime('%B %d, %Y'),
            "sections": blueprint.get("sections", []),
            "learnings": learnings or [],
            "sources": sources or []
        }
        
        with open(blueprint_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Generate PDF using template_2
        timestamp = int(time.time())
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_query = safe_query.replace(' ', '_')[:50]
        
        reports_dir = os.getenv("REPORTS_OUTPUT_DIR", "generated_reports")
        os.makedirs(reports_dir, exist_ok=True)
        output_filename = f"{reports_dir}/{timestamp:03d}_{safe_query}.pdf"
        
        try:
            # Use the render_to_pdf_with_typst function directly
            success = render_to_pdf_with_typst(
                report_data=report_data,
                template_path=f"templates/{template}.typ",
                output_path=output_filename
            )
            if success:
                print(f"✅ PDF generated: {output_filename}")
                return output_filename
            else:
                print(f"❌ PDF generation failed")
                return ""
        except Exception as e:
            print(f"❌ PDF generation failed: {e}")
            return ""
    
    async def _fallback_report_generation(self, query: str, page_count: int, report_type: ReportType, template: str) -> Dict[str, Any]:
        """Fallback to AI-generated content when web research fails"""
        print("🔄 Falling back to AI-generated content")
        
        # Use the existing report planner
        blueprint = await self.report_planner.generate_report_blueprint(query, page_count, report_type)
        
        if not blueprint:
            print("❌ Both web research and AI generation failed")
            return {"success": False, "error": "Failed to generate report"}
        
        # Generate visualizations
        await self._generate_visualizations(blueprint)
        
        # Generate PDF
        pdf_path = await self._generate_pdf(blueprint, query, template)
        
        return {
            "success": True,
            "pdf_path": pdf_path,
            "blueprint": blueprint,
            "method": "ai_generated",
            "credits_used": 0
        }


# Example usage
async def main():
    """Example usage of FirecrawlReportGenerator"""
    generator = FirecrawlReportGenerator(
        gemini_api_key="your_gemini_api_key_here"
    )
    
    result = await generator.generate_report_from_web_research(
        query="Tesla electric vehicle market analysis 2024",
        page_count=8,
        report_type=ReportType.MARKET_RESEARCH
    )
    
    if result["success"]:
        print(f"✅ Report generated successfully!")
        print(f"📄 PDF: {result['pdf_path']}")
        print(f"💳 Credits used: {result['requests_used']}")
        print(f"🔍 Method: {'web_research' if 'sources' in result else 'ai_generated'}")
    else:
        print(f"❌ Report generation failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main()) 