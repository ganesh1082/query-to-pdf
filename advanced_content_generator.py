# query_to_pdf/advanced_content_generator.py

import os
import json
from typing import Dict, Any, Optional
from enum import Enum
import google.generativeai as genai
import re

class ReportType(Enum):
    MARKET_RESEARCH = "market_research"

class ReportConfig:
    def __init__(self, title: str, subtitle: str, author: str, company: str, report_type: ReportType, target_audience: str, brand_colors: Dict[str, str], logo_path: Optional[str] = None):
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.company = company
        self.report_type = report_type
        self.target_audience = target_audience
        self.brand_colors = brand_colors
        self.logo_path = logo_path

class AdvancedContentGenerator:
    """An AI-driven generator that creates a unified blueprint for an entire report."""
    
    def __init__(self, api_key: Optional[str]):
        self.model: Optional[Any] = None
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception as e:
                print(f"⚠️ Could not configure Gemini. Error: {e}")
                self.model = None

    async def generate_full_report_blueprint(self, query: str, page_count: int) -> Optional[Dict[str, Any]]:
        """Generates a complete report blueprint including titles, chart data, and narrative content."""
        if not self.model:
            print("  ⚠️ Gemini not available. Using mock data.")
            return self._get_mock_report_blueprint(query)

        num_sections = max(8, min(14, int(page_count / 1.5)))

        prompt = f"""
You are a professional market research analyst. Create a comprehensive {page_count}-page report on: "{query}"

CRITICAL INSTRUCTIONS:
1. Output ONLY valid JSON wrapped in ```json ... ``` blocks
2. Do not include any text before or after the JSON
3. Ensure all JSON is properly formatted with correct commas and quotes
4. Use exactly {num_sections} sections

REQUIRED JSON STRUCTURE:
{{
  "sections": [
    {{
      "title": "Executive Summary",
      "content": "250-400 words of detailed analysis...",
      "chart_type": "none",
      "chart_data": {{}}
    }},
    {{
      "title": "Section Title",
      "content": "250-400 words of detailed analysis...",
      "chart_type": "bar",
      "chart_data": {{"labels": ["A", "B", "C"], "values": [10, 20, 30]}}
    }}
  ]
}}

SECTION REQUIREMENTS:
- First section: "Executive Summary" (chart_type: "none")
- Last two sections: "Strategic Recommendations" and "Risk Assessment" (chart_type: "none")
- Each section: 250-400 words using Typst markdown (**bold** for headings, `-` for bullets)
- Use diverse chart types: "bar", "line", "pie", "donut", "scatter", "horizontalBar", "none"

CHART DATA FORMATS (copy exactly):
- Single series: {{"labels": ["A", "B", "C"], "values": [10, 20, 30]}}
- Multi-series line: {{"labels": ["2020", "2021", "2022"], "series": [{{"name": "Series1", "values": [10, 15, 20]}}, {{"name": "Series2", "values": [5, 12, 18]}}]}}
- Scatter: {{"points": [{{"x": 1, "y": 2, "name": "P1"}}, {{"x": 3, "y": 4, "name": "P2"}}]}}
- Empty: {{}}

JSON VALIDATION RULES:
- Every object must end with }}
- Every array must end with ]
- Every property must be followed by a comma except the last one
- All strings must be in double quotes
- No trailing commas before }} or ]

OUTPUT FORMAT:
```json
{{YOUR_JSON_HERE}}
```
"""
        
        try:
            print(f"  🧠 Generating full {num_sections}-section report blueprint with Gemini...")
            print(f"  🔍 Using API key: {self.model.api_key[:10]}..." if hasattr(self.model, 'api_key') else "  🔍 API key configured")
            
            generation_config = genai.types.GenerationConfig(temperature=0.6, max_output_tokens=8192)
            response = await self.model.generate_content_async(prompt, generation_config=generation_config)
            
            print(f"  🔍 AI Response received, length: {len(response.text)} characters")
            print(f"  🔍 Response preview: {response.text[:200]}...")
            
            # Multiple strategies to extract JSON from the response
            json_data = self._extract_json_from_response(response.text)
            if json_data:
                print("  ✅ Successfully generated and parsed full report blueprint.")
                print(f"  🔍 Found {len(json_data.get('sections', []))} sections")
                return json_data
            else:
                print("❌ Could not extract valid JSON from AI response. Using mock data.")
                print("  🔍 This indicates the AI response format was not as expected.")
                return self._get_mock_report_blueprint(query)
                
        except Exception as e:
            print(f"❌ Error generating full report blueprint: {e}")
            print(f"  🔍 Error type: {type(e).__name__}")
            # Only try to access response.text if response exists
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"  ⚠️ Raw AI response was:\n---\n{response.text[:500]}...\n---")
            else:
                print("  ⚠️ No response object available")
            return self._get_mock_report_blueprint(query)

    def _repair_json(self, json_str: str) -> str:
        """Attempts to repair common JSON formatting issues."""
        try:
            # Try to parse as-is first
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            pass
        
        # Fix common issues
        repaired = json_str
        
        # Fix missing commas between objects in arrays
        repaired = re.sub(r'}\s*{', '},{', repaired)
        
        # Fix missing commas between properties
        repaired = re.sub(r'"\s*\n\s*"', '",\n"', repaired)
        
        # Fix trailing commas
        repaired = re.sub(r',\s*}', '}', repaired)
        repaired = re.sub(r',\s*]', ']', repaired)
        
        # Fix missing quotes around property names
        repaired = re.sub(r'(\w+):', r'"\1":', repaired)
        
        # Fix unescaped quotes in content
        repaired = re.sub(r'(?<!\\)"(?=.*":)', r'\\"', repaired)
        
        return repaired

    def _extract_json_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Robustly extract JSON from AI response using multiple strategies."""
        if not response_text:
            print("  🔍 No response text to parse")
            return None
            
        print(f"  🔍 Attempting to extract JSON from {len(response_text)} character response")
        
        # Clean the response text first - remove invalid control characters
        cleaned_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', response_text)
        
        # Strategy 1: Look for ```json ... ``` blocks
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", cleaned_text, re.DOTALL)
        if json_match:
            try:
                json_str = json_match.group(1)
                print("  🔍 Strategy 1: Found ```json ... ``` block")
                # Try to repair the JSON
                repaired_json = self._repair_json(json_str)
                result = json.loads(repaired_json)
                print("  ✅ Strategy 1: JSON parsed successfully after repair")
                return result
            except json.JSONDecodeError as e:
                print(f"  ❌ Strategy 1: JSON decode error: {e}")
        
        # Strategy 2: Look for ``` ... ``` blocks (without json specifier)
        json_match = re.search(r"```\s*(\{.*?\})\s*```", cleaned_text, re.DOTALL)
        if json_match:
            try:
                json_str = json_match.group(1)
                print("  🔍 Strategy 2: Found ``` ... ``` block")
                # Try to repair the JSON
                repaired_json = self._repair_json(json_str)
                result = json.loads(repaired_json)
                print("  ✅ Strategy 2: JSON parsed successfully after repair")
                return result
            except json.JSONDecodeError as e:
                print(f"  ❌ Strategy 2: JSON decode error: {e}")
        
        # Strategy 3: Look for JSON object at the beginning or end
        json_match = re.search(r"(\{[^{}]*\{(?:[^{}]|{[^{}]*})*[^{}]*\})", cleaned_text, re.DOTALL)
        if json_match:
            try:
                json_str = json_match.group(1)
                print("  🔍 Strategy 3: Found JSON object with regex")
                # Try to repair the JSON
                repaired_json = self._repair_json(json_str)
                result = json.loads(repaired_json)
                print("  ✅ Strategy 3: JSON parsed successfully after repair")
                return result
            except json.JSONDecodeError as e:
                print(f"  ❌ Strategy 3: JSON decode error: {e}")
        
        # Strategy 4: Try to find and fix common JSON issues
        # Look for the start of what might be JSON
        start_match = re.search(r"(\{[^{}]*\"sections\"\s*:)", cleaned_text, re.DOTALL)
        if start_match:
            start_pos = start_match.start()
            print("  🔍 Strategy 4: Found 'sections' key, attempting to extract JSON")
            # Try to find a reasonable end point
            brace_count = 0
            end_pos = start_pos
            for i, char in enumerate(cleaned_text[start_pos:], start_pos):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break
            
            if end_pos > start_pos:
                try:
                    json_str = cleaned_text[start_pos:end_pos]
                    # Clean up common issues
                    json_str = re.sub(r'[^\x20-\x7E\n\r\t]', '', json_str)  # Remove non-printable chars
                    json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                    json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                    # Try to repair the JSON
                    repaired_json = self._repair_json(json_str)
                    result = json.loads(repaired_json)
                    print("  ✅ Strategy 4: JSON parsed successfully after cleanup and repair")
                    return result
                except json.JSONDecodeError as e:
                    print(f"  ❌ Strategy 4: JSON decode error after cleanup: {e}")
        
        # Strategy 5: Try to find any JSON-like structure
        print("  🔍 Strategy 5: Looking for any JSON-like structure")
        # Look for opening and closing braces
        brace_start = cleaned_text.find('{')
        brace_end = cleaned_text.rfind('}')
        
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            try:
                json_str = cleaned_text[brace_start:brace_end + 1]
                # Try to clean it up
                json_str = re.sub(r'[^\x20-\x7E\n\r\t]', '', json_str)
                # Try to repair the JSON
                repaired_json = self._repair_json(json_str)
                result = json.loads(repaired_json)
                print("  ✅ Strategy 5: JSON parsed successfully from brace matching and repair")
                return result
            except json.JSONDecodeError as e:
                print(f"  ❌ Strategy 5: JSON decode error: {e}")
        
        print("  ❌ All JSON extraction strategies failed")
        return None

    def _get_mock_report_blueprint(self, query: str = "general topic") -> Dict[str, Any]:
        """Provides a complete fallback blueprint with all content if the AI fails."""
        print("  📝 Using mock report blueprint as a fallback.")
        
        # Generate dynamic content based on the query
        query_lower = query.lower()
        
        if "google" in query_lower or "alphabet" in query_lower:
            return {
                "sections": [
                    {"title": "Executive Summary", "content": "**Overview:** This report provides a comprehensive analysis of Google (Alphabet Inc.), one of the world's leading technology companies. Founded in 1998, Google has evolved from a search engine to a global technology conglomerate with diverse business interests.", "chart_type": "none", "chart_data": {}},
                    {"title": "Revenue Breakdown by Segment", "content": "**Financial Analysis:** Google's revenue is primarily driven by advertising, with Google Search and YouTube being the major contributors. Google Cloud and other ventures represent growing segments of the business.", "chart_type": "pie", "chart_data": {"labels": ["Search Advertising", "Network Advertising", "Google Cloud", "Other"], "values": [55, 15, 15, 15]}},
                    {"title": "Market Share in Digital Advertising", "content": "**Competitive Position:** Google dominates the digital advertising market alongside Meta, controlling a significant portion of global ad spend through its search and display networks.", "chart_type": "bar", "chart_data": {"labels": ["Google", "Meta", "Amazon", "Others"], "values": [28, 20, 11, 41]}},
                    {"title": "Strategic Recommendations", "content": "**Future Outlook:** Google should continue investing in AI and cloud services while addressing regulatory challenges and maintaining its competitive edge in search and advertising.", "chart_type": "none", "chart_data": {}},
                ]
            }
        elif "meta" in query_lower or "facebook" in query_lower:
            return {
                "sections": [
                    {"title": "Executive Summary", "content": "**Overview:** Meta Platforms Inc. is a global technology company focused on connecting people through social media platforms. The company has evolved from Facebook to include Instagram, WhatsApp, and metaverse initiatives.", "chart_type": "none", "chart_data": {}},
                    {"title": "User Base by Platform", "content": "**Platform Analysis:** Meta's ecosystem includes multiple platforms with billions of users worldwide, creating a comprehensive social media network.", "chart_type": "pie", "chart_data": {"labels": ["Facebook", "Instagram", "WhatsApp", "Messenger"], "values": [35, 25, 25, 15]}},
                    {"title": "Advertising Revenue Trends", "content": "**Financial Performance:** Meta's advertising revenue has shown strong growth, driven by targeted advertising capabilities and expanding user engagement.", "chart_type": "line", "chart_data": {"labels": ["2019", "2020", "2021", "2022", "2023"], "values": [70, 84, 115, 113, 132]}},
                    {"title": "Strategic Recommendations", "content": "**Future Strategy:** Meta should focus on metaverse development, AI integration, and addressing privacy concerns while maintaining platform engagement.", "chart_type": "none", "chart_data": {}},
                ]
            }
        elif "apple" in query_lower:
            return {
                "sections": [
                    {"title": "Executive Summary", "content": "**Overview:** Apple Inc. is a global technology leader known for its innovative hardware, software, and services. The company has built a premium brand ecosystem with strong customer loyalty.", "chart_type": "none", "chart_data": {}},
                    {"title": "Revenue by Product Category", "content": "**Product Analysis:** Apple's revenue is diversified across hardware, services, and accessories, with iPhone remaining the primary revenue driver.", "chart_type": "pie", "chart_data": {"labels": ["iPhone", "Mac", "iPad", "Services", "Other"], "values": [52, 10, 8, 20, 10]}},
                    {"title": "Global Market Share", "content": "**Competitive Position:** Apple maintains a strong position in premium smartphone and computer markets, with significant market share in key regions.", "chart_type": "bar", "chart_data": {"labels": ["Smartphones", "Tablets", "Laptops", "Smartwatches"], "values": [18, 35, 8, 30]}},
                    {"title": "Strategic Recommendations", "content": "**Growth Strategy:** Apple should continue innovating in services, expanding in emerging markets, and developing new product categories.", "chart_type": "none", "chart_data": {}},
                ]
            }
        else:
            # Generic fallback for other topics
            return {
                "sections": [
                    {"title": "Executive Summary", "content": f"**Overview:** This report provides a comprehensive analysis of {query}. The analysis covers key aspects including market trends, competitive landscape, and strategic implications.", "chart_type": "none", "chart_data": {}},
                    {"title": "Market Analysis", "content": "**Market Overview:** The market shows diverse trends with multiple players competing for market share. Understanding these dynamics is crucial for strategic decision-making.", "chart_type": "bar", "chart_data": {"labels": ["Segment A", "Segment B", "Segment C", "Segment D"], "values": [30, 25, 20, 25]}},
                    {"title": "Trend Analysis", "content": "**Growth Trends:** Recent years have shown consistent growth patterns with some seasonal variations. Future projections indicate continued expansion.", "chart_type": "line", "chart_data": {"labels": ["2020", "2021", "2022", "2023", "2024"], "values": [100, 115, 130, 145, 160]}},
                    {"title": "Strategic Recommendations", "content": "**Action Items:** Based on the analysis, key recommendations include market expansion, technology investment, and strategic partnerships.", "chart_type": "none", "chart_data": {}},
                ]
            }