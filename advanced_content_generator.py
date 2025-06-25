# query-to-pdf copy/advanced_content_generator.py

import os
import json
from typing import Dict, Any, Optional
from enum import Enum
import google.generativeai as genai

class ReportType(Enum):
    MARKET_RESEARCH = "market_research"

class ReportConfig:
    def __init__(self, title: str, subtitle: str, author: str, company: str, report_type: ReportType, target_audience: str, brand_colors: Dict[str, str], logo_path: Optional[str] = None):
        self.title = title; self.subtitle = subtitle; self.author = author; self.company = company; self.report_type = report_type; self.target_audience = target_audience; self.brand_colors = brand_colors; self.logo_path = logo_path

class AdvancedContentGenerator:
    """An AI-driven generator that creates a single, unified blueprint for the entire report."""
    
    def __init__(self, api_key: Optional[str]):
        self.model: Optional[Any] = None
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Using the correct, available model name
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as e:
                print(f"⚠️ Could not configure Gemini. Error: {e}")

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
        Each section object in the list must contain:
        1. "title": A relevant and insightful title for the section.
        2. "content": A detailed, well-structured narrative for the section (250-400 words), using markdown: **bold** for subheadings, and * for bullets. The narrative MUST explain the data in the 'chart_data'.
        3. "chart_type": The best chart for this section. Use a diverse mix of "bar", "line", "pie", "donut", "scatter", "horizontalBar", "area", or "none".
        4. "chart_data": A JSON object with plausible, realistic data for the specified chart type.

        The first section MUST be "Executive Summary" (chart_type: "none").
        The final sections MUST include "Strategic Recommendations" and "Risk Assessment" (chart_type: "none").
        Ensure all content is generated and complete.

        OUTPUT ONLY THE COMPLETE JSON OBJECT.
        """
        
        try:
            print(f"  🧠 Generating full {num_sections}-section report blueprint with Gemini...")
            generation_config = genai.types.GenerationConfig(temperature=0.7, max_output_tokens=8192)
            response = await self.model.generate_content_async(prompt, generation_config=generation_config)
            
            cleaned_text = response.text.strip().replace('```json', '').replace('```', '')
            report_data = json.loads(cleaned_text)
            print("  ✅ Successfully generated and parsed full report blueprint.")
            return report_data
        except Exception as e:
            print(f"❌ Error generating full report blueprint: {e}")
            return self._get_mock_report_blueprint()

    def _get_mock_report_blueprint(self) -> Dict[str, Any]:
        """Provides a complete fallback blueprint with all content if the AI fails."""
        print("  📝 Using mock report blueprint as a fallback.")
        return {
            "sections": [
                {"title": "Executive Summary", "content": "**Overview:** This mock report demonstrates the intended structure and content flow...", "chart_type": "none", "chart_data": {}},
                {"title": "Projected Market Growth (in Billions USD)", "content": "**Strong Upward Trajectory:** Our analysis projects a substantial increase in market size...", "chart_type": "line", "chart_data": {"labels": ["2025", "2026", "2027", "2028", "2029", "2030"], "values": [2.1, 4.5, 9.0, 15.5, 21.0, 25.0]}},
                {"title": "Investment Allocation in a Series B Startup", "content": "**Focus on Scale and R&D:** The primary use of capital for startups is dedicated to scaling production...", "chart_type": "donut", "chart_data": {"labels": ["Scaling Production", "R&D", "Regulatory & Legal", "Marketing"], "values": [45, 35, 10, 10]}}
            ]
        }

    def _normalize_chart_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(data, dict):
            return data
        # Already in simple format
        if 'values' in data:
            return data
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        # Try to extract values from the first dataset
        if datasets and isinstance(datasets, list) and len(datasets) > 0:
            first_dataset = datasets[0]
            if isinstance(first_dataset, dict):
                # For scatter
                if 'data' in first_dataset and isinstance(first_dataset['data'], list):
                    dataset_data = first_dataset['data']
                    if dataset_data and isinstance(dataset_data[0], dict) and 'x' in dataset_data[0] and 'y' in dataset_data[0]:
                        return {
                            'points': [{'x': point.get('x', 0), 'y': point.get('y', 0), 'name': f'Point {i+1}'} for i, point in enumerate(dataset_data)]
                        }
                    # For bar/line/pie
                    elif all(isinstance(x, (int, float)) for x in dataset_data):
                        return {
                            'labels': labels,
                            'values': dataset_data
                        }
        # Fallback: if labels exist but no values, return empty values
        if labels and not datasets:
            return {'labels': labels, 'values': [0]*len(labels)}
        return data