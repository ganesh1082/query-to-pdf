import asyncio
import os
from typing import Dict, Any
from datetime import datetime
import traceback

from enhanced_firecrawl import AdvancedFirecrawlClient, ResearchQuery
from advanced_content_generator import AdvancedContentGenerator, ReportConfig, ReportType
from enhanced_data_visualization import EnhancedDataVisualizer
from professional_pdf_styling import PremiumPDFGenerator, PremiumReportStyling

class ProfessionalReportGenerator:
    """Main orchestrator for professional report generation"""
    
    def __init__(self, openai_api_key: str, firecrawl_api_key: str):
        self.openai_api_key = openai_api_key
        self.firecrawl_api_key = firecrawl_api_key
        
        # Default brand colors
        default_brand_colors = {
            "primary": "#1f4e79",
            "secondary": "#666666", 
            "accent": "#e74c3c"
        }
        
        # Initialize components with enhanced capabilities
        self.content_generator = AdvancedContentGenerator(api_key=openai_api_key)
        self.data_visualizer = EnhancedDataVisualizer(
            brand_colors=default_brand_colors,
            chart_style=os.getenv("CHART_STYLE", "plotly_white")
        )
        
        # Enhanced styling with premium features
        self.styling = PremiumReportStyling(brand_colors=default_brand_colors)
        # Initialize PDF generator without config initially - will be set during generation
        self.pdf_generator = None
        
    async def generate_comprehensive_report(self, config: ReportConfig, query: ResearchQuery) -> str:
        """Generate comprehensive professional report"""
        
        try:
            print(f"\n📋 Phase 1: Initializing Premium Report Generation...")
            
            # Phase 1: Research Pipeline
            print(f"🔍 Phase 2: Executing Research Pipeline...")
            research_data = await self._execute_research_pipeline(query)
            
            # Phase 2: Content Generation
            print(f"🤖 Phase 3: Generating AI-Powered Content...")
            content_data = await self._generate_ai_content(config, research_data)
            
            # Phase 3: Data Visualization
            print(f"📊 Phase 4: Creating Premium Data Visualizations...")
            visualizations = await self._create_data_visualizations(research_data)
            
            # Phase 4: AI Image Generation
            print(f"🎨 Phase 5: Generating AI Images...")
            images = await self._generate_ai_images(config, content_data)
            
            # Phase 5: Premium PDF Generation
            print(f"📄 Phase 6: Compiling Premium Professional PDF...")
            pdf_filename = await self._generate_premium_pdf(config, content_data, images, visualizations)
            
            return pdf_filename
            
        except Exception as e:
            print(f"❌ Error in report generation: {e}")
            raise
    
    async def _execute_research_pipeline(self, query: ResearchQuery) -> Dict[str, Any]:
        """Execute the advanced research pipeline"""
        
        print("  🔍 Discovering authoritative sources...")
        async with AdvancedFirecrawlClient(api_key=self.firecrawl_api_key, openai_api_key=self.openai_api_key) as client:
            research_results = await client.intelligent_research_pipeline(query)
        
        # Enhance with additional analysis
        research_results["research_metadata"] = {
            "execution_time": datetime.now().isoformat(),
            "query_parameters": {
                "topic": query.topic,
                "keywords": query.keywords,
                "depth": query.depth,
                "source_count": len(query.sources) if query.sources else 0
            },
            "pipeline_version": "2.0.0"
        }
        
        print(f"  ✅ Research completed - {len(research_results.get('validated_data', []))} sources analyzed")
        return research_results
    
    async def _generate_ai_content(self, config: ReportConfig, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report content using AI"""
        
        print("  🧠 Generating executive summary...")
        print("  📝 Creating methodology section...")
        print("  💡 Analyzing key findings...")
        print("  🔬 Developing detailed analysis...")
        print("  💼 Formulating strategic recommendations...")
        print("  📋 Compiling appendices...")
        
        report_content = await self.content_generator.generate_comprehensive_report(research_data, config)
        
        # Add metadata and quality metrics
        report_content["generation_metadata"] = {
            "ai_model": "gpt-4",
            "generation_time": datetime.now().isoformat(),
            "content_quality_score": self._calculate_content_quality_score(report_content),
            "word_count": self._calculate_word_count(report_content)
        }
        
        print(f"  ✅ Content generation completed - {report_content['generation_metadata']['word_count']} words")
        return report_content
    
    async def _create_data_visualizations(self, research_data: Dict[str, Any]) -> Dict[str, str]:
        """Create comprehensive data visualizations based on actual research data"""
        
        # Use default brand colors if not in research_data
        brand_colors = {
            "primary": "#1a365d",
            "secondary": "#2d3748", 
            "accent": "#3182ce"
        }
        
        visualizer = EnhancedDataVisualizer(
            brand_colors=brand_colors,
            chart_style=os.getenv("CHART_STYLE", "plotly_white")
        )
        
        # Prepare comprehensive research data for visualizations
        viz_data = self._prepare_visualization_data(research_data)
        
        # Create dynamic visualizations based on actual data
        visualizations = {}
        
        try:
            # Executive dashboard with real data
            print("  📊 Creating executive dashboard...")
            visualizations["executive_dashboard"] = visualizer.create_executive_dashboard(viz_data)
            
            # Only create other visualizations if we have relevant data
            if viz_data.get("trend_data"):
                print("  📈 Creating trend analysis...")
                visualizations["trend_analysis"] = visualizer.create_trend_analysis_chart(viz_data["trend_data"])
            
            if viz_data.get("quality_metrics"):
                print("  📊 Creating quality metrics...")
                visualizations["quality_metrics"] = visualizer.create_quality_metrics_chart(viz_data["quality_metrics"])
            
            if viz_data.get("findings_data"):
                print("  💡 Creating findings summary...")
                visualizations["findings_summary"] = visualizer.create_findings_summary_chart(viz_data["findings_data"])
            
            if viz_data.get("source_analysis"):
                print("  📊 Creating source distribution...")
                visualizations["source_distribution"] = visualizer.create_source_distribution_chart(viz_data["source_analysis"])
            
            if viz_data.get("competitive_data"):
                print("  🏢 Creating competitive landscape...")
                visualizations["competitive_landscape"] = visualizer.create_competitive_landscape_chart(viz_data["competitive_data"])
                
        except Exception as e:
            print(f"  ⚠️ Error creating visualizations: {e}")
            # Fallback to basic dashboard only
            visualizations["executive_dashboard"] = visualizer.create_executive_dashboard(viz_data)
        
        print(f"  📈 Created {len(visualizations)} dynamic visualizations")
        return visualizations
    
    def _prepare_visualization_data(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare comprehensive data for dynamic visualizations"""
        
        validated_data = research_data.get("validated_data", [])
        query_info = research_data.get("research_metadata", {}).get("query_parameters", {})
        
        # Extract real findings from the research data
        all_findings = []
        investment_data = []
        competitive_info = []
        source_categories = {}
        
        for source in validated_data:
            # Collect key findings
            findings = source.get("key_findings", [])
            all_findings.extend(findings)
            
            # Extract investment data if present
            if source.get("investment_data"):
                investment_data.extend(source["investment_data"])
            
            # Extract competitive data
            if source.get("competitive_data"):
                competitive_info.append(source["competitive_data"])
            
            # Categorize sources
            category = source.get("source_metadata", {}).get("category", "unknown")
            source_categories[category] = source_categories.get(category, 0) + 1
        
        # Create trend data from investment amounts over time if available
        trend_data = {}
        if investment_data:
            for investment in investment_data:
                date = investment.get("date", "2024")
                amount_str = investment.get("amount", "$0M")
                try:
                    # Extract numeric value from amount string like "$1.2M"
                    amount = float(amount_str.replace("$", "").replace("M", "").replace("K", ""))
                    if "K" in amount_str:
                        amount = amount / 1000  # Convert K to M
                    trend_data[date] = trend_data.get(date, 0) + amount
                except:
                    continue
        
        # Extract quality metrics from actual sources
        quality_metrics = {}
        if validated_data:
            # Calculate real quality metrics
            quality_scores = [source.get("quality_score", 0.7) for source in validated_data]
            quality_metrics = {
                "average_quality": sum(quality_scores) / len(quality_scores),
                "high_quality_sources": len([s for s in quality_scores if s > 0.8]),
                "total_sources": len(validated_data),
                "real_sources": len([s for s in validated_data if s.get("source_metadata", {}).get("discovery_method") == "web_scraping"]),
                "ai_sources": len([s for s in validated_data if s.get("source_metadata", {}).get("discovery_method") == "ai_generation"])
            }
        
        # Prepare findings data for visualization
        findings_data = {}
        if all_findings:
            # Count key themes in findings
            theme_counts = {}
            keywords = ["investment", "growth", "market", "technology", "funding", "startup", "venture"]
            
            for finding in all_findings:
                for keyword in keywords:
                    if keyword.lower() in finding.lower():
                        theme_counts[keyword] = theme_counts.get(keyword, 0) + 1
            
            findings_data = {
                "themes": theme_counts,
                "total_findings": len(all_findings),
                "key_insights": all_findings[:5]  # Top 5 findings
            }
        
        # Prepare competitive data
        competitive_data = {}
        if competitive_info:
            competitors = {}
            for comp in competitive_info:
                name = comp.get("competitor", "Unknown")
                amount = comp.get("total_investments", "$0M")
                competitors[name] = amount
            competitive_data = {"competitors": competitors}
        
        return {
            "validated_data": validated_data,
            "query": {"topic": query_info.get("topic", "Research Analysis")},
            "trend_data": trend_data,
            "quality_metrics": quality_metrics,
            "findings_data": findings_data,
            "source_analysis": {"categories": source_categories},
            "competitive_data": competitive_data,
            "investment_data": investment_data
        }
    
    async def _generate_ai_images(self, config: ReportConfig, content: Dict[str, Any]) -> Dict[str, str]:
        """Generate comprehensive AI images for the report sections"""
        
        images = {}
        image_prompts = []
        
        try:
            print("  🎨 Phase 5: Generating AI Images")
            print("     Creating comprehensive visual assets...")
            
            # Define professional image prompts for different sections
            image_prompts = [
                {
                    "key": "cover",
                    "prompt": f"Professional business report cover design for '{config.title}', modern corporate aesthetic, clean minimalist layout with abstract business graphics, premium quality, professional color scheme"
                },
                {
                    "key": "executive_concept", 
                    "prompt": f"Executive strategic overview illustration, professional business concept art, C-suite presentation style, modern corporate graphics, data-driven insights visualization"
                },
                {
                    "key": "methodology_concept",
                    "prompt": f"Research methodology framework illustration, professional analytical process diagram, scientific approach visualization, clean business graphics style"
                },
                {
                    "key": "market_overview",
                    "prompt": f"Market landscape overview illustration, business ecosystem visualization, industry dynamics representation, professional infographic style"
                },
                {
                    "key": "key_findings",
                    "prompt": f"Key findings and insights illustration, data analysis results visualization, professional research outcomes, business intelligence graphics"
                },
                {
                    "key": "detailed_analysis",
                    "prompt": f"Detailed market analysis illustration, comprehensive data visualization, analytical framework representation, professional business graphics"
                },
                {
                    "key": "competitive_landscape",
                    "prompt": f"Competitive landscape analysis illustration, market positioning visualization, competitive dynamics representation, strategic business graphics"
                },
                {
                    "key": "industry_trends",
                    "prompt": f"Industry trends and transformation illustration, future outlook visualization, technological advancement graphics, professional trend analysis"
                },
                {
                    "key": "strategic_recommendations",
                    "prompt": f"Strategic recommendations illustration, implementation framework visualization, business strategy graphics, executive decision-making support"
                },
                {
                    "key": "risk_assessment",
                    "prompt": f"Risk assessment and mitigation illustration, risk management framework visualization, strategic risk analysis graphics, professional business planning"
                }
            ]
            
            # Generate images with progress tracking
            successful_images = 0
            for i, image_config in enumerate(image_prompts):
                try:
                    print(f"     🖼️ Creating {image_config['key']} image ({i+1}/{len(image_prompts)})...")
                    
                    # Generate the image
                    image_base64 = await self.content_generator.generate_report_image(image_config["prompt"])
                    
                    if image_base64:
                        images[image_config["key"]] = image_base64
                        successful_images += 1
                        print(f"     ✅ {image_config['key']} image generated successfully")
                    else:
                        print(f"     ⚠️ Failed to generate {image_config['key']} image")
                    
                    # Small delay to avoid rate limiting
                    import asyncio
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    print(f"     ❌ Error generating {image_config['key']} image: {str(e)}")
                    continue
            
            print(f"  ✅ AI image generation completed - {successful_images}/{len(image_prompts)} images created")
            
            # If we have fewer than 3 images, try to generate some basic ones
            if successful_images < 3:
                print("     🔄 Attempting to generate fallback images...")
                fallback_prompts = [
                    {"key": "cover", "prompt": "Simple professional business report cover, clean corporate design"},
                    {"key": "executive_concept", "prompt": "Professional business concept illustration, executive summary visual"},
                    {"key": "key_findings", "prompt": "Business analysis results illustration, professional data visualization"}
                ]
                
                for fallback in fallback_prompts:
                    if fallback["key"] not in images:
                        try:
                            fallback_image = await self.content_generator.generate_report_image(fallback["prompt"])
                            if fallback_image:
                                images[fallback["key"]] = fallback_image
                                successful_images += 1
                                print(f"     ✅ Fallback {fallback['key']} image generated")
                        except:
                            continue
            
        except Exception as e:
            print(f"  ⚠️ AI image generation encountered errors: {str(e)}")
            # Continue without images - PDF will use placeholders
            
        return images
    
    async def _generate_premium_pdf(self, config: ReportConfig, content: Dict[str, Any], images: Dict[str, str], visualizations: Dict[str, str]) -> str:
        """Generate premium PDF report"""
        
        try:
            # Initialize PDF generator with the actual config
            if not self.pdf_generator:
                self.pdf_generator = PremiumPDFGenerator(config=config, styling=self.styling)
            
            # Generate premium PDF
            pdf_filename = self.pdf_generator.generate_complete_pdf(content, images, visualizations)
            
            print(f"✅ Premium PDF generated: {pdf_filename}")
            return pdf_filename
            
        except Exception as e:
            print(f"❌ Error generating premium PDF: {e}")
            raise
    
    def _calculate_content_quality_score(self, content: Dict[str, Any]) -> float:
        """Calculate content quality score based on completeness and depth"""
        
        score = 0.0
        total_sections = 6  # executive_summary, methodology, key_findings, etc.
        
        # Check section completeness
        required_sections = ["executive_summary", "methodology", "key_findings", 
                           "detailed_analysis", "recommendations", "appendices"]
        
        for section in required_sections:
            if section in content and content[section].get("content"):
                score += 1.0 / total_sections
        
        # Adjust for content depth
        avg_length = sum(len(content[section].get("content", "")) for section in required_sections if section in content) / len(required_sections)
        if avg_length > 1000:
            score += 0.1  # Bonus for detailed content
        
        return min(score, 1.0)
    
    def _calculate_word_count(self, content: Dict[str, Any]) -> int:
        """Calculate total word count across all sections"""
        
        total_words = 0
        for section_data in content.values():
            if isinstance(section_data, dict) and "content" in section_data:
                total_words += len(section_data["content"].split())
        
        return total_words

async def main():
    """Main application entry point"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
    
    if not openai_api_key or not firecrawl_api_key:
        print("❌ Error: Missing required API keys")
        print("Please set OPENAI_API_KEY and FIRECRAWL_API_KEY in your .env file")
        return
    
    # Create report configuration
    config = ReportConfig(
        title=os.getenv("DEFAULT_REPORT_TITLE", "Professional Market Research Report"),
        subtitle=os.getenv("DEFAULT_REPORT_SUBTITLE", "Comprehensive Market Analysis and Strategic Insights"),
        author=os.getenv("DEFAULT_AUTHOR", "Research Team"),
        company=os.getenv("DEFAULT_COMPANY_NAME", "Professional Analytics"),
        report_type=ReportType.MARKET_RESEARCH,
        research_objectives=[
            "Analyze current market trends and dynamics",
            "Identify key growth opportunities",
            "Assess competitive landscape",
            "Provide strategic recommendations"
        ],
        target_audience="Executive leadership and strategic decision makers",
        brand_colors={
            "primary": os.getenv("DEFAULT_BRAND_PRIMARY_COLOR", "#1f4e79"),
            "secondary": os.getenv("DEFAULT_BRAND_SECONDARY_COLOR", "#666666"),
            "accent": os.getenv("DEFAULT_BRAND_ACCENT_COLOR", "#e74c3c")
        },
        logo_path=os.getenv("COMPANY_LOGO_PATH")
    )
    
    # Create research query
    research_query = ResearchQuery(
        topic=os.getenv("DEFAULT_RESEARCH_TOPIC", "Artificial Intelligence market trends and adoption"),
        keywords=["AI market", "machine learning adoption", "enterprise AI", "technology trends"],
        sources=[],  # Will be auto-discovered
        depth="comprehensive",
        timeframe="past_12_months"
    )
    
    # Initialize report generator
    generator = ProfessionalReportGenerator(
        openai_api_key=openai_api_key,
        firecrawl_api_key=firecrawl_api_key
    )
    
    try:
        # Generate the report
        output_file = await generator.generate_comprehensive_report(config, research_query)
        
        print(f"\n🎉 Report generation successful!")
        print(f"📁 File location: {output_file}")
        print(f"📊 Report type: {config.report_type.value}")
        print(f"👤 Author: {config.author}")
        print(f"🏢 Company: {config.company}")
        
    except Exception as e:
        print(f"\n💥 Report generation failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 