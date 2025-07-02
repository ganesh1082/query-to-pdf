"""
Report Planner - A dedicated module for generating report blueprints with improved AI prompts and JSON handling.
"""

import json
import re
import asyncio
from typing import Dict, Any, Optional, List
from enum import Enum
import google.generativeai as genai
from datetime import datetime


class ReportType(Enum):
    MARKET_RESEARCH = "market_research"
    COMPANY_ANALYSIS = "company_analysis"
    INDUSTRY_REPORT = "industry_report"
    TECHNICAL_ANALYSIS = "technical_analysis"


class ReportPlanner:
    """
    A dedicated planner for generating report blueprints with improved AI prompts
    and robust JSON parsing capabilities.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the report planner with Gemini API."""
        self.model: Optional[Any] = None
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("  ✅ Report Planner initialized with Gemini API")
            except Exception as e:
                print(f"  ⚠️ Failed to initialize Gemini: {e}")
                self.model = None
    
    async def generate_report_blueprint(self, query: str, page_count: int, report_type: ReportType = ReportType.MARKET_RESEARCH) -> Optional[Dict[str, Any]]:
        """
        Generate a comprehensive report blueprint with improved prompts and JSON handling.
        """
        if not self.model:
            print("  ⚠️ Gemini not available. Using fallback data.")
            return self._get_fallback_blueprint(query, report_type)
        
        num_sections = self._calculate_sections(page_count)
        
        # Create a more structured and clear prompt
        prompt = self._create_structured_prompt(query, page_count, num_sections, report_type)
        
        try:
            print(f"  🧠 Generating {num_sections}-section report blueprint...")
            
            # Use lower temperature for more consistent JSON output
            generation_config = genai.types.GenerationConfig(
                temperature=0.3,  # Lower temperature for more consistent output
                max_output_tokens=16384,  # Increased from 8192 for longer content
                top_p=0.8,
                top_k=40
            )
            
            response = await self.model.generate_content_async(prompt, generation_config=generation_config)
            
            print(f"  🔍 AI Response received: {len(response.text)} characters")
            
            # Extract and validate JSON
            json_data = self._extract_and_validate_json(response.text)
            
            if json_data and self._validate_blueprint_structure(json_data):
                print("  ✅ Successfully generated valid report blueprint")
                return json_data
            else:
                print("  ❌ Invalid JSON structure. Using fallback data.")
                return self._get_fallback_blueprint(query, report_type)
                
        except Exception as e:
            print(f"❌ Error in report planning: {e}")
            return self._get_fallback_blueprint(query, report_type)
    
    def _calculate_sections(self, page_count: int) -> int:
        """Calculate optimal number of sections based on page count."""
        # 1.5 pages per section on average
        base_sections = max(6, min(12, int(page_count / 1.5)))
        
        # Ensure we have enough sections for a comprehensive report
        if base_sections < 8:
            return 8
        elif base_sections > 12:
            return 12
        else:
            return base_sections
    
    def _create_structured_prompt(self, query: str, page_count: int, num_sections: int, report_type: ReportType) -> str:
        """Create a well-structured prompt that encourages proper JSON output with detailed content."""
        
        # Define section templates based on report type
        section_templates = self._get_section_templates(report_type, num_sections)
        
        # Calculate target content length per section - INCREASED for more comprehensive content
        target_words_per_section = max(600, int((page_count * 800) / num_sections))  # ~800 words per page (increased from 500)
        
        prompt = f"""You are an expert report writer and analyst. Create a comprehensive {page_count}-page report for: "{query}"

CRITICAL: Output ONLY valid JSON. No explanations, no markdown formatting, just pure JSON.

REPORT REQUIREMENTS:
- Total sections: {num_sections}
- Report type: {report_type.value}
- Target length: {page_count} pages
- Target content per section: {target_words_per_section} words minimum
- Content must be detailed, analytical, and comprehensive

REQUIRED JSON FORMAT:
{{
  "sections": [
    {{
      "title": "Section Title",
      "content": "DETAILED CONTENT with **bold** headings, - bullet points, and comprehensive analysis. Include specific data, trends, insights, and detailed explanations. Each section should be substantial and informative with multiple paragraphs, detailed examples, industry context, and expert analysis. Expand on key points with thorough explanations and provide actionable insights.",
      "chart_type": "bar|line|pie|donut|scatter|horizontalBar|none",
      "chart_data": {{}}
    }}
  ]
}}

SECTION TEMPLATES (use these exact titles and chart types):
{json.dumps(section_templates, indent=2)}

CONTENT REQUIREMENTS:
1. Each section must contain detailed, comprehensive content (minimum {target_words_per_section} words)
2. Include specific data points, statistics, and examples with detailed explanations
3. Use **bold** for important headings within content
4. Use - bullet points for key insights and findings
5. Provide analytical insights and expert commentary with detailed reasoning
6. Include relevant industry context and background information
7. Make content engaging and informative for professional audience
8. EXPAND on each point with detailed explanations and examples
9. Include multiple paragraphs with comprehensive analysis
10. Add industry-specific terminology and expert insights
11. Provide detailed market trends and future projections
12. Include competitive analysis and strategic implications

CHART DATA EXAMPLES:
- Bar chart: {{"labels": ["A", "B", "C"], "values": [10, 20, 30]}}
- Line chart: {{"labels": ["2020", "2021", "2022"], "values": [100, 120, 140]}}
- Pie chart: {{"labels": ["Red", "Blue", "Green"], "values": [30, 40, 30]}}
- Multi-series: {{"labels": ["Q1", "Q2", "Q3"], "series": [{{"name": "Series1", "values": [10, 15, 20]}}, {{"name": "Series2", "values": [5, 12, 18]}}]}}
- Empty: {{}}

JSON RULES:
1. All property names must be in double quotes
2. All string values must be in double quotes
3. Use commas between properties, not after the last one
4. Escape quotes in content with backslash: \\"
5. Use \\n for line breaks in content
6. No trailing commas before }} or ]

OUTPUT FORMAT:
```json
{{YOUR_JSON_HERE}}
```"""
        
        return prompt
    
    def _get_section_templates(self, report_type: ReportType, num_sections: int) -> List[Dict[str, Any]]:
        """Get section templates based on report type."""
        
        if report_type == ReportType.COMPANY_ANALYSIS:
            return [
                {"title": "Executive Summary", "chart_type": "none"},
                {"title": "Company Overview & History", "chart_type": "none"},
                {"title": "Financial Performance & Growth", "chart_type": "line"},
                {"title": "Market Position & Share", "chart_type": "bar"},
                {"title": "Product Portfolio Analysis", "chart_type": "pie"},
                {"title": "Competitive Landscape", "chart_type": "bar"},
                {"title": "Innovation & Future Outlook", "chart_type": "line"},
                {"title": "Risk Assessment", "chart_type": "none"},
                {"title": "Strategic Recommendations", "chart_type": "none"}
            ]
        elif report_type == ReportType.MARKET_RESEARCH:
            return [
                {"title": "Executive Summary", "chart_type": "none"},
                {"title": "Market Overview", "chart_type": "none"},
                {"title": "Market Size & Growth", "chart_type": "line"},
                {"title": "Market Segmentation", "chart_type": "pie"},
                {"title": "Competitive Analysis", "chart_type": "bar"},
                {"title": "Customer Analysis", "chart_type": "bar"},
                {"title": "Trend Analysis", "chart_type": "line"},
                {"title": "Market Opportunities", "chart_type": "scatter"},
                {"title": "Strategic Recommendations", "chart_type": "none"}
            ]
        else:
            # Generic template
            return [
                {"title": "Executive Summary", "chart_type": "none"},
                {"title": "Background & Context", "chart_type": "none"},
                {"title": "Key Findings", "chart_type": "bar"},
                {"title": "Trend Analysis", "chart_type": "line"},
                {"title": "Comparative Analysis", "chart_type": "bar"},
                {"title": "Impact Assessment", "chart_type": "pie"},
                {"title": "Future Projections", "chart_type": "line"},
                {"title": "Strategic Recommendations", "chart_type": "none"}
            ]
    
    def _extract_and_validate_json(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract and validate JSON from AI response with improved parsing."""
        
        if not response_text:
            return None
        
        # Clean the response
        cleaned_text = self._clean_response_text(response_text)
        
        # Try multiple extraction strategies
        json_data = self._extract_json_strategy_1(cleaned_text)  # ```json blocks
        if json_data:
            return json_data
        
        json_data = self._extract_json_strategy_2(cleaned_text)  # ``` blocks
        if json_data:
            return json_data
        
        json_data = self._extract_json_strategy_3(cleaned_text)  # Raw JSON
        if json_data:
            return json_data
        
        # Try a more aggressive extraction strategy for longer content
        json_data = self._extract_json_strategy_4(cleaned_text)  # Aggressive extraction
        if json_data:
            return json_data
        
        print("  ❌ All JSON extraction strategies failed")
        return None
    
    def _clean_response_text(self, text: str) -> str:
        """Clean response text for better JSON parsing."""
        # Remove control characters
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Remove common AI artifacts
        cleaned = re.sub(r'^Here is the.*?:', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^I have created.*?:', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'^The report.*?:', '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    def _extract_json_strategy_1(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from ```json blocks."""
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            try:
                json_str = self._repair_json(match.group(1))
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"  ❌ Strategy 1 failed: {e}")
        return None
    
    def _extract_json_strategy_2(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from ``` blocks."""
        match = re.search(r'```\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            try:
                json_str = self._repair_json(match.group(1))
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"  ❌ Strategy 2 failed: {e}")
        return None
    
    def _extract_json_strategy_3(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from raw text."""
        # Find the largest JSON object
        brace_count = 0
        start = -1
        max_length = 0
        best_json = None
        
        for i, char in enumerate(text):
            if char == '{':
                if brace_count == 0:
                    start = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start != -1:
                    json_candidate = text[start:i+1]
                    if len(json_candidate) > max_length:
                        try:
                            json_str = self._repair_json(json_candidate)
                            json.loads(json_str)  # Test if valid
                            max_length = len(json_candidate)
                            best_json = json_str
                        except json.JSONDecodeError:
                            pass
        
        if best_json:
            try:
                return json.loads(best_json)
            except json.JSONDecodeError as e:
                print(f"  ❌ Strategy 3 failed: {e}")
        
        return None
    
    def _extract_json_strategy_4(self, text: str) -> Optional[Dict[str, Any]]:
        """Aggressive JSON extraction for longer content with multiple repair attempts."""
        # Try to find JSON structure even if it's malformed
        # Look for the largest possible JSON object
        
        # First, try to find sections array
        sections_match = re.search(r'"sections"\s*:\s*\[(.*?)\]', text, re.DOTALL)
        if sections_match:
            # Try to reconstruct the JSON
            sections_content = sections_match.group(1)
            
            # Find all section objects
            section_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', sections_content)
            
            if section_matches:
                # Try to reconstruct a valid JSON
                reconstructed_json = '{"sections": [' + ','.join(section_matches) + ']}'
                
                # Try multiple repair attempts
                for attempt in range(3):
                    try:
                        repaired = self._repair_json(reconstructed_json)
                        return json.loads(repaired)
                    except json.JSONDecodeError:
                        # Try more aggressive repairs
                        repaired = re.sub(r'([^"])\n([^"])', r'\1\\n\2', repaired)
                        try:
                            return json.loads(repaired)
                        except json.JSONDecodeError:
                            continue
        
        return None
    
    def _repair_json(self, json_str: str) -> str:
        """Repair common JSON formatting issues with enhanced handling for longer content."""
        
        # Try parsing as-is first
        try:
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            pass
        
        repaired = json_str
        
        # Fix unquoted property names (most common issue)
        repaired = re.sub(r'(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*):', r'\1"\2"\3:', repaired)
        
        # Fix missing commas between objects in arrays
        repaired = re.sub(r'}\s*{', '},{', repaired)
        
        # Fix trailing commas
        repaired = re.sub(r',\s*}', '}', repaired)
        repaired = re.sub(r',\s*]', ']', repaired)
        
        # Fix unescaped quotes in string values - more robust handling
        # Look for quotes that are inside string values but not escaped
        # This is a more sophisticated approach for longer content
        lines = repaired.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Skip lines that are property definitions (already handled)
            if re.match(r'\s*"[^"]*"\s*:', line):
                fixed_lines.append(line)
                continue
            
            # For content lines, escape unescaped quotes more carefully
            if '"' in line:
                # Split by quotes and escape them properly
                parts = line.split('"')
                if len(parts) > 1:
                    # Escape quotes in content parts (odd indices)
                    for i in range(1, len(parts), 2):
                        if i < len(parts):
                            parts[i] = parts[i].replace('"', '\\"')
                    line = '"'.join(parts)
            
            fixed_lines.append(line)
        
        repaired = '\n'.join(fixed_lines)
        
        # Fix newlines in content - more comprehensive
        repaired = re.sub(r'(?<!\\)\n', '\\n', repaired)
        repaired = re.sub(r'(?<!\\)\r', '\\r', repaired)
        repaired = re.sub(r'(?<!\\)\t', '\\t', repaired)
        
        # Additional fixes for longer content
        # Fix missing quotes around string values
        repaired = re.sub(r':\s*([^"\d\[\]{},][^,}\]]*[^"\d\[\]{},])\s*([,}\]])', r': "\1"\2', repaired)
        
        # Fix common AI formatting issues
        repaired = re.sub(r'\\n\\n', '\\n', repaired)  # Remove double newlines
        repaired = re.sub(r'\\n\s*\\n', '\\n', repaired)  # Remove newlines with spaces
        
        return repaired
    
    def _validate_blueprint_structure(self, data: Dict[str, Any]) -> bool:
        """Validate that the blueprint has the correct structure."""
        if not isinstance(data, dict):
            return False
        
        if 'sections' not in data:
            return False
        
        sections = data['sections']
        if not isinstance(sections, list) or len(sections) == 0:
            return False
        
        # Validate each section
        for section in sections:
            if not isinstance(section, dict):
                return False
            
            required_fields = ['title', 'content', 'chart_type', 'chart_data']
            for field in required_fields:
                if field not in section:
                    return False
        
        return True
    
    def _get_fallback_blueprint(self, query: str, report_type: ReportType) -> Dict[str, Any]:
        """Provide a fallback blueprint when AI generation fails."""
        print("  📝 Using fallback blueprint")
        
        # Generate a simple but comprehensive fallback
        sections = [
            {
                "title": "Executive Summary",
                "content": f"**Overview:** This report provides a comprehensive analysis of {query}. The analysis examines key trends, market dynamics, and strategic implications for stakeholders.",
                "chart_type": "none",
                "chart_data": {}
            },
            {
                "title": "Market Analysis",
                "content": "**Market Overview:** The market demonstrates significant growth potential with diverse competitive dynamics. Understanding these factors is crucial for strategic decision-making.",
                "chart_type": "bar",
                "chart_data": {
                    "labels": ["Segment A", "Segment B", "Segment C", "Segment D"],
                    "values": [30, 25, 20, 25]
                }
            },
            {
                "title": "Trend Analysis",
                "content": "**Growth Trends:** Recent years have shown consistent growth patterns with some seasonal variations. Future projections indicate continued expansion.",
                "chart_type": "line",
                "chart_data": {
                    "labels": ["2020", "2021", "2022", "2023", "2024"],
                    "values": [100, 115, 130, 145, 160]
                }
            },
            {
                "title": "Strategic Recommendations",
                "content": "**Action Items:** Based on the analysis, key recommendations include market expansion, technology investment, and strategic partnerships.",
                "chart_type": "none",
                "chart_data": {}
            }
        ]
        
        return {"sections": sections} 