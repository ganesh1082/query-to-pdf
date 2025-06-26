#!/usr/bin/env python3
"""
Test script for Typst template validation
"""

import json
import os
import subprocess
from typing import Dict, Any

def create_test_data() -> Dict[str, Any]:
    """Create test data for the template"""
    return {
        "title": "Test Market Research Report",
        "subtitle": "Comprehensive Analysis and Strategic Insights",
        "author": "Research Team",
        "company": "Market Intelligence Corp",
        "date": "December 2024",
        "logo_path": "",
        "sections": [
            {
                "title": "Executive Summary",
                "content": "This is a **test report** with some content.\n\n- Point 1\n- Point 2\n- Point 3",
                "chart_type": "none",
                "chart_path": ""
            },
            {
                "title": "Market Overview",
                "content": "The market shows **strong growth** in several key areas.\n\n- Growth drivers\n- Market size\n- Key players",
                "chart_type": "bar",
                "chart_path": "temp_charts/test_chart.png"
            }
        ]
    }

def test_typst_installation():
    """Test if Typst is installed"""
    try:
        result = subprocess.run(["typst", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Typst is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Typst command failed")
            return False
    except FileNotFoundError:
        print("❌ Typst not found in PATH")
        return False

def test_template_syntax():
    """Test the template syntax"""
    try:
        # Create test data
        test_data = create_test_data()
        
        # Write test data to JSON
        with open("test_report_data.json", "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print("✅ Test data created: test_report_data.json")
        
        # Test Typst compilation
        if test_typst_installation():
            command = ["typst", "compile", "report_template.typ", "test_output.pdf"]
            print(f"🚀 Running: {' '.join(command)}")
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Template compilation successful!")
                print("📄 Generated: test_output.pdf")
                return True
            else:
                print("❌ Template compilation failed:")
                print(f"STDERR: {result.stderr}")
                return False
        else:
            print("⚠️ Skipping compilation test - Typst not installed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing template: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists("test_report_data.json"):
            os.remove("test_report_data.json")

def create_alternative_solution():
    """Create an alternative solution using a different PDF library"""
    print("\n🔧 Creating alternative PDF solution...")
    
    # Create a simple HTML-based PDF generator as fallback
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{title}}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2cm; }
        h1 { color: #1a365d; border-bottom: 2px solid #3182ce; }
        h2 { color: #2d3748; }
        .cover { text-align: center; page-break-after: always; }
        .toc { page-break-after: always; }
        .section { page-break-before: always; }
        img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <div class="cover">
        <h1>{{title}}</h1>
        <h2>{{subtitle}}</h2>
        <p><strong>Author:</strong> {{author}}</p>
        <p><strong>Company:</strong> {{company}}</p>
        <p><strong>Date:</strong> {{date}}</p>
    </div>
    
    <div class="toc">
        <h1>Table of Contents</h1>
        {% for section in sections %}
        <p>{{loop.index}}. {{section.title}}</p>
        {% endfor %}
    </div>
    
    {% for section in sections %}
    <div class="section">
        <h1>{{section.title}}</h1>
        <div>{{section.content | safe}}</div>
        {% if section.chart_path %}
        <figure>
            <img src="{{section.chart_path}}" alt="Chart for {{section.title}}">
            <figcaption>Visualization for: {{section.title}}</figcaption>
        </figure>
        {% endif %}
    </div>
    {% endfor %}
</body>
</html>
"""
    
    with open("alternative_template.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print("✅ Created alternative HTML template: alternative_template.html")
    print("💡 You can use this with a tool like wkhtmltopdf or weasyprint")

if __name__ == "__main__":
    print("🧪 Testing Typst Template")
    print("=" * 50)
    
    # Test Typst installation
    typst_available = test_typst_installation()
    
    # Test template syntax
    template_works = test_template_syntax()
    
    # Create alternative solution
    create_alternative_solution()
    
    print("\n📋 Summary:")
    print(f"Typst Available: {'✅' if typst_available else '❌'}")
    print(f"Template Works: {'✅' if template_works else '❌'}")
    
    if not typst_available:
        print("\n💡 To install Typst, you can:")
        print("1. Use Homebrew: brew install typst")
        print("2. Download from: https://github.com/typst/typst/releases")
        print("3. Use the alternative HTML template provided") 