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
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as e:
                print(f"⚠️ Could not configure Gemini. Error: {e}")
                self.model = None

    async def generate_full_report_blueprint(self, query: str, page_count: int) -> Optional[Dict[str, Any]]:
        """Generates a complete report blueprint including titles, chart data, and narrative content."""
        if not self.model:
            print("  ⚠️ Gemini not available. Using mock data.")
            return self._get_mock_report_blueprint()

        num_sections = max(8, min(14, int(page_count / 1.5)))

        prompt = f"""
        Act as a top-tier market research analyst creating a deep-dive report of approximately {page_count} pages on the query: "{query}".
        Your task is to generate the entire report's content as a single, complete JSON object.

        The JSON object must have a key "sections" containing a list of {num_sections} section objects.
        Each section object must contain:
        1. "title": A relevant, insightful title for the section.
        2. "content": A detailed, well-structured narrative (250-400 words), using Typst-friendly markdown: **bold** for subheadings and `-` for bullet points. The narrative MUST explain the data in 'chart_data'.
        3. "chart_type": The best chart for this section. Use a diverse mix of "bar", "line", "pie", "donut", "scatter", "horizontalBar", or "none".
        4. "chart_data": A JSON object with plausible, realistic data. Use the exact formats specified below.

        The first section MUST be an "Executive Summary" (chart_type: "none").
        The final sections MUST include "Strategic Recommendations" and "Risk Assessment" (chart_type: "none").
        Ensure all content is generated and complete.

        OUTPUT ONLY THE COMPLETE JSON OBJECT, WRAPPED IN ```json ... ```.

        CRITICAL: Use these EXACT chart_data formats:
        - For bar/line/pie/donut (single series): {{"labels": ["A", "B", "C"], "values": [10, 20, 30]}}
        - For multi-series line charts: {{"labels": ["2020", "2021", "2022"], "series": [{{"name": "Series1", "values": [10, 15, 20]}}, {{"name": "Series2", "values": [5, 12, 18]}}]}}
        - For scatter: {{"points": [{{"x": 1, "y": 2, "name": "P1"}}, {{"x": 3, "y": 4, "name": "P2"}}]}}
        
        IMPORTANT: For line charts, if you want multiple series, use the "series" array format. If single series, use "labels" and "values".
        """
        
        try:
            print(f"  🧠 Generating full {num_sections}-section report blueprint with Gemini...")
            generation_config = genai.types.GenerationConfig(temperature=0.6, max_output_tokens=8192)
            response = await self.model.generate_content_async(prompt, generation_config=generation_config)
            
            # Robustly extract JSON from the response
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", response.text, re.DOTALL)
            if not json_match:
                print("❌ No valid JSON block found in the AI response. Falling back to mock data.")
                return self._get_mock_report_blueprint()

            json_str = json_match.group(1)
            report_data = json.loads(json_str)
            print("  ✅ Successfully generated and parsed full report blueprint.")
            return report_data
        except Exception as e:
            print(f"❌ Error generating full report blueprint: {e}")
            # Only try to access response.text if response exists
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"  ⚠️ Raw AI response was:\n---\n{response.text[:500]}...\n---")
            return self._get_mock_report_blueprint()

    def _get_mock_report_blueprint(self) -> Dict[str, Any]:
        """Provides a complete fallback blueprint with all content if the AI fails."""
        print("  📝 Using mock report blueprint as a fallback.")
        return {
            "sections": [
                {"title": "Executive Summary", "content": "**Overview:** This mock report demonstrates the intended structure. The global coffee market is a complex system influenced by climate, economics, and consumer trends. This report analyzes these factors to provide strategic insights.", "chart_type": "none", "chart_data": {}},
                {"title": "Key Coffee Producing Regions", "content": "**Production Analysis:** Brazil leads global coffee production, followed by Vietnam and Colombia. Each region specializes in different bean types and qualities, creating a diverse global supply.", "chart_type": "horizontalBar", "chart_data": {"labels": ["Brazil", "Vietnam", "Colombia", "Indonesia", "Ethiopia"], "values": [62.5, 30.1, 12.5, 11.2, 10.5]}},
                {"title": "Processing Method Distribution", "content": "**Methodology Impact:** The 'Washed' or wet process is the most common method, known for producing clean and bright flavors. Dry processing accounts for a significant portion, offering fuller-bodied coffees.", "chart_type": "pie", "chart_data": {"labels": ["Wet Processed", "Dry Processed", "Honey Processed"], "values": [60, 30, 10]}},
                {"title": "Market Price Trends (USD/lb)", "content": "**Price Volatility:** Coffee prices have shown a steady increase over the past five years, driven by rising demand and climate-related supply constraints. This trend underscores the need for robust risk management strategies.", "chart_type": "line", "chart_data": {"labels": ["2019", "2020", "2021", "2022", "2023"], "values": [1.05, 1.15, 1.50, 1.90, 1.85]}},
                {"title": "Strategic Recommendations", "content": "**Actionable Insights:** To navigate the evolving market, companies should focus on diversifying sourcing, investing in sustainable practices, and leveraging technology for supply chain transparency.", "chart_type": "none", "chart_data": {}},
            ]
        }