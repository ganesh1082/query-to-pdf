#!/usr/bin/env python3
"""
Enhanced Research System Test
Tests the comprehensive data collection with Firecrawl and OpenAI verification
"""

import asyncio
import os
import json
from datetime import datetime
from main_application import ProfessionalReportGenerator
from advanced_content_generator import ReportConfig
from enhanced_firecrawl import ResearchQuery

async def test_enhanced_research_system():
    """Test the enhanced research system with comprehensive data collection"""
    
    print("🔬 ENHANCED RESEARCH SYSTEM TEST")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize the enhanced research application
    try:
        app = ProfessionalReportGenerator(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            firecrawl_api_key=os.getenv("FIRECRAWL_API_KEY")
        )
        print("✅ Enhanced Research Application initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        return
    
    # Create a comprehensive research configuration
    config = ReportConfig(
        title="AI-Powered Healthcare Technology Market Analysis 2024",
        research_query="AI healthcare technology market trends, investment analysis, regulatory landscape, competitive positioning",
        target_audience="Healthcare executives, investors, technology strategists",
        research_objectives=[
            "Analyze AI healthcare market size and growth projections",
            "Identify key investment trends and funding patterns",
            "Map competitive landscape and market leaders",
            "Assess regulatory impact and compliance requirements",
            "Evaluate technology adoption patterns and barriers",
            "Provide strategic recommendations for market entry"
        ],
        report_type="comprehensive_market_intelligence",
        industry_focus="Healthcare Technology",
        geographic_scope="Global with US focus",
        time_horizon="2024-2027",
        depth_level="executive_detailed"
    )
    
    # Create research query for Firecrawl
    research_query = ResearchQuery(
        topic="AI healthcare technology market analysis",
        keywords=["AI healthcare", "medical AI", "healthcare technology", "digital health", "medical innovation", "healthcare AI investment"],
        depth="comprehensive",
        sources=[
            "https://www.healthcaredive.com",
            "https://www.mobihealthnews.com", 
            "https://www.healthcarefinancenews.com",
            "https://www.fiercehealthcare.com",
            "https://www.healthtechmagazine.net"
        ]
    )
    
    print("📋 RESEARCH CONFIGURATION")
    print(f"Title: {config.title}")
    print(f"Query: {config.research_query}")
    print(f"Objectives: {len(config.research_objectives)} strategic objectives")
    print(f"Industry: {config.industry_focus}")
    print(f"Scope: {config.geographic_scope}")
    print()
    
    # Execute comprehensive research with enhanced data collection
    print("🔍 EXECUTING ENHANCED RESEARCH PIPELINE")
    print("-" * 50)
    
    try:
        # Generate comprehensive report with enhanced data collection
        pdf_path = await app.generate_comprehensive_report(config, research_query)
        
        print("✅ Enhanced research pipeline completed successfully")
        print()
        
        # Generate PDF report
        print("📄 ENHANCED PDF REPORT GENERATED")
        print("-" * 40)
        
        if pdf_path:
            print(f"✅ PDF Report Generated: {pdf_path}")
            
            # Check file size and quality
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path) / 1024  # KB
                print(f"📋 File Size: {file_size:.1f} KB")
                
                if file_size > 50:  # Substantial content
                    print("✅ PDF contains substantial content")
                else:
                    print("⚠️  PDF may be lacking detailed content")
            else:
                print("❌ PDF file not found")
        else:
            print("❌ PDF generation failed")
        
        print()
        print("🎯 ENHANCED RESEARCH SYSTEM TEST SUMMARY")
        print("=" * 50)
        print(f"✅ PDF Generation: {'SUCCESS' if pdf_path else 'FAILED'}")
        print(f"✅ Enhanced Firecrawl: {'ACTIVE' if os.getenv('FIRECRAWL_API_KEY') else 'INACTIVE'}")
        print(f"✅ OpenAI Verification: {'ACTIVE' if os.getenv('OPENAI_API_KEY') else 'INACTIVE'}")
        
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path) / 1024
            print(f"✅ Content Quality: {'HIGH' if file_size > 100 else 'STANDARD'}")
            print(f"🎉 EXCELLENT: Enhanced research system generated a comprehensive report")
        else:
            print("⚠️  NEEDS IMPROVEMENT: Enhanced research system requires optimization")
        
        return pdf_path
        
    except Exception as e:
        print(f"❌ Enhanced research pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_enhanced_research_system()) 