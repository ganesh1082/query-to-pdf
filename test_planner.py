#!/usr/bin/env python3
"""
Test script for the improved Report Planner
"""

import asyncio
import os
from dotenv import load_dotenv
from report_planner import ReportPlanner, ReportType

async def test_planner():
    """Test the report planner with different scenarios."""
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    print("🧪 Testing Report Planner")
    print("=" * 50)
    
    # Initialize planner
    planner = ReportPlanner(api_key=api_key)
    
    # Test queries
    test_cases = [
        {
            "query": "Tesla electric vehicle market analysis",
            "pages": 8,
            "type": ReportType.COMPANY_ANALYSIS
        },
        {
            "query": "Global renewable energy market trends",
            "pages": 10,
            "type": ReportType.MARKET_RESEARCH
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['query']}")
        print("-" * 40)
        
        try:
            # Generate blueprint
            blueprint = await planner.generate_report_blueprint(
                query=test_case["query"],  # type: ignore
                page_count=test_case["pages"],  # type: ignore
                report_type=test_case["type"]  # type: ignore
            )
            
            if blueprint and "sections" in blueprint:
                print(f"✅ Successfully generated blueprint with {len(blueprint['sections'])} sections")
                
                # Show section details
                for j, section in enumerate(blueprint["sections"], 1):
                    print(f"  {j}. {section['title']} ({section['chart_type']})")
                    
                    # Show chart data if present
                    if section['chart_type'] != 'none' and section['chart_data']:
                        chart_data = section['chart_data']
                        if 'labels' in chart_data and 'values' in chart_data:
                            print(f"     Chart: {len(chart_data['labels'])} data points")
                        elif 'series' in chart_data:
                            print(f"     Chart: {len(chart_data['series'])} series")
            else:
                print("❌ Failed to generate valid blueprint")
                
        except Exception as e:
            print(f"❌ Error in test case {i}: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_planner()) 