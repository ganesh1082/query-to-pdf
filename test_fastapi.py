#!/usr/bin/env python3
"""
Test script for FastAPI endpoints
"""

import requests
import json
import time

# FastAPI server URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Status: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_generate_json():
    """Test JSON report generation"""
    print("\n📄 Testing JSON report generation...")
    
    payload = {
        "prompt": "Tesla electric vehicle market analysis",
        "template": "template_1",
        "web_research": False,
        "page_count": 6,
        "report_type": "market_research"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-json", json=payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ JSON report generated successfully")
            print(f"   Report ID: {result['report_id']}")
            print(f"   Message: {result['message']}")
            print(f"   Timestamp: {result['timestamp']}")
            
            # Save the JSON data to a file
            if result['json_data']:
                filename = f"test_report_{result['report_id']}.json"
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

def test_generate_full_report():
    """Test full report generation (JSON + PDF)"""
    print("\n📊 Testing full report generation...")
    
    payload = {
        "prompt": "Apple company analysis and market position",
        "template": "template_2",
        "web_research": False,
        "page_count": 8,
        "report_type": "company_analysis"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-report", json=payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ Full report generated successfully")
            print(f"   Report ID: {result['report_id']}")
            print(f"   PDF Path: {result['pdf_path']}")
            print(f"   Message: {result['message']}")
            print(f"   Timestamp: {result['timestamp']}")
            
            return result['report_id']
        else:
            print(f"❌ Full report generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Full report generation error: {e}")
    
    return None

def test_download_files(report_id):
    """Test downloading generated files"""
    if not report_id:
        return
    
    print(f"\n📥 Testing file downloads for report: {report_id}")
    
    # Test PDF download
    try:
        response = requests.get(f"{BASE_URL}/download-pdf/{report_id}")
        if response.status_code == 200:
            filename = f"downloaded_{report_id}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ PDF downloaded: {filename}")
        else:
            print(f"❌ PDF download failed: {response.status_code}")
    except Exception as e:
        print(f"❌ PDF download error: {e}")
    
    # Test JSON download
    try:
        response = requests.get(f"{BASE_URL}/download-json/{report_id}")
        if response.status_code == 200:
            filename = f"downloaded_{report_id}.json"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ JSON downloaded: {filename}")
        else:
            print(f"❌ JSON download failed: {response.status_code}")
    except Exception as e:
        print(f"❌ JSON download error: {e}")

def test_list_reports():
    """Test listing all reports"""
    print("\n📋 Testing report listing...")
    
    try:
        response = requests.get(f"{BASE_URL}/reports")
        if response.status_code == 200:
            result = response.json()
            print("✅ Reports listed successfully")
            print(f"   PDF Reports: {len(result['pdf_reports'])}")
            print(f"   JSON Reports: {len(result['json_reports'])}")
            
            if result['pdf_reports']:
                print("   Recent PDF reports:")
                for report in result['pdf_reports'][:3]:
                    print(f"     - {report['filename']} ({report['created']})")
            
            if result['json_reports']:
                print("   Recent JSON reports:")
                for report in result['json_reports'][:3]:
                    print(f"     - {report['filename']} ({report['created']})")
        else:
            print(f"❌ Report listing failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Report listing error: {e}")

def main():
    """Run all tests"""
    print("🧪 FastAPI Endpoint Tests")
    print("=" * 40)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Test health endpoint
    test_health()
    
    # Test JSON generation
    json_report_id = test_generate_json()
    
    # Test full report generation
    full_report_id = test_generate_full_report()
    
    # Test file downloads
    if full_report_id:
        test_download_files(full_report_id)
    
    # Test listing reports
    test_list_reports()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main() 