# query_to_pdf/advanced_content_generator.py

import os
import json
from typing import Dict, Any, Optional
from enum import Enum
import re
import google.generativeai as genai

class ReportType(Enum):
    MARKET_RESEARCH = "market_research"

class ReportConfig:
    def __init__(self, title: str, subtitle: str, author: str, company: str, report_type: ReportType, target_audience: str, brand_colors: Optional[Dict[str, str]] = None, logo_path: Optional[str] = None):
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.company = company
        self.report_type = report_type
        self.target_audience = target_audience
        self.brand_colors = brand_colors or {}
        self.logo_path = logo_path

class AdvancedContentGenerator:
    """An AI-driven generator that creates a unified blueprint for an entire report."""
    
    def __init__(self, api_key: str):
        self.model: Optional[Any] = None
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model_version = os.getenv('GEMINI_MODEL_VERSION', 'gemini-2.0-flash')
                self.model = genai.GenerativeModel(model_version)
            except Exception as e:
                print(f"⚠️ Could not configure Gemini. Error: {e}")
                self.model = None

    def _get_chart_catalog(self) -> Dict[str, Any]:
        """
        Pull the live chart catalog from `visuals.charts`.
        Falls back to a flat list if the module is missing.
        """
        try:
            from visuals.charts import get_chart_catalog
            catalog = get_chart_catalog()
            if catalog:
                print(f"  ✅ Loaded {len(catalog)} charts from visuals.charts")
                return catalog
        except Exception as e:
            print(f"  ⚠️ Could not load chart catalog: {e}")
        
        # Fallback: wrap legacy list in minimal metadata
        legacy_types = [
            "bar", "line", "pie", "donut", "scatter", "area",
            "stackedBar", "multiLine", "radar", "bubble", "heatmap",
            "waterfall", "funnel", "gauge", "treeMap", "sunburst",
            "candlestick", "boxPlot", "violinPlot", "histogram",
            "pareto", "flowchart", "none",
        ]
        fallback_catalog = {t: {"goal": "generic", "dims": "nD", "complexity": "medium"}
                for t in legacy_types}
        print(f"  ⚠️ Using fallback catalog with {len(fallback_catalog)} charts")
        return fallback_catalog

    async def generate_full_report_blueprint(self, query: str, page_count: int) -> Optional[Dict[str, Any]]:
        """Generate a complete report blueprint using Gemini AI."""
        if not self.model:
            print("❌ ERROR: Gemini API not available. Cannot generate report without AI capabilities.")
            raise RuntimeError("Gemini API not available - cannot generate report")
        
        try:
            # Calculate number of sections based on page count
            num_sections = max(8, page_count * 2)  # Minimum 8 sections, 2 per page
            
            # Get chart catalog for dynamic chart selection
            chart_catalog = self._get_chart_catalog()
            
            prompt = f"""
Act as a team of senior strategy consultants from a top-tier firm like McKinsey, BCG, or Kearney. Your task is to create a complete, comprehensive, in-depth, and data-driven professional report of approximately {page_count} pages. The report is market research on the topic of: "{query}". The target audience is senior executives and decision makers.

Your output MUST be a single, complete, and well-formed JSON object, ready for parsing.

The JSON object must adhere to this exact structure:
- A root object with a single key: "sections".
- The "sections" key must contain a list of exactly {num_sections} section objects.

Each section object in the list MUST contain the following four keys:
1.  "title": A specific, detailed, and professional title that clearly indicates the section's focus and scope.
2.  "content": A comprehensive, detailed, well-structured narrative (2000-3500 words) using Typst-friendly markdown. Use `**bold text**` for subheadings or emphasis, and `-` for bullet points. The narrative MUST provide extensive context, detailed analysis, strategic insights, and comprehensive coverage of the topic. Include detailed market analysis, competitive landscape, industry trends, case studies, quantitative insights, strategic frameworks, and specific data points. Each section should be substantial and thorough with extensive depth and analysis.
3.  "chart_type": The most appropriate chart type from this catalog: {list(chart_catalog.keys())}. Choose the chart type that best visualizes the section's key data points and insights. Use "none" if no chart is appropriate.
4.  "chart_data": A JSON object with the appropriate data structure for the chosen chart type. The data MUST be realistic, relevant to the section content, and include detailed labels and values that directly support the section's analysis. Ensure the data is specific, accurate, and provides meaningful insights.

IMPORTANT REQUIREMENTS:
- Each section must be comprehensive and detailed (2000-3500 words minimum)
- Chart data must be highly relevant and specific to each section's content
- Use realistic, current data and statistics
- Include specific company names, market figures, and industry insights
- Ensure all content is professional and executive-level quality
- Make sure chart labels and values directly relate to the section's analysis
- Include detailed market analysis, competitive insights, and strategic recommendations

Respond with ONLY valid JSON format, no additional text or explanations. Use this exact structure:

{{
  "sections": [
    {{
      "title": "specific section title",
      "content": "comprehensive content with detailed analysis",
      "chart_type": "appropriate_chart_type",
      "chart_data": {{
        "labels": ["detailed", "relevant", "labels"],
        "values": [realistic, values, here]
      }}
    }}
  ]
}}

Ensure all property names are in double quotes and all string values are properly escaped.
"""

            generation_config = genai.types.GenerationConfig(
                temperature=float(os.getenv('GEMINI_TEMPERATURE', 0.6)),
                max_output_tokens=int(os.getenv('GEMINI_MAX_OUTPUT_TOKENS', 32768))
            )
            
            response = await self.model.generate_content_async(prompt, generation_config=generation_config)
            
            if not response or not response.text:
                print("❌ ERROR: No response from Gemini API")
                raise RuntimeError("No response from Gemini API")
            
            # Extract JSON from response
            extracted_data = self._extract_json_from_response(response.text)
            
            if extracted_data and "sections" in extracted_data:
                sections = extracted_data["sections"]
                if len(sections) >= 8:  # Ensure minimum sections
                    print(f"✅ Successfully generated report blueprint with {len(sections)} sections")
                    return extracted_data
                else:
                    print(f"❌ ERROR: Insufficient sections generated ({len(sections)} < 8 minimum)")
                    raise RuntimeError(f"Insufficient sections: {len(sections)} < 8 minimum")
            else:
                print("❌ ERROR: Could not extract valid JSON from AI response")
                raise RuntimeError("Invalid JSON response from Gemini API")
                
        except Exception as e:
            print(f"❌ ERROR: Failed to generate report blueprint: {e}")
            raise RuntimeError(f"Report generation failed: {e}")

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
        
        # Fix missing quotes around property names (most common issue)
        repaired = re.sub(r'(\s*)(\w+)(\s*):', r'\1"\2"\3:', repaired)
        
        # Fix missing commas between objects in arrays
        repaired = re.sub(r'}\s*{', '},{', repaired)
        
        # Fix missing commas between properties
        repaired = re.sub(r'"\s*\n\s*"', '",\n"', repaired)
        
        # Fix trailing commas
        repaired = re.sub(r',\s*}', '}', repaired)
        repaired = re.sub(r',\s*]', ']', repaired)
        
        # Fix unescaped quotes in content
        repaired = re.sub(r'(?<!\\)"(?=.*":)', r'\\"', repaired)
        
        # Fix newlines and special characters in content
        repaired = re.sub(r'\n', '\\n', repaired)
        repaired = re.sub(r'\r', '\\r', repaired)
        repaired = re.sub(r'\t', '\\t', repaired)
        
        # Remove any control characters that might cause issues
        repaired = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', repaired)
        
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