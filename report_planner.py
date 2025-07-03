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
                self.model = genai.GenerativeModel('gemini-2.5-flash')
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
                # Add fixed Executive Summary
                json_data = self._add_fixed_executive_summary(json_data, query, report_type)
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

REPORT FLOW STRUCTURE:
1. Executive Summary (FIXED - will be added automatically)
2. Analysis Sections (DYNAMIC - create natural section titles based on research content)
3. Strategic Recommendations (DYNAMIC - actionable roadmap with clear owners)
4. Future Outlook (DYNAMIC - market trends, risk assessment, opportunity identification)

REQUIRED JSON FORMAT:
{{
  "sections": [
    {{
      "title": "Executive Summary",
      "content": "FIXED CONTENT - will be replaced automatically",
      "chart_type": "none",
      "chart_data": {{}}
    }},
    {{
      "title": "DYNAMIC SECTION TITLE",
      "content": "DETAILED CONTENT with **bold** headings, - bullet points, and comprehensive analysis. Include specific data, trends, insights, and detailed explanations. Each section should be substantial and informative with multiple paragraphs, detailed examples, industry context, and expert analysis. Expand on key points with thorough explanations and provide actionable insights.",
      "chart_type": "bar|horizontalBar|line|pie|donut|scatter|area|stackedBar|multiLine|radar|bubble|heatmap|waterfall|funnel|gauge|treeMap|sunburst|candlestick|boxPlot|violinPlot|histogram|pareto|flowchart|none",
      "chart_data": {{}}
    }}
  ]
}}

DYNAMIC SECTION GUIDELINES:
- Create natural, relevant section titles based on the research topic
- Use strategic frameworks (PESTLE, Porter's Five Forces, SWOT, etc.) where appropriate
- Include data-driven insights with supporting evidence
- Provide comprehensive analysis with multiple perspectives
- Focus on actionable intelligence and strategic implications

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
- Horizontal bar: {{"labels": ["A", "B", "C"], "values": [10, 20, 30]}}
- Line chart: {{"labels": ["2020", "2021", "2022"], "values": [100, 120, 140]}}
- Pie chart: {{"labels": ["Red", "Blue", "Green"], "values": [30, 40, 30]}}
- Donut chart: {{"labels": ["Red", "Blue", "Green"], "values": [30, 40, 30]}}
- Scatter plot: {{"labels": ["Point1", "Point2", "Point3"], "x_values": [1, 2, 3], "y_values": [10, 20, 30]}}
- Area chart: {{"labels": ["2020", "2021", "2022"], "values": [100, 120, 140]}}
- Stacked bar: {{"labels": ["Q1", "Q2", "Q3"], "series": [{{"name": "Product A", "values": [10, 15, 20]}}, {{"name": "Product B", "values": [5, 12, 18]}}]}}
- Multi-line: {{"labels": ["Jan", "Feb", "Mar"], "series": [{{"name": "Revenue", "values": [100, 120, 140]}}, {{"name": "Profit", "values": [20, 25, 30]}}]}}
- Radar chart: {{"labels": ["Quality", "Price", "Service", "Innovation", "Brand"], "values": [85, 70, 90, 75, 80]}}
- Bubble chart: {{"labels": ["A", "B", "C"], "x_values": [10, 20, 30], "y_values": [5, 15, 25], "sizes": [20, 40, 60]}}
- Heatmap: {{"labels": ["Q1", "Q2", "Q3", "Q4"], "categories": ["North", "South", "East", "West"], "values": [[10, 20, 30, 40], [15, 25, 35, 45], [20, 30, 40, 50], [25, 35, 45, 55]]}}
- Waterfall chart: {{"labels": ["Start", "Revenue", "Costs", "Taxes", "End"], "values": [100, 50, -30, -10, 110]}}
- Funnel chart: {{"labels": ["Leads", "Qualified", "Proposals", "Negotiations", "Closed"], "values": [1000, 800, 600, 400, 200]}}
- Gauge chart: {{"value": 75, "max": 100, "label": "Performance"}}
- Tree map: {{"labels": ["Category A", "Category B", "Category C"], "values": [40, 30, 30], "subcategories": [["A1", "A2"], ["B1", "B2"], ["C1", "C2"]]}}
- Sunburst chart: {{"labels": ["Root", "Branch1", "Branch2"], "values": [100, 60, 40], "children": [["Leaf1", "Leaf2"], ["Leaf3", "Leaf4"]]}}
- Candlestick: {{"labels": ["Day1", "Day2", "Day3"], "open": [100, 105, 110], "high": [110, 115, 120], "low": [95, 100, 105], "close": [105, 110, 115]}}
- Box plot: {{"labels": ["Group A", "Group B", "Group C"], "data": [[10, 15, 20, 25, 30], [12, 18, 22, 28, 35], [8, 12, 18, 24, 32]]}}
- Violin plot: {{"labels": ["Group A", "Group B"], "data": [[10, 15, 20, 25, 30], [12, 18, 22, 28, 35]]}}
- Histogram: {{"labels": ["0-10", "11-20", "21-30", "31-40"], "values": [5, 12, 8, 3]}}
- Pareto chart: {{"labels": ["Issue A", "Issue B", "Issue C", "Issue D"], "values": [40, 30, 20, 10], "cumulative": [40, 70, 90, 100]}}
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
        """Get flexible section guidelines based on report type."""
        
        # Base structure with Executive Summary always first
        base_sections = [
            {"title": "Executive Summary", "chart_type": "none"}
        ]
        
        # Dynamic section suggestions based on report type
        if report_type == ReportType.COMPANY_ANALYSIS:
            dynamic_suggestions = [
                "Company Overview & History",
                "Financial Performance & Growth", 
                "Market Position & Share",
                "Product Portfolio Analysis",
                "Competitive Landscape",
                "Innovation & Future Outlook",
                "Risk Assessment",
                "Strategic Recommendations"
            ]
        elif report_type == ReportType.MARKET_RESEARCH:
            dynamic_suggestions = [
                "Market Overview",
                "Market Size & Growth",
                "Market Segmentation",
                "Competitive Analysis",
                "Customer Analysis",
                "Trend Analysis",
                "Market Opportunities",
                "Strategic Recommendations"
            ]
        else:
            # Generic suggestions
            dynamic_suggestions = [
                "Background & Context",
                "Key Findings",
                "Trend Analysis",
                "Comparative Analysis",
                "Impact Assessment",
                "Future Projections",
                "Strategic Recommendations"
            ]
        
        # Add dynamic sections (excluding Executive Summary)
        remaining_sections = num_sections - 1
        for i in range(remaining_sections):
            if i < len(dynamic_suggestions):
                # Suggest chart types based on section content
                chart_type = self._suggest_chart_type(dynamic_suggestions[i])
                base_sections.append({
                    "title": dynamic_suggestions[i],
                    "chart_type": chart_type
                })
            else:
                # Generic dynamic section
                base_sections.append({
                    "title": f"Analysis Section {i+1}",
                    "chart_type": "bar"
                })
        
        return base_sections
    
    def _suggest_chart_type(self, section_title: str) -> str:
        """Suggest appropriate chart type based on section title with enhanced variety and intelligence."""
        title_lower = section_title.lower()
        
        # Executive Summary and recommendations typically don't need charts
        if any(word in title_lower for word in ['executive summary', 'summary', 'recommendations', 'conclusion', 'overview']):
            return 'none'
        
        # Time series and trends
        if any(word in title_lower for word in ['growth', 'trend', 'performance', 'forecast', 'timeline', 'evolution', 'history', 'development']):
            return 'line'
        
        # Distribution and composition
        elif any(word in title_lower for word in ['segmentation', 'distribution', 'breakdown', 'composition', 'portfolio', 'mix', 'structure']):
            return 'pie'
        
        # Comparisons and rankings
        elif any(word in title_lower for word in ['competitive', 'comparison', 'analysis', 'ranking', 'benchmark', 'versus', 'vs', 'market share']):
            return 'bar'
        
        # Opportunities and correlations
        elif any(word in title_lower for word in ['opportunities', 'scatter', 'correlation', 'relationship', 'factors', 'drivers']):
            return 'scatter'
        
        # Financial and cumulative data
        elif any(word in title_lower for word in ['financial', 'revenue', 'profit', 'cost', 'budget', 'cumulative', 'earnings', 'income']):
            return 'waterfall'
        
        # Sales and conversion processes
        elif any(word in title_lower for word in ['sales', 'conversion', 'funnel', 'pipeline', 'leads', 'process', 'workflow']):
            return 'funnel'
        
        # Performance metrics and KPIs
        elif any(word in title_lower for word in ['performance', 'kpi', 'metric', 'score', 'rating', 'efficiency', 'productivity']):
            return 'gauge'
        
        # Market share and competitive landscape
        elif any(word in title_lower for word in ['market share', 'competitive landscape', 'positioning', 'competitive analysis']):
            return 'radar'
        
        # Geographic and regional data
        elif any(word in title_lower for word in ['geographic', 'regional', 'location', 'territory', 'global', 'international']):
            return 'heatmap'
        
        # Hierarchical and organizational data
        elif any(word in title_lower for word in ['hierarchy', 'organization', 'structure', 'category', 'classification']):
            return 'tree map'
        
        # Stock and financial trading data
        elif any(word in title_lower for word in ['stock', 'trading', 'price', 'market data', 'investment', 'returns']):
            return 'candlestick'
        
        # Statistical distributions
        elif any(word in title_lower for word in ['distribution', 'statistics', 'variance', 'spread', 'demographics', 'population']):
            return 'box plot'
        
        # Process and workflow analysis
        elif any(word in title_lower for word in ['process', 'workflow', 'efficiency', 'productivity', 'operations']):
            return 'histogram'
        
        # Quality and defect analysis
        elif any(word in title_lower for word in ['quality', 'defect', 'issue', 'problem', 'challenges', 'risks']):
            return 'pareto'
        
        # Multi-dimensional analysis
        elif any(word in title_lower for word in ['multi', 'dimensional', 'complex', 'comprehensive', 'holistic']):
            return 'bubble'
        
        # Customer and user analysis
        elif any(word in title_lower for word in ['customer', 'user', 'consumer', 'audience', 'demographics']):
            return 'bar'
        
        # Technology and innovation
        elif any(word in title_lower for word in ['technology', 'innovation', 'research', 'development', 'rd']):
            return 'line'
        
        # Supply chain and logistics
        elif any(word in title_lower for word in ['supply chain', 'logistics', 'operations', 'inventory', 'procurement']):
            return 'bar'
        
        # Default to bar chart for general analysis
        else:
            return 'bar'
    
    def _should_include_chart(self, section_title: str, content_length: int) -> bool:
        """Intelligently determine if a section should include a chart based on content and purpose."""
        title_lower = section_title.lower()
        
        # Sections that typically don't benefit from charts
        no_chart_sections = [
            'executive summary', 'summary', 'conclusion', 'recommendations', 
            'methodology', 'approach', 'introduction', 'background'
        ]
        
        if any(no_chart in title_lower for no_chart in no_chart_sections):
            return False
        
        # Sections that almost always benefit from charts
        chart_heavy_sections = [
            'market analysis', 'financial performance', 'competitive analysis',
            'trend analysis', 'data analysis', 'statistical analysis'
        ]
        
        if any(chart_section in title_lower for chart_section in chart_heavy_sections):
            return True
        
        # For other sections, base decision on content length
        # Short content (< 100 words) usually doesn't need charts
        if content_length < 100:
            return False
        
        # Long content (> 300 words) usually benefits from charts
        if content_length > 300:
            return True
        
        # Medium content: include charts for analytical sections
        analytical_keywords = [
            'analysis', 'comparison', 'evaluation', 'assessment', 'review',
            'examination', 'investigation', 'study', 'research'
        ]
        
        return any(keyword in title_lower for keyword in analytical_keywords)
    
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
        
        # Try a final strategy with multiple repair attempts
        json_data = self._extract_json_strategy_5(cleaned_text)  # Multi-repair strategy
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
    
    def _extract_json_strategy_5(self, text: str) -> Optional[Dict[str, Any]]:
        """Multi-repair strategy with multiple attempts to fix JSON."""
        # Find the largest JSON object and try multiple repair strategies
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
                        max_length = len(json_candidate)
                        best_json = json_candidate
        
        if not best_json:
            return None
        
        # Try multiple repair strategies
        repair_strategies = [
            lambda x: self._repair_json(x),
            lambda x: self._repair_json_aggressive(x),
            lambda x: self._repair_json_minimal(x),
        ]
        
        for strategy in repair_strategies:
            try:
                repaired = strategy(best_json)
                result = json.loads(repaired)
                print(f"  ✅ Strategy 5 succeeded with repair strategy")
                return result
            except json.JSONDecodeError as e:
                print(f"  🔍 Strategy 5 repair attempt failed: {e}")
                continue
        
        return None
    
    def _repair_json_aggressive(self, json_str: str) -> str:
        """More aggressive JSON repair for complex cases."""
        repaired = json_str
        
        # Remove control characters first
        repaired = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', repaired)

        # Replace unescaped newlines inside string values (especially in content) with \\n
        # This regex finds all string values and replaces newlines inside them
        def replace_newlines_in_strings(match):
            value = match.group(0)
            # Only replace newlines inside the quotes
            return value.replace('\n', '\\n').replace('\r', '\\r')
        repaired = re.sub(r'"(.*?)"', replace_newlines_in_strings, repaired)

        # Remove all newlines and extra spaces in content (legacy)
        repaired = re.sub(r'"content"\s*:\s*"([^"]*)"', lambda m: '"content": "{}"'.format(m.group(1).replace(chr(10), " ").replace(chr(13), " ").replace(chr(9), " ")), repaired)

        # Fix any remaining quote issues - more comprehensive
        # Handle unescaped quotes in content
        repaired = re.sub(
            r'"content"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"',
            lambda m: '"content": "{}"'.format(m.group(1).replace('"', '\\"')),
            repaired
        )
        
        # Fix any remaining unescaped quotes in string values
        repaired = re.sub(r'([^\\])"([^"]*)"([^"]*)"', r'\1"\2\\"\3"', repaired)
        
        # Ensure all property names are quoted
        repaired = re.sub(r'(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*):', r'\1"\2"\3:', repaired)
        
        # Fix missing commas between properties
        repaired = re.sub(r'"\s*\n\s*"', '",\n"', repaired)
        
        # Fix trailing commas
        repaired = re.sub(r',\s*}', '}', repaired)
        repaired = re.sub(r',\s*]', ']', repaired)
        
        return repaired
    
    def _repair_json_minimal(self, json_str: str) -> str:
        """Minimal JSON repair - just fix the most common issues."""
        repaired = json_str
        
        # Fix unquoted property names
        repaired = re.sub(r'(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*):', r'\1"\2"\3:', repaired)
        
        # Fix trailing commas
        repaired = re.sub(r',\s*}', '}', repaired)
        repaired = re.sub(r',\s*]', ']', repaired)
        
        return repaired
    
    def _repair_json(self, json_str: str) -> str:
        """Repair common JSON formatting issues with enhanced handling for longer content."""
        
        # Try parsing as-is first
        try:
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            pass
        
        repaired = json_str
        
        # Remove any BOM or encoding issues
        repaired = repaired.replace('\ufeff', '')
        
        # Fix unquoted property names (most common issue)
        repaired = re.sub(r'(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*):', r'\1"\2"\3:', repaired)
        
        # Fix missing commas between objects in arrays
        repaired = re.sub(r'}\s*{', '},{', repaired)
        
        # Fix trailing commas
        repaired = re.sub(r',\s*}', '}', repaired)
        repaired = re.sub(r',\s*]', ']', repaired)
        
        # Fix missing commas between properties
        repaired = re.sub(r'"\s*\n\s*"', '",\n"', repaired)
        
        # Fix unescaped quotes in string values - more robust handling
        # First, let's handle the content field specifically since it's the most problematic
        content_pattern = r'"content"\s*:\s*"([^"]*(?:\\"[^"]*)*)"'
        content_matches = re.findall(content_pattern, repaired)
        
        for content in content_matches:
            # Escape any unescaped quotes in content
            escaped_content = content.replace('"', '\\"')
            # Replace the original content with escaped version
            repaired = repaired.replace(f'"content": "{content}"', f'"content": "{escaped_content}"')
        
        # Handle other string values more carefully
        lines = repaired.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Skip lines that are property definitions (already handled)
            if re.match(r'\s*"[^"]*"\s*:', line):
                fixed_lines.append(line)
                continue
            
            # For content lines, escape unescaped quotes more carefully
            if '"' in line and not line.strip().startswith('"'):
                # This is likely a content line with unescaped quotes
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
        
        # Fix any remaining unescaped quotes in string values
        # Look for patterns like "text"text" and fix them
        repaired = re.sub(r'([^\\])"([^"]*)"([^"]*)"', r'\1"\2\\"\3"', repaired)
        
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
        
        # Generate a simple but comprehensive fallback with fixed Executive Summary
        sections = [
            {
                "title": "Executive Summary",
                "content": self._generate_fixed_executive_summary(query, report_type),
                "chart_type": "none",
                "chart_data": {}
            },
            {
                "title": "Market Analysis",
                "content": "**Market Overview:** The market demonstrates significant growth potential with diverse competitive dynamics. Understanding these factors is crucial for strategic decision-making. **Key Trends:** Recent market analysis reveals several emerging trends that are reshaping the competitive landscape. **Growth Drivers:** Multiple factors are contributing to market expansion, including technological innovation, changing consumer preferences, and regulatory developments.",
                "chart_type": "bar",
                "chart_data": {
                    "labels": ["Segment A", "Segment B", "Segment C", "Segment D"],
                    "values": [30, 25, 20, 25]
                }
            },
            {
                "title": "Competitive Landscape",
                "content": "**Competitive Analysis:** The competitive landscape is characterized by both established players and emerging disruptors. **Market Share Distribution:** Current market share analysis shows a fragmented landscape with opportunities for consolidation. **Competitive Advantages:** Key players differentiate through technology, customer service, and strategic partnerships.",
                "chart_type": "radar",
                "chart_data": {
                    "labels": ["Technology", "Market Share", "Customer Service", "Innovation", "Brand Recognition"],
                    "values": [85, 70, 90, 75, 80]
                }
            },
            {
                "title": "Financial Performance",
                "content": "**Revenue Analysis:** Financial performance shows strong growth trends with improving profitability margins. **Cost Structure:** Operational efficiency improvements are driving cost reductions across key business areas. **Investment Returns:** Strategic investments are delivering positive returns and supporting future growth initiatives.",
                "chart_type": "waterfall",
                "chart_data": {
                    "labels": ["Start", "Revenue", "Costs", "Taxes", "End"],
                    "values": [100, 50, -30, -10, 110]
                }
            },
            {
                "title": "Sales Pipeline",
                "content": "**Lead Generation:** The sales pipeline demonstrates strong lead generation capabilities with high conversion rates. **Conversion Process:** Each stage of the sales funnel shows optimized processes and clear progression metrics. **Revenue Impact:** Pipeline improvements are directly contributing to revenue growth and market expansion.",
                "chart_type": "funnel",
                "chart_data": {
                    "labels": ["Leads", "Qualified", "Proposals", "Negotiations", "Closed"],
                    "values": [1000, 800, 600, 400, 200]
                }
            },
            {
                "title": "Trend Analysis",
                "content": "**Growth Trends:** Recent years have shown consistent growth patterns with some seasonal variations. Future projections indicate continued expansion. **Technology Impact:** Digital transformation is driving fundamental changes in market dynamics. **Customer Behavior:** Shifting preferences are creating new opportunities and challenges.",
                "chart_type": "line",
                "chart_data": {
                    "labels": ["2020", "2021", "2022", "2023", "2024"],
                    "values": [100, 115, 130, 145, 160]
                }
            },
            {
                "title": "Strategic Recommendations",
                "content": "**Action Items:** Based on the analysis, key recommendations include market expansion, technology investment, and strategic partnerships. **Implementation Roadmap:** A phased approach is recommended with clear milestones and success metrics. **Risk Mitigation:** Comprehensive risk assessment frameworks should be implemented.",
                "chart_type": "none",
                "chart_data": {}
            }
        ]
        
        return {"sections": sections}

    def _add_fixed_executive_summary(self, json_data: Dict[str, Any], query: str, report_type: ReportType) -> Dict[str, Any]:
        """Add a fixed Executive Summary to the report blueprint."""
        if not isinstance(json_data, dict) or 'sections' not in json_data:
            return json_data
        
        sections = json_data['sections']
        if not isinstance(sections, list) or len(sections) == 0:
            return json_data
        
        # Find the Executive Summary section
        executive_summary_section = next((section for section in sections if section['title'] == 'Executive Summary'), None)
        if not executive_summary_section:
            return json_data
        
        # Create fixed Executive Summary (150-200 words) following the specified structure
        executive_summary = self._generate_fixed_executive_summary(query, report_type)
        executive_summary_section['content'] = executive_summary
        
        # Apply intelligent chart decisions to all sections
        for section in sections:
            if section['title'] != 'Executive Summary':  # Skip Executive Summary
                content_length = len(section.get('content', '').split())
                
                # Determine if this section should have a chart
                should_include = self._should_include_chart(section['title'], content_length)
                
                if should_include:
                    # Suggest appropriate chart type based on section title
                    suggested_type = self._suggest_chart_type(section['title'])
                    section['chart_type'] = suggested_type
                    
                    # Generate appropriate chart data based on the suggested type
                    section['chart_data'] = self._generate_chart_data_for_type(suggested_type, section['title'])
                else:
                    section['chart_type'] = 'none'
                    section['chart_data'] = {}
        
        return json_data
    
    def _generate_chart_data_for_type(self, chart_type: str, section_title: str) -> Dict[str, Any]:
        """Generate appropriate chart data based on chart type and section context."""
        title_lower = section_title.lower()
        
        if chart_type == 'bar':
            return {
                "labels": ["Category A", "Category B", "Category C", "Category D"],
                "values": [30, 25, 20, 25]
            }
        elif chart_type == 'line':
            return {
                "labels": ["2020", "2021", "2022", "2023", "2024"],
                "values": [100, 115, 130, 145, 160]
            }
        elif chart_type == 'pie':
            return {
                "labels": ["Segment A", "Segment B", "Segment C", "Segment D"],
                "values": [35, 30, 20, 15]
            }
        elif chart_type == 'radar':
            return {
                "labels": ["Quality", "Price", "Service", "Innovation", "Brand"],
                "values": [85, 70, 90, 75, 80]
            }
        elif chart_type == 'waterfall':
            return {
                "labels": ["Start", "Revenue", "Costs", "Taxes", "End"],
                "values": [100, 50, -30, -10, 110]
            }
        elif chart_type == 'funnel':
            return {
                "labels": ["Leads", "Qualified", "Proposals", "Negotiations", "Closed"],
                "values": [1000, 800, 600, 400, 200]
            }
        elif chart_type == 'scatter':
            return {
                "labels": ["Point A", "Point B", "Point C", "Point D"],
                "x_values": [10, 20, 30, 40],
                "y_values": [5, 15, 25, 35],
                "sizes": [100, 200, 150, 300]
            }
        elif chart_type == 'heatmap':
            return {
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "categories": ["North", "South", "East", "West"],
                "values": [[10, 20, 30, 40], [15, 25, 35, 45], [20, 30, 40, 50], [25, 35, 45, 55]]
            }
        elif chart_type == 'gauge':
            return {
                "value": 75,
                "max": 100,
                "label": "Performance Score"
            }
        elif chart_type == 'stackedBar':
            return {
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "series": [
                    {"name": "Product A", "values": [10, 15, 20, 25]},
                    {"name": "Product B", "values": [5, 12, 18, 22]}
                ]
            }
        elif chart_type == 'multiLine':
            return {
                "labels": ["Jan", "Feb", "Mar", "Apr"],
                "series": [
                    {"name": "Revenue", "values": [100, 120, 140, 160]},
                    {"name": "Profit", "values": [20, 25, 30, 35]}
                ]
            }
        elif chart_type == 'bubble':
            return {
                "labels": ["Market A", "Market B", "Market C"],
                "x_values": [10, 20, 30],
                "y_values": [5, 15, 25],
                "sizes": [200, 300, 250]
            }
        elif chart_type == 'candlestick':
            return {
                "labels": ["Day1", "Day2", "Day3", "Day4"],
                "open": [100, 105, 110, 108],
                "high": [110, 115, 120, 118],
                "low": [95, 100, 105, 103],
                "close": [105, 110, 115, 113]
            }
        elif chart_type == 'boxPlot':
            return {
                "labels": ["Group A", "Group B", "Group C"],
                "data": [[10, 15, 20, 25, 30], [12, 18, 22, 28, 35], [8, 12, 18, 24, 32]]
            }
        elif chart_type == 'histogram':
            return {
                "labels": ["0-10", "11-20", "21-30", "31-40"],
                "values": [5, 12, 8, 3]
            }
        elif chart_type == 'pareto':
            return {
                "labels": ["Issue A", "Issue B", "Issue C", "Issue D"],
                "values": [40, 30, 20, 10],
                "cumulative": [40, 70, 90, 100]
            }
        elif chart_type == 'flowchart':
            return {
                "nodes": [
                    {"id": "start", "label": "Start", "type": "start"},
                    {"id": "process1", "label": "Process Step 1", "type": "process"},
                    {"id": "decision", "label": "Decision Point", "type": "decision"},
                    {"id": "process2", "label": "Process Step 2", "type": "process"},
                    {"id": "end", "label": "End", "type": "end"}
                ],
                "connections": [
                    {"from": "start", "to": "process1", "label": "Begin"},
                    {"from": "process1", "to": "decision", "label": "Evaluate"},
                    {"from": "decision", "to": "process2", "label": "Yes"},
                    {"from": "decision", "to": "end", "label": "No"},
                    {"from": "process2", "to": "end", "label": "Complete"}
                ]
            }
        else:
            return {}
    
    def _generate_fixed_executive_summary(self, query: str, report_type: ReportType) -> str:
        """Generate a fixed Executive Summary with the specified structure (150-200 words)."""
        
        # Base overview paragraph
        overview = f"This comprehensive report analyzes {query}, providing critical insights into market dynamics, competitive landscape, and strategic opportunities. The analysis leverages industry data, trend analysis, and expert perspectives to deliver actionable intelligence for stakeholders."
        
        # Key findings (3-5 bullet points)
        key_findings = [
            f"**Market Growth:** The {query.lower()} market demonstrates robust growth potential with projected expansion rates exceeding industry averages",
            f"**Competitive Dynamics:** Intense competition characterizes the landscape, with both established players and emerging disruptors vying for market share",
            f"**Technology Impact:** Digital transformation and technological innovation are driving fundamental changes in market structure and customer behavior",
            f"**Regulatory Environment:** Evolving regulatory frameworks present both challenges and opportunities for market participants",
            f"**Customer Preferences:** Shifting consumer demands and preferences are reshaping product development and service delivery models"
        ]
        
        # Primary recommendations
        primary_recommendations = [
            f"**Strategic Positioning:** Develop differentiated value propositions that address evolving customer needs and market gaps",
            f"**Technology Investment:** Prioritize digital transformation initiatives to enhance operational efficiency and customer engagement",
            f"**Partnership Strategy:** Forge strategic alliances and partnerships to expand market reach and capabilities",
            f"**Risk Management:** Implement comprehensive risk assessment frameworks to navigate regulatory and market uncertainties"
        ]
        
        # Combine all elements
        executive_summary = f"{overview}\n\n**Key Findings:**\n"
        for finding in key_findings[:4]:  # Use 4 findings to keep within word limit
            executive_summary += f"- {finding}\n"
        
        executive_summary += "\n**Primary Recommendations:**\n"
        for recommendation in primary_recommendations[:3]:  # Use 3 recommendations
            executive_summary += f"- {recommendation}\n"
        
        return executive_summary 