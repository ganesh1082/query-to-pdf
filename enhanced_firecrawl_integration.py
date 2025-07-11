#!/usr/bin/env python3
"""
Enhanced Firecrawl Integration - Connects real-time web research with report generation
Uses enhanced research capabilities with Gemini processing
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from enhanced_firecrawl_research import EnhancedFirecrawlResearch, ResearchProgress
from report_planner import ReportPlanner, ReportType
from enhanced_visualization_generator import PremiumVisualizationGenerator
from typst_renderer import render_to_pdf_with_typst
import traceback
import re

# Load environment variables from .env file
load_dotenv()


class EnhancedFirecrawlReportGenerator:
    """Generate reports using enhanced real-time web data from Firecrawl"""
    
    def __init__(self, gemini_api_key: str):
        """Initialize the enhanced report generator with Gemini API key"""
        self.gemini_api_key = gemini_api_key
        
        # Initialize enhanced Firecrawl research
        try:
            self.firecrawl_research = EnhancedFirecrawlResearch(gemini_api_key)
            print("✅ Enhanced Firecrawl research initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize enhanced Firecrawl research: {e}")
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
        
        # Use the Gemini model from firecrawl_research
        self.gemini_model = self.firecrawl_research.gemini_model
    
    async def collect_learnings_only(self, query: str) -> Dict[str, Any]:
        """Collect learnings from enhanced Firecrawl research"""
        print(f"🌐 Collecting enhanced learnings for: {query}")
        
        # Check if Firecrawl URL is available
        firecrawl_url = os.getenv('FIRECRAWL_API_URL')
        if not firecrawl_url:
            print("❌ ERROR: FIRECRAWL_API_URL not configured")
            return {
                "success": False,
                "error": "FIRECRAWL_API_URL not configured",
                "learnings": [],
                "sources": []
            }
        
        print(f"🌐 Using enhanced Firecrawl URL: {firecrawl_url}")
        
        # Run enhanced Firecrawl research
        try:
            print("🔍 Starting enhanced deep research...")
            
            def progress_callback(progress: ResearchProgress):
                print(f"📊 Research Progress: {progress.completed_queries}/{progress.total_queries} queries completed")
                if progress.current_query:
                    print(f"   Current: {progress.current_query}")
            
            research_result = await self.firecrawl_research.deep_research(
                query=query,
                breadth=4,  # Use enhanced breadth
                depth=2,    # Use enhanced depth
                on_progress=progress_callback
            )
            
            learnings = research_result.get("learnings", [])
            source_metadata = research_result.get("source_metadata", [])
            requests_used = research_result.get("requests_used", 0)
            comprehensive_report = research_result.get("comprehensive_report", "")
            
            print(f"📈 Enhanced research completed:")
            print(f"   - Learnings found: {len(learnings)}")
            print(f"   - Sources found: {len(source_metadata)}")
            print(f"   - Requests used: {requests_used}")
            print(f"   - Report generated: {len(comprehensive_report)} characters")
            
            # Check if research was successful
            if not learnings or not source_metadata:
                print(f"⚠️ Enhanced Firecrawl research returned no learnings or sources")
                return {
                    "success": False,
                    "error": "No learnings or sources found",
                    "learnings": [],
                    "sources": []
                }
            
            # Convert source metadata to the format expected by template
            sources = []
            for source in source_metadata:
                sources.append({
                    "url": source.url,
                    "domain": source.domain,
                    "reliability_score": source.reliability_score,
                    "reliability_reasoning": source.reliability_reasoning,
                    "title": source.title,
                    "content_length": source.content_length
                })
            
            return {
                "success": True,
                "learnings": learnings,
                "sources": sources,
                "requests_used": requests_used,
                "method": "enhanced_web_research",
                "comprehensive_report": comprehensive_report
            }
            
        except Exception as e:
            print(f"❌ Enhanced web research failed: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "learnings": [],
                "sources": []
            }
    
    async def generate_report_from_enhanced_research(self, query: str, page_count: int = 8, 
                                                   report_type: ReportType = ReportType.MARKET_RESEARCH,
                                                   template: str = "template_1") -> Dict[str, Any]:
        """Generate report using enhanced Firecrawl research"""
        print(f"🌐 Starting enhanced web research for: {query}")
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
        
        print(f"🌐 Using enhanced Firecrawl URL: {firecrawl_url}")
        
        # Run enhanced Firecrawl research
        try:
            print("🔍 Starting enhanced deep research...")
            
            def progress_callback(progress: ResearchProgress):
                print(f"📊 Research Progress: {progress.completed_queries}/{progress.total_queries} queries completed")
                if progress.current_query:
                    print(f"   Current: {progress.current_query}")
            
            research_result = await self.firecrawl_research.deep_research(
                query=query,
                breadth=4,  # Use enhanced breadth
                depth=2,    # Use enhanced depth
                on_progress=progress_callback
            )
            
            learnings = research_result.get("learnings", [])
            source_metadata = research_result.get("source_metadata", [])
            requests_used = research_result.get("requests_used", 0)
            comprehensive_report = research_result.get("comprehensive_report", "")
            
            print(f"📈 Enhanced research completed:")
            print(f"   - Learnings found: {len(learnings)}")
            print(f"   - Sources found: {len(source_metadata)}")
            print(f"   - Requests used: {requests_used}")
            print(f"   - Report generated: {len(comprehensive_report)} characters")
            
            # Check if research was successful
            if not learnings or not source_metadata:
                print(f"⚠️ Enhanced Firecrawl research returned no learnings or sources, falling back to AI generation")
                return await self._fallback_report_generation(query, page_count, report_type, template)
            
            # Use ReportPlanner to generate the report blueprint using learnings and sources
            print("📋 Generating report blueprint...")
            blueprint = await self.report_planner.generate_report_blueprint(
                query, page_count, report_type, learnings=learnings, source_metadata=source_metadata
            )
            
            # If we have a comprehensive report, use it as the main content
            if comprehensive_report:
                print("📝 Using comprehensive report as main content...")
                blueprint['sections'] = [
                    {
                        'title': 'Executive Summary',
                        'content': comprehensive_report[:2000] + "..." if len(comprehensive_report) > 2000 else comprehensive_report,
                        'type': 'text'
                    },
                    {
                        'title': 'Comprehensive Analysis',
                        'content': comprehensive_report,
                        'type': 'text'
                    }
                ]
            
            print("📊 Generating visualizations...")
            await self._generate_visualizations(blueprint)
            
            # Convert source metadata to the format expected by template
            sources = []
            for source in source_metadata:
                sources.append({
                    "url": source.url,
                    "domain": source.domain,
                    "reliability_score": source.reliability_score,
                    "reliability_reasoning": source.reliability_reasoning,
                    "title": source.title,
                    "content_length": source.content_length
                })
            
            # Generate PDF with learnings and sources
            print("📄 Generating PDF report...")
            pdf_path = await self._generate_pdf(blueprint, query, template, learnings, sources)
            
            return {
                "success": True,
                "pdf_path": pdf_path,
                "blueprint": blueprint,
                "method": "enhanced_web_research",
                "requests_used": requests_used,
                "learnings_count": len(learnings),
                "sources_count": len(source_metadata),
                "learnings": learnings,
                "sources": sources,
                "comprehensive_report": comprehensive_report
            }
            
        except Exception as e:
            print(f"❌ Enhanced web research failed: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            return await self._fallback_report_generation(query, page_count, report_type, template)
    
    def _progress_callback(self, progress):
        """Progress callback for research"""
        print(f"📊 Progress: {progress.completed_queries}/{progress.total_queries} queries completed")
    
    async def _generate_visualizations(self, blueprint: Dict[str, Any]) -> None:
        """Generate visualizations for the report"""
        try:
            sections = blueprint.get('sections', [])
            
            for section in sections:
                if section.get('type') == 'chart' and section.get('chart_data'):
                    print(f"📊 Generating chart: {section.get('title', 'Untitled')}")
                    
                    chart_data = section['chart_data']
                    chart_type = chart_data.get('type', 'bar')
                    title = section.get('title', 'Chart')
                    
                    # Generate chart using the visualization generator
                    chart_result = await self.visualization_generator.generate_chart(
                        chart_data=chart_data,
                        chart_type=chart_type,
                        title=title,
                        brand_colors=self.brand_colors
                    )
                    
                    if chart_result and chart_result.get('success'):
                        section['chart_path'] = chart_result.get('chart_path')
                        section['chart_data'] = chart_result.get('chart_data')
                        print(f"  ✅ Chart generated: {chart_result.get('chart_path')}")
                    else:
                        print(f"  ❌ Failed to generate chart: {chart_result.get('error', 'Unknown error')}")
                        
        except Exception as e:
            print(f"❌ Error generating visualizations: {e}")
    
    async def _generate_chart_data_from_content(self, content: str, chart_type: str, title: str, allowed_chart_types=None) -> Dict[str, Any]:
        """Generate chart data from content using Gemini"""
        try:
            if allowed_chart_types is None:
                allowed_chart_types = ['bar', 'line', 'pie', 'scatter']
            
            prompt = f"""Analyze the following content and generate chart data for a {chart_type} chart titled "{title}".

Content:
{content}

Generate appropriate chart data that would be useful for visualizing key information from this content. The chart should be informative and relevant to the content.

Provide your response in JSON format:
{{
    "type": "{chart_type}",
    "title": "{title}",
    "data": {{
        "labels": ["label1", "label2", ...],
        "datasets": [
            {{
                "label": "Dataset Name",
                "data": [value1, value2, ...],
                "backgroundColor": ["#color1", "#color2", ...]
            }}
        ]
    }},
    "options": {{
        "responsive": true,
        "plugins": {{
            "title": {{
                "display": true,
                "text": "{title}"
            }}
        }}
    }}
}}"""

            response = await self.gemini_model.generate_content_async(prompt)
            response_text = response.text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback chart data
                return {
                    "type": chart_type,
                    "title": title,
                    "data": {
                        "labels": ["Data Point 1", "Data Point 2", "Data Point 3"],
                        "datasets": [{
                            "label": "Values",
                            "data": [10, 20, 30],
                            "backgroundColor": ["#4A90E2", "#666666", "#0D203D"]
                        }]
                    }
                }
                
        except Exception as e:
            print(f"Error generating chart data: {e}")
            return None
    
    async def _generate_pdf(self, blueprint: Dict[str, Any], query: str, template: str = "template_1", 
                           learnings: Optional[List[str]] = None, sources: Optional[List[Dict[str, Any]]] = None) -> str:
        """Generate PDF report using Typst"""
        try:
            # Prepare template data
            template_data = {
                "title": query,
                "date": datetime.now().strftime("%B %d, %Y"),
                "company_name": os.getenv('COMPANY_NAME', 'Solarpunk'),
                "author": os.getenv('AUTHOR', 'Ubik'),
                "organization": os.getenv('ORGANIZATION', 'Ubik Research Division'),
                "sections": blueprint.get('sections', []),
                "learnings": learnings or [],
                "sources": sources or [],
                "logo_path": os.getenv('COMPANY_LOGO_PATH', 'assets/logo.png')
            }
            
            # Generate PDF
            output_dir = os.getenv('REPORTS_OUTPUT_DIR', './generated_reports')
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_report_{timestamp}.pdf"
            output_path = os.path.join(output_dir, filename)
            
            pdf_path = await render_to_pdf_with_typst(template_data, template, output_path)
            
            print(f"✅ PDF generated: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            return ""
    
    async def _fallback_report_generation(self, query: str, page_count: int, report_type: ReportType, template: str) -> Dict[str, Any]:
        """Fallback to AI-only report generation"""
        print("🔄 Falling back to AI-only report generation...")
        
        try:
            # Generate report blueprint without web research
            blueprint = await self.report_planner.generate_report_blueprint(
                query, page_count, report_type
            )
            
            print("📊 Generating visualizations...")
            await self._generate_visualizations(blueprint)
            
            # Generate PDF
            print("📄 Generating PDF report...")
            pdf_path = await self._generate_pdf(blueprint, query, template)
            
            return {
                "success": True,
                "pdf_path": pdf_path,
                "blueprint": blueprint,
                "method": "ai_only",
                "requests_used": 0,
                "learnings_count": 0,
                "sources_count": 0,
                "learnings": [],
                "sources": []
            }
            
        except Exception as e:
            print(f"❌ Fallback report generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "failed"
            }


async def main():
    """Test the enhanced Firecrawl integration"""
    try:
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
            return
        
        generator = EnhancedFirecrawlReportGenerator(gemini_api_key)
        
        # Test collecting learnings only
        print("🧪 Testing enhanced learnings collection...")
        learnings_result = await generator.collect_learnings_only("artificial intelligence trends 2024")
        
        if learnings_result['success']:
            print(f"✅ Learnings collected successfully!")
            print(f"   - Learnings: {len(learnings_result['learnings'])}")
            print(f"   - Sources: {len(learnings_result['sources'])}")
            print(f"   - Method: {learnings_result['method']}")
            
            # Test full report generation
            print("\n🧪 Testing enhanced report generation...")
            report_result = await generator.generate_report_from_enhanced_research(
                "artificial intelligence trends 2024",
                page_count=6,
                report_type=ReportType.MARKET_RESEARCH
            )
            
            if report_result['success']:
                print(f"✅ Report generated successfully!")
                print(f"   - PDF: {report_result['pdf_path']}")
                print(f"   - Method: {report_result['method']}")
                print(f"   - Requests used: {report_result['requests_used']}")
            else:
                print(f"❌ Report generation failed: {report_result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Learnings collection failed: {learnings_result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 