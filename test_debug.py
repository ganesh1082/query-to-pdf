#!/usr/bin/env python3
"""
Debug script to test the generate_report_blueprint method
"""

import asyncio
import os
from dotenv import load_dotenv
from report_planner import ReportPlanner, ReportType

async def test_generate_blueprint():
    """Test the generate_report_blueprint method"""
    load_dotenv()
    
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    print("🔧 Testing generate_report_blueprint...")
    
    try:
        planner = ReportPlanner(api_key=gemini_api_key)
        
        # Test with correct parameters
        print("📝 Testing with correct parameters...")
        result = await planner.generate_report_blueprint(
            query="Tesla electric vehicle market analysis",
            page_count=8,
            report_type=ReportType.MARKET_RESEARCH
        )
        
        if result:
            print("✅ Success! Generated blueprint:")
            print(f"  - Sections: {len(result.get('sections', []))}")
            for i, section in enumerate(result.get('sections', [])[:3]):
                print(f"  - Section {i+1}: {section.get('title', 'No title')}")
        else:
            print("❌ Failed to generate blueprint")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_generate_blueprint()) 