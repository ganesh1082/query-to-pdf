#!/usr/bin/env python3
"""
Enhanced Content Generator - Creates comprehensive, detailed content and dynamic chart selection
based on Firecrawl research data with intelligent analysis and explanations.
"""

import asyncio
import json
import re
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EnhancedContentGenerator:
    """Generate comprehensive, detailed content and dynamic charts based on research data"""
    
    def __init__(self, gemini_api_key: str):
        """Initialize the content generator"""
        self.gemini_api_key = gemini_api_key
        
        # Initialize Gemini
        self.model: Optional[Any] = None
        try:
            genai.configure(api_key=gemini_api_key)
            model_version = os.getenv('GEMINI_MODEL_VERSION', 'gemini-2.0-flash')
            self.model = genai.GenerativeModel(model_version)
            print(f"✅ Enhanced Content Generator initialized with Gemini API ({model_version})")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
            self.model = None
    
    async def generate_comprehensive_sections(self, query: str, learnings: List[str], sources: List[Dict], page_count: int = 8) -> Dict[str, Any]:
        """Generate comprehensive sections with detailed content and dynamic chart selection"""
        if not self.model:
            print("❌ Gemini not available for content generation")
            return self._get_fallback_sections(query)
        
        print(f"🧠 Generating comprehensive sections for: {query}")
        print(f"📊 Using {len(learnings)} learnings and {len(sources)} sources")
        
        # Calculate number of sections based on page count and content richness
        num_sections = max(8, int(page_count * 1.2))  # More sections for comprehensive coverage
        
        # Create comprehensive prompt for detailed content generation
        prompt = self._create_comprehensive_prompt(query, learnings, sources, num_sections, page_count)
        
        try:
            print(f"🎯 Generating {num_sections} comprehensive sections...")
            
            generation_config = genai.types.GenerationConfig(
                temperature=0.4,  # Slightly higher for more creative content
                max_output_tokens=32768,  # Higher token limit for detailed content
                top_p=0.9,
                top_k=40
            )
            
            response = await self.model.generate_content_async(prompt, generation_config=generation_config)
            
            print(f"📝 AI Response received: {len(response.text)} characters")
            
            # Extract and validate JSON
            json_data = self._extract_and_validate_json(response.text)
            
            if json_data and self._validate_sections_structure(json_data):
                print("✅ Successfully generated comprehensive sections")
                return json_data
            else:
                print("❌ Invalid JSON structure. Using fallback data.")
                # Save the raw response for debugging
                with open("debug_ai_response.txt", "w") as f:
                    f.write(response.text)
                print("💾 Raw AI response saved to debug_ai_response.txt for debugging")
                return self._get_fallback_sections(query)
                
        except Exception as e:
            print(f"❌ Error in content generation: {e}")
            return self._get_fallback_sections(query)
    
    def _create_comprehensive_prompt(self, query: str, learnings: List[str], sources: List[Dict], num_sections: int, page_count: int) -> str:
        """Create a comprehensive prompt for detailed content generation"""
        
        # Calculate target content length per section - MUCH HIGHER for comprehensive content
        target_words_per_section = max(3000, int((page_count * 3000) / num_sections))  # 3000+ words per section
        
        # Process learnings for better context
        processed_learnings = []
        for i, learning in enumerate(learnings[:20]):  # Use more learnings
            # Extract key data points
            percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', learning)
            amounts = re.findall(r'\$(\d+(?:\.\d+)?)\s*(?:billion|million|thousand)?', learning)
            years = re.findall(r'20(?:2[0-9]|1[0-9])', learning)
            
            processed_learning = {
                "text": learning,
                "percentages": [float(p) for p in percentages],
                "amounts": [float(a) for a in amounts],
                "years": [int(y) for y in years],
                "has_data": len(percentages) > 0 or len(amounts) > 0 or len(years) > 0
            }
            processed_learnings.append(processed_learning)
        
        # Group learnings by themes
        data_rich_learnings = [l for l in processed_learnings if l["has_data"]]
        trend_learnings = [l for l in processed_learnings if any(y >= 2020 for y in l["years"])]
        percentage_learnings = [l for l in processed_learnings if l["percentages"]]
        amount_learnings = [l for l in processed_learnings if l["amounts"]]
        
        # Create learnings summary for context
        learnings_summary = f"""
RESEARCH DATA SUMMARY:
- Total learnings: {len(learnings)}
- Data-rich learnings: {len(data_rich_learnings)}
- Trend analysis learnings: {len(trend_learnings)}
- Percentage-based insights: {len(percentage_learnings)}
- Financial/amount insights: {len(amount_learnings)}

KEY DATA POINTS EXTRACTED:
"""
        
        # Add key data points
        all_percentages = []
        all_amounts = []
        all_years = []
        
        for learning in processed_learnings:
            all_percentages.extend(learning["percentages"])
            all_amounts.extend(learning["amounts"])
            all_years.extend(learning["years"])
        
        if all_percentages:
            learnings_summary += f"- Percentage data points: {len(all_percentages)} (range: {min(all_percentages):.1f}% - {max(all_percentages):.1f}%)\n"
        if all_amounts:
            learnings_summary += f"- Financial data points: {len(all_amounts)} (range: ${min(all_amounts):.1f} - ${max(all_amounts):.1f})\n"
        if all_years:
            learnings_summary += f"- Time period: {min(all_years)} - {max(all_years)}\n"
        
        # Add sample learnings for context
        learnings_summary += "\nSAMPLE RESEARCH INSIGHTS:\n"
        for i, learning in enumerate(processed_learnings[:10]):
            learnings_summary += f"{i+1}. {learning['text']}\n"
        
        # Source reliability analysis
        sources_summary = ""
        if sources:
            high_reliability = [s for s in sources if s.get("reliability_score", 0) > 0.8]
            medium_reliability = [s for s in sources if 0.6 <= s.get("reliability_score", 0) <= 0.8]
            
            sources_summary = f"""
SOURCE RELIABILITY ANALYSIS:
- Total sources: {len(sources)}
- High reliability (0.8+): {len(high_reliability)}
- Medium reliability (0.6-0.8): {len(medium_reliability)}
- Average reliability: {sum(s.get("reliability_score", 0) for s in sources) / len(sources):.2f}
"""
        
        # Available chart types for dynamic selection
        chart_types = [
            "bar", "horizontalBar", "line", "area", "pie", "donut", "scatter", "bubble",
            "radar", "waterfall", "funnel", "gauge", "heatmap", "treeMap", "sunburst",
            "candlestick", "boxPlot", "violinPlot", "histogram", "pareto", "stackedBar",
            "multiLine", "none"
        ]
        
        prompt = f"""You are an expert research analyst and report writer. Create a comprehensive, detailed, and analytically rich {page_count}-page report for: "{query}"

CRITICAL: Output ONLY valid JSON. No explanations, no markdown formatting, just pure JSON.

{learnings_summary}{sources_summary}

REPORT REQUIREMENTS:
- Target sections: {num_sections} (minimum, can be more if content requires it)
- Target length: {page_count} pages
- Target content per section: {target_words_per_section} words minimum
- Content must be extremely detailed, analytical, and comprehensive
- Each section should be unique, non-repetitive, and deeply insightful
- Use research data as evidence and foundation for analysis
- Create dynamic, relevant section titles based on the research findings
- Include detailed explanations for all charts and data visualizations

CONTENT STRUCTURE REQUIREMENTS:
1. EXECUTIVE SUMMARY: Comprehensive overview with key findings and strategic implications
2. MARKET OVERVIEW: Detailed market analysis with size, growth, and key drivers
3. COMPETITIVE LANDSCAPE: In-depth competitive analysis with market positioning
4. TECHNOLOGY TRENDS: Current and emerging technology trends with detailed analysis
5. ADOPTION PATTERNS: Detailed analysis of adoption rates, barriers, and success factors
6. FINANCIAL IMPACT: Comprehensive financial analysis with ROI and cost-benefit analysis
7. REGIONAL ANALYSIS: Geographic and regional variations in adoption and trends
8. FUTURE OUTLOOK: Detailed projections and strategic recommendations
9. RISK ASSESSMENT: Comprehensive risk analysis and mitigation strategies
10. STRATEGIC RECOMMENDATIONS: Actionable insights and strategic guidance

RESEARCH DATA INTEGRATION REQUIREMENTS:
- Use specific learnings as evidence and examples throughout each section
- Reference actual data points, percentages, and statistics from the research
- Include source reliability information when citing specific findings
- Build comprehensive analysis around the research data rather than generic statements
- Ensure every major claim is supported by research evidence
- Use learnings to provide concrete examples and case studies
- Integrate research findings naturally into flowing paragraphs

ADDITIONAL SECTIONS (create as many as needed based on research depth):
- Industry-specific analysis
- Customer behavior and preferences
- Regulatory environment and compliance
- Supply chain and ecosystem analysis
- Innovation and R&D trends
- Workforce and skills analysis
- Environmental and sustainability impact
- Digital transformation strategies
- Investment and funding analysis
- Partnership and collaboration trends

CONTENT QUALITY REQUIREMENTS:
1. Each section must contain extremely detailed, comprehensive content (minimum {target_words_per_section} words)
2. Include specific data points, statistics, and examples with detailed explanations
3. Use ONLY paragraph format - NO bullet points, NO subtitles, NO headings within content
4. Provide analytical insights and expert commentary with detailed reasoning
5. Include relevant industry context and background information
6. Make content engaging and informative for professional audience
7. EXPAND on each point with detailed explanations and examples
8. Include multiple paragraphs with comprehensive analysis
9. Add industry-specific terminology and expert insights
10. Provide detailed market trends and future projections
11. Include competitive analysis and strategic implications
12. Use research learnings as evidence and foundation for analysis - INTEGRATE learnings naturally into paragraphs
13. Include detailed chart explanations and data interpretation
14. Provide context for all data points and their significance
15. Write in flowing, narrative style with smooth transitions between paragraphs
16. Use research data to support every major claim and insight
17. Create comprehensive analysis that builds upon the research findings
18. Ensure each paragraph flows naturally into the next without breaks or lists

DYNAMIC CHART SELECTION GUIDELINES:
Choose chart types based on the analytical goal and available data:

- TREND ANALYSIS: Use 'line', 'area', 'multiLine' for time-series data and growth patterns
- COMPARATIVE ANALYSIS: Use 'bar', 'horizontalBar', 'radar' for competitive analysis and rankings
- COMPOSITION ANALYSIS: Use 'pie', 'donut', 'stackedBar', 'treeMap' for market segmentation and breakdowns
- CORRELATION ANALYSIS: Use 'scatter', 'bubble', 'heatmap' for relationship analysis
- DISTRIBUTION ANALYSIS: Use 'histogram', 'boxPlot', 'violinPlot' for statistical analysis
- FLOW ANALYSIS: Use 'waterfall', 'funnel' for process and conversion analysis
- PERFORMANCE METRICS: Use 'gauge', 'pareto' for KPI and performance analysis
- HIERARCHICAL DATA: Use 'treeMap', 'sunburst' for organizational and categorical data
- FINANCIAL DATA: Use 'candlestick', 'waterfall' for financial and investment analysis
- GEOGRAPHIC DATA: Use 'heatmap' for regional and location-based analysis

CHART DATA REQUIREMENTS:
- Use ONLY real data extracted from the research learnings
- Create meaningful labels based on the actual data context
- Ensure data values are realistic and based on research findings
- Provide detailed explanations for what each chart represents
- Include data interpretation and insights in the content

AVAILABLE CHART TYPES: {chart_types}

REQUIRED JSON FORMAT:
{{
  "sections": [
    {{
      "title": "Executive Summary",
      "content": "COMPREHENSIVE EXECUTIVE SUMMARY with detailed overview, key findings, strategic implications, and market insights. Include specific data points and actionable recommendations. Write in flowing paragraph format with no bullet points or subtitles.",
      "chart_type": "none",
      "chart_data": {{}},
      "chart_explanation": ""
    }},
    {{
      "title": "DYNAMIC SECTION TITLE",
      "content": "EXTREMELY DETAILED CONTENT (minimum {target_words_per_section} words) with comprehensive analysis, data interpretation, expert insights, and detailed explanations. Include multiple paragraphs, specific examples, and detailed reasoning. Write in flowing paragraph format with no bullet points or subtitles. Use research learnings as evidence throughout the content.",
      "chart_type": "CHART_TYPE_BASED_ON_CONTENT",
      "chart_data": {{
        "labels": ["REAL_DATA_LABELS"],
        "values": [REAL_DATA_VALUES]
      }},
      "chart_explanation": "DETAILED EXPLANATION of what the chart shows, how to interpret it, and what insights it provides. Include data context and strategic implications."
    }}
  ]
}}

CHART DATA EXAMPLES (use real data from research):
- Bar chart: {{"labels": ["Category A", "Category B", "Category C"], "values": [REAL_PERCENTAGES]}}
- Line chart: {{"labels": ["2020", "2021", "2022", "2023", "2024"], "values": [REAL_TREND_DATA]}}
- Pie chart: {{"labels": ["Segment 1", "Segment 2", "Segment 3"], "values": [REAL_DISTRIBUTION_DATA]}}
- Scatter plot: {{"labels": ["Point1", "Point2", "Point3"], "x_values": [REAL_X_DATA], "y_values": [REAL_Y_DATA]}}
- Waterfall chart: {{"labels": ["Start", "Revenue", "Costs", "Taxes", "End"], "values": [REAL_FINANCIAL_DATA]}}

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
    
    def _extract_and_validate_json(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract and validate JSON from AI response with improved parsing for large responses"""
        try:
            # Clean the response text
            cleaned_text = self._clean_response_text(response_text)
            
            print(f"🔍 Attempting JSON extraction from {len(cleaned_text)} characters...")
            
            # Try multiple extraction strategies
            json_data = None
            
            # Strategy 1: Direct JSON extraction
            json_data = self._extract_json_strategy_1(cleaned_text)
            if json_data:
                print("✅ Strategy 1 (Direct JSON) succeeded")
                return json_data
            
            # Strategy 2: Code block extraction
            json_data = self._extract_json_strategy_2(cleaned_text)
            if json_data:
                print("✅ Strategy 2 (Code block) succeeded")
                return json_data
            
            # Strategy 3: Brace-based extraction
            json_data = self._extract_json_strategy_3(cleaned_text)
            if json_data:
                print("✅ Strategy 3 (Brace-based) succeeded")
                return json_data
            
            # Strategy 4: Aggressive repair
            json_data = self._extract_json_strategy_4(cleaned_text)
            if json_data:
                print("✅ Strategy 4 (Aggressive repair) succeeded")
                return json_data
            
            # Strategy 5: Truncate and try again (for very long responses)
            json_data = self._extract_json_strategy_5(cleaned_text)
            if json_data:
                print("✅ Strategy 5 (Truncate) succeeded")
                return json_data
            
            # Strategy 6: NEW - Handle very large responses with better parsing
            json_data = self._extract_json_strategy_6(cleaned_text)
            if json_data:
                print("✅ Strategy 6 (Large response) succeeded")
                return json_data
            
            # Strategy 7: NEW - Handle extremely large responses with chunked parsing
            json_data = self._extract_json_strategy_7(cleaned_text)
            if json_data:
                print("✅ Strategy 7 (Chunked parsing) succeeded")
                return json_data
            
            print("❌ All JSON extraction strategies failed")
            return None
            
        except Exception as e:
            print(f"❌ Error extracting JSON: {e}")
            return None
    
    def _clean_response_text(self, text: str) -> str:
        """Clean response text for JSON extraction"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*$', '', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _extract_json_strategy_1(self, text: str) -> Optional[Dict[str, Any]]:
        """Strategy 1: Direct JSON parsing"""
        try:
            return json.loads(text)
        except:
            return None
    
    def _extract_json_strategy_2(self, text: str) -> Optional[Dict[str, Any]]:
        """Strategy 2: Extract from code blocks"""
        try:
            # Look for JSON-like content between braces
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                json_str = match.group()
                # Try to clean up the JSON string
                json_str = self._repair_json_aggressive(json_str)
                return json.loads(json_str)
        except Exception as e:
            print(f"Strategy 2 failed: {e}")
        return None
    
    def _extract_json_strategy_3(self, text: str) -> Optional[Dict[str, Any]]:
        """Strategy 3: Brace-based extraction"""
        try:
            # Find the outermost braces
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = text[start:end+1]
                return json.loads(json_str)
        except:
            pass
        return None
    
    def _extract_json_strategy_4(self, text: str) -> Optional[Dict[str, Any]]:
        """Strategy 4: Aggressive repair and extraction"""
        try:
            # Try to repair common JSON issues
            repaired_text = self._repair_json_aggressive(text)
            return json.loads(repaired_text)
        except:
            pass
        return None
    
    def _extract_json_strategy_5(self, text: str) -> Optional[Dict[str, Any]]:
        """Strategy 5: Truncate and try again for very long responses"""
        try:
            # For very long responses, try to extract just the first complete JSON object
            # Look for the start of the JSON
            start = text.find('{')
            if start == -1:
                return None
            
            # Find the matching closing brace by counting braces
            brace_count = 0
            end = start
            
            for i, char in enumerate(text[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            if end > start:
                json_str = text[start:end]
                # Try to repair and parse
                repaired_json = self._repair_json_aggressive(json_str)
                return json.loads(repaired_json)
        except Exception as e:
            print(f"Strategy 5 failed: {e}")
        return None
    
    def _extract_json_strategy_6(self, text: str) -> Optional[Dict[str, Any]]:
        """Strategy 6: Handle very large responses with better parsing"""
        try:
            # For very large responses, try a more sophisticated approach
            # Look for the largest JSON object by finding all brace pairs
            brace_pairs = []
            stack = []
            
            for i, char in enumerate(text):
                if char == '{':
                    stack.append(i)
                elif char == '}':
                    if stack:
                        start = stack.pop()
                        if not stack:  # Complete object
                            brace_pairs.append((start, i + 1))
            
            if not brace_pairs:
                return None
            
            # Sort by size (largest first)
            brace_pairs.sort(key=lambda x: x[1] - x[0], reverse=True)
            
            # Try each pair, starting with the largest
            for start, end in brace_pairs:
                try:
                    json_str = text[start:end]
                    
                    # Try multiple repair strategies
                    repaired_strategies = [
                        json_str,  # Original
                        self._repair_json_aggressive(json_str),  # Aggressive repair
                        self._repair_json_minimal(json_str),  # Minimal repair
                    ]
                    
                    for repaired in repaired_strategies:
                        try:
                            result = json.loads(repaired)
                            # Validate that it has the expected structure
                            if isinstance(result, dict) and "sections" in result:
                                return result
                        except json.JSONDecodeError:
                            continue
                            
                except Exception as e:
                    print(f"Strategy 6 attempt failed: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"Strategy 6 failed: {e}")
            return None
    
    def _extract_json_strategy_7(self, text: str) -> Optional[Dict[str, Any]]:
        """Strategy 7: Handle extremely large responses with smart truncation"""
        try:
            # For very large responses, the JSON might be getting cut off
            # Try to find the complete JSON by looking for the end of the last complete section
            
            # Look for the pattern that indicates the end of a complete section
            # This is more reliable than just counting braces for very large JSON
            
            # Find all occurrences of "chart_explanation" followed by closing braces
            import re
            pattern = r'"chart_explanation":\s*"[^"]*"\s*}\s*}\s*'
            matches = list(re.finditer(pattern, text))
            
            if matches:
                # Take the last complete match
                last_match = matches[-1]
                end_pos = last_match.end()
                
                # Find the start of the JSON
                start_pos = text.find('{')
                if start_pos != -1 and end_pos > start_pos:
                    json_str = text[start_pos:end_pos]
                    
                    # Try to repair and parse
                    repaired_json = self._repair_json_aggressive(json_str)
                    try:
                        result = json.loads(repaired_json)
                        if isinstance(result, dict) and "sections" in result:
                            return result
                    except json.JSONDecodeError:
                        pass
            
            # Fallback: try to find the largest complete JSON object
            # by looking for the pattern that indicates a complete sections array
            pattern2 = r'"sections":\s*\[.*?\]\s*}\s*$'
            matches2 = list(re.finditer(pattern2, text, re.DOTALL))
            
            if matches2:
                last_match2 = matches2[-1]
                end_pos2 = last_match2.end()
                start_pos2 = text.find('{')
                
                if start_pos2 != -1 and end_pos2 > start_pos2:
                    json_str2 = text[start_pos2:end_pos2]
                    repaired_json2 = self._repair_json_aggressive(json_str2)
                    try:
                        result2 = json.loads(repaired_json2)
                        if isinstance(result2, dict) and "sections" in result2:
                            return result2
                    except json.JSONDecodeError:
                        pass
            
            return None
            
        except Exception as e:
            print(f"Strategy 7 failed: {e}")
            return None
    
    def _repair_json_aggressive(self, json_str: str) -> str:
        """Aggressively repair JSON string"""
        # Remove any text before the first {
        start = json_str.find('{')
        if start != -1:
            json_str = json_str[start:]
        
        # Remove any text after the last }
        end = json_str.rfind('}')
        if end != -1:
            json_str = json_str[:end+1]
        
        # Fix common issues
        json_str = re.sub(r'(["\w])\s*\n\s*(["\w])', r'\1 \2', json_str)  # Remove newlines between properties
        json_str = re.sub(r',\s*}', r'}', json_str)  # Remove trailing commas
        json_str = re.sub(r',\s*]', r']', json_str)  # Remove trailing commas in arrays
        
        return json_str
    
    def _repair_json_minimal(self, json_str: str) -> str:
        """Minimal JSON repair for basic issues"""
        # Remove any text before the first {
        start = json_str.find('{')
        if start != -1:
            json_str = json_str[start:]
        
        # Remove any text after the last }
        end = json_str.rfind('}')
        if end != -1:
            json_str = json_str[:end+1]
        
        # Fix basic issues
        json_str = re.sub(r',\s*}', r'}', json_str)  # Remove trailing commas
        json_str = re.sub(r',\s*]', r']', json_str)  # Remove trailing commas in arrays
        
        return json_str
    
    def _validate_sections_structure(self, data: Dict[str, Any]) -> bool:
        """Validate the structure of generated sections"""
        try:
            if not isinstance(data, dict):
                return False
            
            if "sections" not in data:
                return False
            
            sections = data["sections"]
            if not isinstance(sections, list):
                return False
            
            if len(sections) < 3:  # Minimum sections
                return False
            
            # Validate each section
            for section in sections:
                if not isinstance(section, dict):
                    return False
                
                required_fields = ["title", "content", "chart_type"]
                for field in required_fields:
                    if field not in section:
                        return False
                
                # Check content length - much higher for comprehensive content
                if len(section["content"]) < 2000:  # Minimum content length for comprehensive sections
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False
    
    def _get_fallback_sections(self, query: str) -> Dict[str, Any]:
        """Get fallback sections if AI generation fails"""
        return {
            "sections": [
                {
                    "title": "Executive Summary",
                    "content": f"This comprehensive report analyzes {query} with detailed insights and strategic recommendations. The analysis covers market trends, competitive landscape, and future opportunities in this dynamic sector.",
                    "chart_type": "none",
                    "chart_data": {},
                    "chart_explanation": ""
                },
                {
                    "title": "Market Overview",
                    "content": f"The {query} market represents a significant opportunity with strong growth potential. This section provides a detailed analysis of market size, key drivers, and growth trends.",
                    "chart_type": "bar",
                    "chart_data": {
                        "labels": ["Market Size", "Growth Rate", "Adoption Rate", "Investment", "ROI"],
                        "values": [75, 25, 60, 80, 45]
                    },
                    "chart_explanation": "This chart shows key market metrics including market size, growth rate, adoption rate, investment levels, and return on investment."
                }
            ]
        }


async def main():
    """Test the enhanced content generator"""
    print("🧪 Testing Enhanced Content Generator")
    
    # Load environment variables
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return
    
    # Initialize the generator
    generator = EnhancedContentGenerator(gemini_api_key)
    
    # Sample data for testing
    sample_learnings = [
        "AI adoption in enterprise software reached 78% by 2024, up from 65% in 2023",
        "Organizations using AI reported 42% increase in productivity",
        "AI investment in enterprise software exceeded $4.4 trillion in 2024",
        "71% of organizations regularly use generative AI in business functions",
        "AI adoption in IT departments increased by 35% compared to 2023",
        "Companies reported 27% cost reduction through AI implementation",
        "AI market is expected to grow by 37% annually through 2027",
        "92% of companies plan to increase AI investments over the next three years",
        "AI implementation led to 45% improvement in customer satisfaction",
        "Organizations saw 30% reduction in operational costs with AI"
    ]
    
    sample_sources = [
        {
            "url": "https://mckinsey.com/ai-adoption-report-2024",
            "domain": "mckinsey.com",
            "reliability_score": 0.85,
            "reliability_reasoning": "Reputable global consulting firm with strong research methodology",
            "title": "AI Adoption in Enterprise Software 2024",
            "content_length": 8000
        }
    ]
    
    # Test content generation
    result = await generator.generate_comprehensive_sections(
        query="AI adoption in enterprise software",
        learnings=sample_learnings,
        sources=sample_sources,
        page_count=8
    )
    
    if result and "sections" in result:
        print(f"✅ Generated {len(result['sections'])} comprehensive sections")
        for i, section in enumerate(result["sections"]):
            print(f"  {i+1}. {section['title']} ({len(section['content'])} chars, chart: {section['chart_type']})")
    else:
        print("❌ Failed to generate comprehensive sections")


if __name__ == "__main__":
    asyncio.run(main()) 