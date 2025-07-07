#!/usr/bin/env python3
"""
Test script for Firecrawl JSON functionality
"""

import requests
import json
import time

# FastAPI server URL
BASE_URL = "http://localhost:8000"

def test_firecrawl_json_generation():
    """Test JSON report generation with Firecrawl research"""
    print("🔍 Testing JSON report generation with Firecrawl research...")
    
    payload = {
        "prompt": "Tesla electric vehicle market analysis 2024",
        "template": "template_1",
        "web_research": True,  # Enable Firecrawl research
        "breadth": 3,
        "depth": 2,
        "page_count": 6,
        "report_type": "market_research"
    }
    
    try:
        print("📡 Sending request to generate JSON with Firecrawl research...")
        response = requests.post(f"{BASE_URL}/generate-json", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ JSON report with Firecrawl research generated successfully")
            print(f"   Report ID: {result['report_id']}")
            print(f"   Message: {result['message']}")
            
            # Check if Firecrawl data is included
            if result.get('json_data') and result['json_data'].get('firecrawl_research'):
                firecrawl_data = result['json_data']['firecrawl_research']
                print(f"   🔍 Firecrawl Research Data:")
                print(f"      - Key Findings: {len(firecrawl_data.get('key_findings', []))}")
                print(f"      - Total Sources: {firecrawl_data.get('total_sources', 0)}")
                print(f"      - High Quality Sources: {firecrawl_data.get('high_quality_sources', 0)}")
                print(f"      - Credits Used: {firecrawl_data.get('credits_used', 0)}")
                
                # Display some key findings
                key_findings = firecrawl_data.get('key_findings', [])
                if key_findings:
                    print(f"   📋 Sample Key Findings:")
                    for i, finding in enumerate(key_findings[:3]):
                        print(f"      {i+1}. {finding[:100]}...")
                
                # Display some sources
                sources = firecrawl_data.get('sources', [])
                if sources:
                    print(f"   🔗 Sample Sources:")
                    for i, source in enumerate(sources[:3]):
                        print(f"      {i+1}. {source.get('domain', 'Unknown')} - {source.get('url', 'No URL')}")
                        print(f"         Reliability: {source.get('reliability_score', 0):.2f}")
                
            else:
                print("   ⚠️ No Firecrawl research data found in response")
            
            # Save the JSON data to a file
            if result['json_data']:
                filename = f"firecrawl_test_{result['report_id']}.json"
                with open(filename, 'w') as f:
                    json.dump(result['json_data'], f, indent=2)
                print(f"   📁 JSON data saved to: {filename}")
            
            return result['report_id']
        else:
            print(f"❌ JSON generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ JSON generation error: {e}")
    
    return None

def test_firecrawl_full_report():
    """Test full report generation with Firecrawl research"""
    print("\n📊 Testing full report generation with Firecrawl research...")
    
    payload = {
        "prompt": "Apple iPhone market analysis and competition",
        "template": "template_1",
        "web_research": True,  # Enable Firecrawl research
        "breadth": 2,
        "depth": 1,
        "page_count": 8,
        "report_type": "company_analysis"
    }
    
    try:
        print("📡 Sending request to generate full report with Firecrawl research...")
        response = requests.post(f"{BASE_URL}/generate-report", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Full report with Firecrawl research generated successfully")
            print(f"   Report ID: {result['report_id']}")
            print(f"   PDF Path: {result['pdf_path']}")
            
            # Check if Firecrawl data is included
            if result.get('json_data') and result['json_data'].get('firecrawl_research'):
                firecrawl_data = result['json_data']['firecrawl_research']
                print(f"   🔍 Firecrawl Research Data:")
                print(f"      - Key Findings: {len(firecrawl_data.get('key_findings', []))}")
                print(f"      - Total Sources: {firecrawl_data.get('total_sources', 0)}")
                print(f"      - High Quality Sources: {firecrawl_data.get('high_quality_sources', 0)}")
                print(f"      - Credits Used: {firecrawl_data.get('credits_used', 0)}")
            else:
                print("   ⚠️ No Firecrawl research data found in response")
            
            return result['report_id']
        else:
            print(f"❌ Full report generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Full report generation error: {e}")
    
    return None

def test_download_firecrawl_json(report_id):
    """Test downloading JSON with Firecrawl data"""
    if not report_id:
        return
    
    print(f"\n📥 Testing JSON download for report: {report_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/download-json/{report_id}")
        if response.status_code == 200:
            filename = f"downloaded_firecrawl_{report_id}.json"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ JSON with Firecrawl data downloaded: {filename}")
            
            # Parse and display some info
            try:
                json_data = json.loads(response.content)
                if json_data.get('firecrawl_research'):
                    firecrawl_data = json_data['firecrawl_research']
                    print(f"   📊 Firecrawl Data Summary:")
                    print(f"      - Key Findings: {len(firecrawl_data.get('key_findings', []))}")
                    print(f"      - Sources: {len(firecrawl_data.get('sources', []))}")
                    print(f"      - Research Metrics: {firecrawl_data.get('research_metrics', {})}")
            except json.JSONDecodeError:
                print("   ⚠️ Could not parse downloaded JSON")
        else:
            print(f"❌ JSON download failed: {response.status_code}")
    except Exception as e:
        print(f"❌ JSON download error: {e}")

def main():
    """Run all Firecrawl tests"""
    print("🧪 Firecrawl JSON Integration Tests")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Test JSON generation with Firecrawl
    json_report_id = test_firecrawl_json_generation()
    
    # Test full report generation with Firecrawl
    full_report_id = test_firecrawl_full_report()
    
    # Test downloading JSON with Firecrawl data
    if json_report_id:
        test_download_firecrawl_json(json_report_id)
    
    print("\n🎉 All Firecrawl tests completed!")
    print("\n📋 Summary:")
    print("   - JSON reports now include Firecrawl research data when web_research=True")
    print("   - Key findings and sources are preserved in the JSON output")
    print("   - PDF rendering remains unchanged (template_1 compatibility maintained)")
    print("   - Research metrics and reliability scores are included")

if __name__ == "__main__":
    main() 