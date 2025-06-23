"""
Professional Research Report Generator v2.0
Enhanced with AI, Advanced Analytics, and Enterprise Features
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from main_application import ProfessionalReportGenerator
from enhanced_firecrawl import ResearchQuery
from advanced_content_generator import ReportConfig, ReportType


def validate_environment():
    """Validate that all required environment variables are set"""
    required_vars = ['OPENAI_API_KEY', 'FIRECRAWL_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        return False
    
    return True


async def generate_research_report(query_text: str = None) -> str:
    """
    Generate a comprehensive research report based on the query
    Returns the path to the generated PDF file
    """
    
    # Validate environment
    if not validate_environment():
        raise Exception("Missing required environment variables")
    
    # Get API keys from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
    
    # Use provided query or default
    if not query_text:
        query_text = os.getenv("DEFAULT_REPORT_TITLE", "analyze the latest 5 publically available investments by anthill ventures and try to map their sector, intent focus")
    
    try:
        # Configure the report
        config = ReportConfig(
            title=query_text,
            subtitle=f"Comprehensive Analysis: {query_text}",
            author=os.getenv("DEFAULT_AUTHOR", "Ubik Research"),
            company=os.getenv("DEFAULT_COMPANY_NAME", "Ubik Research"),
            report_type=ReportType.MARKET_RESEARCH,
            research_objectives=[
                f"Analyze: {query_text}",
                "Provide comprehensive market intelligence",
                "Deliver actionable insights and recommendations"
            ],
            target_audience="C-suite executives, investors, and strategic decision makers",
            brand_colors={
                "primary": os.getenv("DEFAULT_BRAND_PRIMARY_COLOR", "#1f4e79"),
                "secondary": os.getenv("DEFAULT_BRAND_SECONDARY_COLOR", "#666666"),
                "accent": os.getenv("DEFAULT_BRAND_ACCENT_COLOR", "#e74c3c")
            },
            logo_path=os.getenv("COMPANY_LOGO_PATH")
        )
        
        # Configure the research query
        research_query = ResearchQuery(
            topic=query_text,
            keywords=[query_text, "market analysis", "investment trends", "sector analysis"],
            sources=[],  # Auto-discovered by the system
            depth="comprehensive",
            timeframe="past_12_months"
        )
        
        print(f"\n📊 Report Configuration:")
        print(f"   Title: {config.title}")
        print(f"   Type: {config.report_type.value}")
        print(f"   Author: {config.author}")
        print(f"   Company: {config.company}")
        
        print(f"\n🔍 Research Configuration:")
        print(f"   Topic: {research_query.topic}")
        print(f"   Keywords: {', '.join(research_query.keywords)}")
        print(f"   Depth: {research_query.depth}")
        print(f"   Timeframe: {research_query.timeframe}")
        
        # Initialize the professional report generator
        print(f"\n🤖 Initializing Professional Report Generator...")
        generator = ProfessionalReportGenerator(
            openai_api_key=openai_api_key,
            firecrawl_api_key=firecrawl_api_key
        )
        
        # Generate the comprehensive report
        print(f"\n🎯 Starting comprehensive report generation...")
        output_file = await generator.generate_comprehensive_report(config, research_query)
        
        return output_file
        
    except Exception as e:
        print(f"\n❌ Error during report generation: {str(e)}")
        raise


async def main():
    """Enhanced main function for professional report generation"""
    
    print("🚀 Professional Research Report Generator v2.0")
    print("=" * 50)
    
    try:
        # Generate the report
        output_file = await generate_research_report()
        
        # Success message
        print(f"\n" + "=" * 50)
        print(f"🎉 SUCCESS! Professional report generated successfully!")
        print(f"📁 Output File: {output_file}")
        
        # Additional information
        reports_dir = os.getenv("REPORTS_OUTPUT_DIR", "generated_reports")
        print(f"\n📋 Additional Information:")
        print(f"   Reports Directory: {reports_dir}")
        print(f"   Report Features: Executive Summary, Visualizations, AI Images, Professional PDF")
        print(f"   Research Quality: Enterprise-grade with source validation")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Review the generated PDF report")
        print(f"   2. Customize branding via environment variables")
        print(f"   3. Modify research topics in the configuration")
        print(f"   4. Share with stakeholders and decision makers")
        
        return output_file
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Report generation interrupted by user")
        return None
    
    except Exception as e:
        print(f"\n❌ Error during report generation:")
        print(f"   {str(e)}")
        print(f"\n🔧 Troubleshooting Tips:")
        print(f"   1. Check your internet connection")
        print(f"   2. Verify API keys are valid and have sufficient credits")
        print(f"   3. Ensure all dependencies are installed (run: pip install -r requirements.txt)")
        print(f"   4. Check the .env file configuration")
        
        # For debugging
        import traceback
        print(f"\n🔍 Technical Details:")
        print(traceback.format_exc())
        
        return None


# API-ready function for external use
async def api_generate_report(query: str) -> dict:
    """
    API-ready function to generate reports
    Returns a dictionary with status and file path
    """
    try:
        output_file = await generate_research_report(query)
        return {
            "status": "success",
            "message": "Report generated successfully",
            "output_file": output_file,
            "file_exists": os.path.exists(output_file) if output_file else False
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "output_file": None,
            "file_exists": False
        }


if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print(f"\n✅ Final output: {result}")
    else:
        print(f"\n❌ Report generation failed")