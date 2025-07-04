#!/usr/bin/env python3
"""
Firecrawl Research Module - Real-time web scraping and AI-powered report generation
"""

import os
import json
import asyncio
import time
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass
from urllib.parse import urlparse
import requests
import google.generativeai as genai
from datetime import datetime
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class SourceMetadata:
    """Metadata about a source"""
    url: str
    title: Optional[str] = None
    domain: Optional[str] = None
    reliability_score: float = 0.5
    reliability_reasoning: str = ""
    content_length: int = 0
    last_checked: Optional[str] = None


@dataclass
class ResearchLearning:
    """A learning from research with reliability score"""
    content: str
    reliability: float
    sources: List[str]
    data_type: str = "regular"


@dataclass
class ResearchProgress:
    """Progress tracking for research"""
    current_depth: int
    total_depth: int
    current_breadth: int
    total_breadth: int
    current_query: Optional[str] = None
    total_queries: int = 0
    completed_queries: int = 0
    learnings_count: int = 0


class FirecrawlResearch:
    """Real-time web research using Firecrawl and Gemini"""
    
    def __init__(self, firecrawl_api_key: Optional[str] = None, gemini_api_key: Optional[str] = None):
        """Initialize with API keys"""
        self.firecrawl_api_key = firecrawl_api_key or os.getenv('FIRECRAWL_API_KEY')
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        
        # Initialize Gemini
        self.gemini_model: Optional[Any] = None
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                model_version = os.getenv('GEMINI_MODEL_VERSION', 'gemini-2.0-flash')
                self.gemini_model = genai.GenerativeModel(model_version)
                print(f"✅ Gemini API initialized ({model_version})")
            except Exception as e:
                print(f"❌ Failed to initialize Gemini: {e}")
        
        # Rate limiting for Firecrawl
        self.rate_limits = {
            'search': {
                'limit': int(os.getenv('FIRECRAWL_RATE_LIMIT_SEARCH', 50)), 
                'window': int(os.getenv('FIRECRAWL_RATE_LIMIT_WINDOW', 60000)), 
                'requests': 0, 
                'reset_time': 0.0
            },
            'scrape': {
                'limit': int(os.getenv('FIRECRAWL_RATE_LIMIT_SCRAPE', 100)), 
                'window': int(os.getenv('FIRECRAWL_RATE_LIMIT_WINDOW', 60000)), 
                'requests': 0, 
                'reset_time': 0.0
            }
        }
        
        # Credit tracking
        self.credit_costs = {
            'search': 1,
            'scrape': 1
        }
        self.current_credits = 0
        self.max_credits_per_query = int(os.getenv('FIRECRAWL_MAX_CREDITS_PER_QUERY', 20))
        
        print(f"🔥 Firecrawl Research initialized")
    
    async def check_rate_limit(self, endpoint: str) -> None:
        """Check and handle rate limiting"""
        now = time.time() * 1000
        state = self.rate_limits[endpoint]
        limits = self.rate_limits[endpoint]
        
        # Reset counter if window has passed
        if now >= state['reset_time']:
            state['requests'] = 0
            state['reset_time'] = now + limits['window']
        
        # Check if we're at the limit
        if state['requests'] >= limits['limit']:
            wait_time = state['reset_time'] - now
            print(f"⏱️ Rate limit reached for {endpoint}. Waiting {int(wait_time/1000)}s...")
            await asyncio.sleep(wait_time/1000 + 1)
            state['requests'] = 0
            state['reset_time'] = now + limits['window']
        
        state['requests'] += 1
    
    def check_credit_limit(self, operation: str) -> bool:
        """Check if we can afford the operation"""
        cost = self.credit_costs[operation]
        if self.current_credits + cost > self.max_credits_per_query:
            print(f"🚫 Credit limit reached! Would use {self.current_credits + cost} credits")
            return False
        return True
    
    def track_credit_usage(self, operation: str) -> None:
        """Track credit usage"""
        cost = self.credit_costs[operation]
        self.current_credits += cost
        if self.current_credits > self.max_credits_per_query * 0.8:
            print(f"⚠️ Credits: {self.current_credits}/{self.max_credits_per_query}")
    
    def reset_credits(self) -> None:
        """Reset credit tracking for new query"""
        self.current_credits = 0
    
    async def search_with_retry(self, query: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Search with retry logic and better credit management"""
        for attempt in range(max_retries):
            try:
                # Check credit limit before making request
                if not self.check_credit_limit("search"):
                    print(f"  ⚠️ Credit limit reached ({self.current_credits}/{self.max_credits_per_query})")
                    return None
                
                # Check rate limits
                await self.check_rate_limit("search")
                
                # Make the search request
                response = await self._make_search_request(query)
                
                if response and response.get("success"):
                    self.track_credit_usage("search")
                    return response
                elif response and response.get("error"):
                    error_msg = response.get("error", "").lower()
                    if "insufficient credits" in error_msg or "payment required" in error_msg:
                        print(f"  ❌ Payment required (402): Your Firecrawl account needs credits or upgrade")
                        print(f"   Response: {response}")
                        return None
                    elif "rate limit" in error_msg:
                        print(f"  ⏳ Rate limited, waiting... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        print(f"  ⚠️ Search failed: {response.get('error')}")
                        return None
                else:
                    print(f"  ⚠️ Unexpected response format: {response}")
                    return None
                    
            except Exception as e:
                print(f"  ❌ Search error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                else:
                    return None
        
        return None
    
    async def evaluate_source_reliability(self, domain: str, context: str) -> Tuple[float, str]:
        """Evaluate source reliability using Gemini"""
        if not self.gemini_model:
            return 0.5, "No AI model available"
        
        try:
            prompt = f"""Evaluate the reliability of the following source domain for research about: "{context}"

Domain: {domain}

Consider factors like:
1. Editorial standards and fact-checking processes
2. Domain expertise in the subject matter
3. Reputation for accuracy and objectivity
4. Transparency about sources and methodology
5. Professional vs user-generated content
6. Commercial biases or conflicts of interest
7. Academic or professional credentials
8. Track record in the field

Return a reliability score between 0 and 1, where:
- 0.9-1.0: Highest reliability (e.g. peer-reviewed journals, primary sources)
- 0.7-0.89: Very reliable (e.g. respected news organizations)
- 0.5-0.69: Moderately reliable (e.g. industry blogs with editorial oversight)
- 0.3-0.49: Limited reliability (e.g. personal blogs, commercial sites)
- 0-0.29: Low reliability (e.g. known misinformation sources)

Respond with JSON format:
{{
  "score": 0.75,
  "reasoning": "Brief explanation of reliability assessment"
}}"""

            response = await self.gemini_model.generate_content_async(prompt)
            
            # Try to extract JSON from response
            try:
                # Find JSON in the response
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    return data.get('score', 0.5), data.get('reasoning', 'No reasoning provided')
            except:
                pass
            
            # Fallback: try to extract score from text
            score_match = re.search(r'"score":\s*([0-9.]+)', response.text)
            if score_match:
                score = float(score_match.group(1))
                return score, "Extracted from AI response"
            
            return 0.5, "Default reliability score"
            
        except Exception as e:
            print(f"❌ Error evaluating reliability: {e}")
            return 0.5, "Error in evaluation"
    
    async def generate_search_queries(self, query: str, learnings: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Generate search queries using Gemini"""
        if not self.gemini_model:
            return [{"query": query, "research_goal": "Basic research"}]
        
        try:
            learnings_context = ""
            if learnings:
                learnings_context = f"\nPrevious learnings:\n" + "\n".join([f"- {learning}" for learning in learnings[:5]])
            
            prompt = f"""Generate search queries to thoroughly research the following topic: "{query}"

Create specific, targeted search queries that will help find comprehensive information about this topic. Each query should be designed to uncover different aspects or angles of the research topic.

{learnings_context}

Generate 4-6 search queries that will effectively research different aspects of: {query}

Respond with JSON format:
{{
  "queries": [
    {{
      "query": "specific search query",
      "research_goal": "What this query aims to accomplish",
      "reliability_threshold": 0.6
    }}
  ]
}}"""

            response = await self.gemini_model.generate_content_async(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get('queries', [{"query": query, "research_goal": "Basic research"}])
            
            return [{"query": query, "research_goal": "Basic research"}]
            
        except Exception as e:
            print(f"❌ Error generating queries: {e}")
            return [{"query": query, "research_goal": "Basic research"}]
    
    async def process_search_results(self, query: str, result: Dict[str, Any], reliability_threshold: Optional[float] = None) -> Tuple[List[str], List[float], List[SourceMetadata]]:
        """Process search results and extract learnings"""
        if reliability_threshold is None:
            reliability_threshold = float(os.getenv('FIRECRAWL_RELIABILITY_THRESHOLD', 0.3))
        
        if not result or 'data' not in result:
            return [], [], []
        
        contents = []
        source_metadata = []
        
        # Process each search result
        for item in result['data']:
            if not item.get('markdown'):
                continue
            
            content = item['markdown']
            url = item.get('url', '')
            
            if not url:
                continue
            
            # Extract domain
            try:
                domain = urlparse(url).netloc
            except:
                domain = url
            
            # Evaluate reliability
            reliability_score, reasoning = await self.evaluate_source_reliability(domain, query)
            
            # Only include if above threshold
            if reliability_score >= reliability_threshold:
                contents.append(content)
                source_metadata.append(SourceMetadata(
                    url=url,
                    title=item.get('title'),
                    domain=domain,
                    reliability_score=reliability_score,
                    reliability_reasoning=reasoning,
                    content_length=len(content),
                    last_checked=datetime.now().isoformat()
                ))
        
        # Generate learnings from content using Gemini
        learnings, learning_reliabilities = await self.extract_learnings(contents, query)
        
        return learnings, learning_reliabilities, source_metadata
    
    async def extract_learnings(self, contents: List[str], query: str) -> Tuple[List[str], List[float]]:
        """Extract learnings from content using Gemini"""
        if not self.gemini_model or not contents:
            return [], []
        
        try:
            # Combine content (limit to avoid token limits)
            combined_content = "\n\n---\n\n".join(contents[:5])  # Limit to 5 sources
            if len(combined_content) > 15000:
                combined_content = combined_content[:15000] + "..."
            
            prompt = f"""Given the following contents from a search for the query "{query}", generate a list of learnings from the contents. Return a maximum of 15 learnings, but feel free to return less if the contents are clear. Make sure each learning is unique and not similar to each other. The learnings should be concise and to the point, as detailed and information dense as possible. Make sure to include any entities like people, places, companies, products, things, etc in the learnings, as well as any exact metrics, numbers, or dates.

Content:
{combined_content}

Respond with JSON format:
{{
  "learnings": [
    {{
      "content": "specific learning",
      "confidence": 0.8,
      "sources": ["domain1.com", "domain2.com"]
    }}
  ]
}}"""

            response = await self.gemini_model.generate_content_async(prompt)
            
            # Multiple strategies to extract JSON from response
            learnings, reliabilities = self._extract_learnings_from_response(response.text)
            
            if learnings:
                return learnings, reliabilities
            
            # Fallback: try to extract simple list format
            return self._extract_simple_learnings(response.text)
            
        except Exception as e:
            print(f"❌ Error extracting learnings: {e}")
            return [], []
    
    def _extract_learnings_from_response(self, response_text: str) -> Tuple[List[str], List[float]]:
        """Extract learnings from AI response using multiple strategies"""
        if not response_text:
            return [], []
        
        # Strategy 1: Try to find JSON object
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                # Clean up common JSON issues
                json_str = self._clean_json_string(json_str)
                data = json.loads(json_str)
                learnings = [item['content'] for item in data.get('learnings', [])]
                reliabilities = [item.get('confidence', 0.7) for item in data.get('learnings', [])]
                return learnings, reliabilities
        except Exception as e:
            print(f"  ⚠️ Strategy 1 failed: {e}")
        
        # Strategy 2: Try to find array of learnings
        try:
            array_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if array_match:
                array_str = array_match.group()
                # Clean up common JSON issues
                array_str = self._clean_json_string(array_str)
                learnings = json.loads(array_str)
                if isinstance(learnings, list) and all(isinstance(x, str) for x in learnings):
                    reliabilities = [0.7] * len(learnings)
                    return learnings, reliabilities
        except Exception as e:
            print(f"  ⚠️ Strategy 2 failed: {e}")
        
        return [], []
    
    def _extract_simple_learnings(self, response_text: str) -> Tuple[List[str], List[float]]:
        """Extract learnings from simple text format as fallback"""
        learnings = []
        
        # Look for numbered or bulleted lists
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            # Remove common list markers
            line = re.sub(r'^[\d\-•*]+\.?\s*', '', line)
            # Remove quotes
            line = re.sub(r'^["\']|["\']$', '', line)
            
            if line and len(line) > 20 and len(line) < 500:
                # Check if it looks like a learning (contains facts, numbers, entities)
                if any(keyword in line.lower() for keyword in ['million', 'billion', 'percent', '2024', '2023', 'company', 'market', 'sales', 'revenue', 'growth']):
                    learnings.append(line)
        
        # Limit to 15 learnings
        learnings = learnings[:15]
        reliabilities = [0.6] * len(learnings)  # Lower confidence for extracted learnings
        
        return learnings, reliabilities
    
    def _clean_json_string(self, json_str: str) -> str:
        """Clean up common JSON formatting issues"""
        # Remove control characters
        json_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_str)
        
        # Fix common quote issues
        json_str = re.sub(r'(?<!\\)"(?=.*":)', r'\\"', json_str)
        
        # Fix missing quotes around property names
        json_str = re.sub(r'(\s*)(\w+)(\s*):', r'\1"\2"\3:', json_str)
        
        # Fix trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # Fix newlines in content
        json_str = re.sub(r'\n', '\\n', json_str)
        json_str = re.sub(r'\r', '\\r', json_str)
        json_str = re.sub(r'\t', '\\t', json_str)
        
        return json_str
    
    async def generate_comprehensive_report(self, query: str, learnings: List[str], source_metadata: List[SourceMetadata], 
                                          learning_reliabilities: List[float]) -> Dict[str, Any]:
        """Generate comprehensive report using Gemini"""
        if not self.gemini_model:
            return {"error": "No AI model available"}
        
        try:
            # Prepare source reliability analysis
            high_reliability = [s for s in source_metadata if s.reliability_score >= 0.8]
            medium_reliability = [s for s in source_metadata if 0.6 <= s.reliability_score < 0.8]
            low_reliability = [s for s in source_metadata if s.reliability_score < 0.6]
            
            reliability_analysis = f"""
HIGH RELIABILITY SOURCES (≥80%): {len(high_reliability)} sources
{chr(10).join([f"- {s.domain}: {s.reliability_score:.0%} - {s.reliability_reasoning}" for s in high_reliability])}

MEDIUM RELIABILITY SOURCES (60-79%): {len(medium_reliability)} sources
{chr(10).join([f"- {s.domain}: {s.reliability_score:.0%} - {s.reliability_reasoning}" for s in medium_reliability])}

LOW RELIABILITY SOURCES (<60%): {len(low_reliability)} sources
{chr(10).join([f"- {s.domain}: {s.reliability_score:.0%} - {s.reliability_reasoning}" for s in low_reliability])}
"""
            
            # Prepare learnings with reliability scores
            learnings_with_reliability = []
            for i, learning in enumerate(learnings):
                reliability = learning_reliabilities[i] if i < len(learning_reliabilities) else 0.7
                learnings_with_reliability.append(f"[Reliability: {reliability:.2f}] {learning}")
            
            learnings_text = "\n".join(learnings_with_reliability)
            
            prompt = f"""You are an expert research analyst. Create a comprehensive research report for the query: "{query}"

RESEARCH DATA:
Total Sources: {len(source_metadata)}
Total Learnings: {len(learnings)}

LEARNINGS WITH RELIABILITY SCORES:
{learnings_text}

SOURCE RELIABILITY ANALYSIS:
{reliability_analysis}

REQUIREMENTS:
Follow this EXACT report structure:

1. EXECUTIVE SUMMARY (150-200 words):
   - Key findings in 3-5 bullet points
   - Primary recommendations
   - Critical success factors

2. ANALYSIS SECTIONS (3-5 sections):
   - Natural section titles based on research content
   - Data-driven insights with supporting evidence
   - Strategic framework application (PESTLE, Porter's Five Forces, etc.)

3. STRATEGIC RECOMMENDATIONS:
   - Actionable roadmap with clear owners
   - Implementation timelines
   - Success metrics and KPIs

4. FUTURE OUTLOOK:
   - Market trends and implications
   - Risk assessment
   - Opportunity identification

Generate the complete research report in JSON format:
{{
  "executive_summary": "150-200 word executive summary with key findings, primary recommendations, and critical success factors",
  "sections": [
    {{
      "title": "Natural section title based on research content",
      "content": "Data-driven insights with supporting evidence and strategic framework application (PESTLE, Porter's Five Forces, etc.)",
      "chart_type": "bar|line|pie|scatter|area|radar|waterfall|funnel|gauge|none",
      "chart_data": {{
        "labels": ["A", "B", "C"],
        "values": [10, 20, 30]
      }}
    }}
  ],
  "strategic_recommendations": {{
    "title": "Strategic Recommendations",
    "content": "Actionable roadmap with clear owners, implementation timelines, and success metrics/KPIs"
  }},
  "future_outlook": {{
    "title": "Future Outlook",
    "content": "Market trends and implications, risk assessment, and opportunity identification"
  }},
  "methodology": "Methodology section explaining data sources and quality",
  "sources": [
    {{
      "url": "source_url",
      "domain": "domain.com",
      "reliability_score": 0.85,
      "reliability_reasoning": "reasoning"
    }}
  ]
}}"""

            # Ensure gemini_model is available
            if not self.gemini_model:
                return {"error": "No AI model available"}
            response = await self.gemini_model.generate_content_async(prompt)
            
            # Extract JSON from response with better error handling
            report_data = self._extract_report_from_response(response.text)
            
            if report_data and "error" not in report_data:
                return report_data
            
            return {"error": "Failed to parse report data"}
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return {"error": str(e)}
    
    def _extract_report_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract report data from AI response with robust JSON parsing"""
        if not response_text:
            return None
        
        # Strategy 1: Try to find JSON object
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                # Clean up common JSON issues
                json_str = self._clean_json_string(json_str)
                report_data = json.loads(json_str)
                return report_data
        except Exception as e:
            print(f"  ⚠️ Report extraction Strategy 1 failed: {e}")
        
        # Strategy 2: Try to find JSON with code block markers
        try:
            code_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if code_match:
                json_str = code_match.group(1)
                # Clean up common JSON issues
                json_str = self._clean_json_string(json_str)
                report_data = json.loads(json_str)
                return report_data
        except Exception as e:
            print(f"  ⚠️ Report extraction Strategy 2 failed: {e}")
        
        return None
    
    async def deep_research(self, query: str, breadth: Optional[int] = None, depth: Optional[int] = None, 
                           on_progress: Optional[Callable] = None) -> Dict[str, Any]:
        """Perform deep research using Firecrawl and Gemini with adaptive breadth and true depth"""
        print(f"🚀 Starting deep research for: {query}")
        
        # Use environment variables if not provided
        if breadth is None:
            breadth = int(os.getenv('FIRECRAWL_RESEARCH_BREADTH', 4))
        if depth is None:
            depth = int(os.getenv('FIRECRAWL_RESEARCH_DEPTH', 2))
        
        # Reset credits
        self.reset_credits()
        
        # Generate initial search queries
        initial_queries = await self.generate_search_queries(query)
        
        # Use adaptive breadth - start with breadth setting, can adjust based on findings
        search_queries = initial_queries[:breadth]
        
        all_learnings = []
        all_learning_reliabilities = []
        all_source_metadata = []
        all_visited_urls = []
        all_query_results = []
        
        progress = ResearchProgress(
            current_depth=0,
            total_depth=depth,
            current_breadth=0,
            total_breadth=len(search_queries),
            total_queries=len(search_queries)
        )
        
        # Phase 1: Initial breadth search
        print(f"📊 Phase 1: Initial breadth search ({len(search_queries)} queries)")
        for i, search_query in enumerate(search_queries):
            progress.current_breadth = i + 1
            progress.current_query = search_query['query']
            
            if on_progress:
                on_progress(progress)
            
            print(f"🔍 Processing query {i+1}/{len(search_queries)}: {search_query['query']}")
            
            # Perform search
            result = await self.search_with_retry(search_query['query'])
            
            if result:
                # Process results
                learnings, reliabilities, metadata = await self.process_search_results(
                    search_query['query'], 
                    result, 
                    search_query.get('reliability_threshold', 0.3)
                )
                
                # Store query results for depth analysis
                query_result = {
                    'query': search_query['query'],
                    'learnings': learnings,
                    'reliabilities': reliabilities,
                    'metadata': metadata,
                    'quality_score': self._calculate_query_quality(learnings, metadata),
                    'urls': [m.url for m in metadata]
                }
                all_query_results.append(query_result)
                
                # Add to collections
                all_learnings.extend(learnings)
                all_learning_reliabilities.extend(reliabilities)
                all_source_metadata.extend(metadata)
                urls = query_result['urls'] if isinstance(query_result['urls'], list) else [query_result['urls']]
                all_visited_urls.extend(urls)
                
                progress.completed_queries += 1
                progress.learnings_count = len(all_learnings)
                
                print(f"✅ Found {len(learnings)} learnings from {len(metadata)} sources (Quality: {query_result['quality_score']:.2f})")
            else:
                print(f"⚠️ Search failed for query {i+1}, continuing...")
            
            # Small delay between requests
            await asyncio.sleep(1)
        
        # Phase 2: Adaptive depth search (if depth > 1)
        if depth > 1 and all_learnings:
            print(f"🔍 Phase 2: Adaptive depth search (depth {depth})")
            depth_queries = await self._generate_depth_queries(all_learnings, query, depth - 1)
            
            # Prioritize depth queries based on potential value
            prioritized_depth_queries = self._prioritize_queries(depth_queries, all_learnings)
            
            # Limit depth queries based on remaining credits and quality
            max_depth_queries = min(
                len(prioritized_depth_queries),
                self.max_credits_per_query - self.current_credits,
                6  # Maximum 6 depth queries
            )
            
            depth_queries_to_execute = prioritized_depth_queries[:max_depth_queries]
            
            print(f"🎯 Executing {len(depth_queries_to_execute)} prioritized depth queries")
            
            for i, depth_query in enumerate(depth_queries_to_execute):
                progress.current_depth = 1
                progress.current_query = depth_query['query']
                
                if on_progress:
                    on_progress(progress)
                
                print(f"🔍 Depth query {i+1}/{len(depth_queries_to_execute)}: {depth_query['query']}")
                
                # Perform depth search
                result = await self.search_with_retry(depth_query['query'])
                
                if result:
                    # Process results with higher reliability threshold for depth searches
                    reliability_threshold = depth_query.get('reliability_threshold', 0.5)
                    min_threshold = 0.5
                    final_threshold = reliability_threshold if reliability_threshold > min_threshold else min_threshold
                    learnings, reliabilities, metadata = await self.process_search_results(
                        depth_query['query'], 
                        result, 
                        final_threshold
                    )
                    
                    # Add to collections
                    all_learnings.extend(learnings)
                    all_learning_reliabilities.extend(reliabilities)
                    all_source_metadata.extend(metadata)
                    urls = query_result['urls'] if isinstance(query_result['urls'], list) else [query_result['urls']]
                    all_visited_urls.extend(urls)
                    
                    progress.learnings_count = len(all_learnings)
                    
                    print(f"✅ Depth: Found {len(learnings)} learnings from {len(metadata)} sources")
                else:
                    print(f"⚠️ Depth search failed for query {i+1}")
                
                # Check credit limit
                if self.current_credits >= self.max_credits_per_query * 0.9:
                    print(f"⚠️ Credit limit reached during depth search")
                    break
                
                await asyncio.sleep(1)
        
        print(f"✅ Research completed: {len(all_learnings)} learnings from {len(all_visited_urls)} sources")
        print(f"💳 Credits used: {self.current_credits}/{self.max_credits_per_query}")
        
        # Generate comprehensive report
        report = await self.generate_comprehensive_report(
            query, all_learnings, all_source_metadata, all_learning_reliabilities
        )
        
        return {
            "query": query,
            "learnings": all_learnings,
            "learning_reliabilities": all_learning_reliabilities,
            "source_metadata": [vars(m) for m in all_source_metadata],
            "visited_urls": all_visited_urls,
            "query_results": all_query_results,
            "report": report,
            "credits_used": self.current_credits,
            "research_metrics": {
                "breadth_queries": len(search_queries),
                "depth_queries": depth - 1 if depth > 1 else 0,
                "total_sources": len(all_visited_urls),
                "high_quality_sources": len([s for s in all_source_metadata if s.reliability_score >= 0.7]),
                "average_reliability": sum(s.reliability_score for s in all_source_metadata) / len(all_source_metadata) if all_source_metadata else 0
            }
        }
    
    def _calculate_query_quality(self, learnings: List[str], metadata: List[SourceMetadata]) -> float:
        """Calculate quality score for a query based on learnings and source quality"""
        if not learnings or not metadata:
            return 0.0
        
        # Factor 1: Number of learnings (more is better, but with diminishing returns)
        learning_score = min(len(learnings) / 10.0, 1.0)  # Cap at 10 learnings
        
        # Factor 2: Average source reliability
        avg_reliability = sum(m.reliability_score for m in metadata) / len(metadata)
        
        # Factor 3: Content richness (total content length)
        total_content = sum(m.content_length for m in metadata)
        content_score = min(total_content / 50000.0, 1.0)  # Cap at 50k characters
        
        # Factor 4: Source diversity (different domains)
        unique_domains = len(set(m.domain for m in metadata))
        diversity_score = min(unique_domains / 5.0, 1.0)  # Cap at 5 unique domains
        
        # Weighted combination
        quality_score = (
            learning_score * 0.3 +
            avg_reliability * 0.4 +
            content_score * 0.2 +
            diversity_score * 0.1
        )
        
        return quality_score
    
    async def _generate_depth_queries(self, learnings: List[str], original_query: str, depth_levels: int) -> List[Dict[str, Any]]:
        """Generate follow-up queries based on initial learnings for depth search"""
        if not self.gemini_model or not learnings:
            return []
        
        try:
            # Select most informative learnings for query generation
            top_learnings = learnings[:8]  # Use top 8 learnings
            
            prompt = f"""Based on these initial research findings about "{original_query}", generate specific follow-up search queries for deeper investigation.

INITIAL FINDINGS:
{chr(10).join([f"- {learning}" for learning in top_learnings])}

Generate {depth_levels * 2} specific follow-up queries that will:
1. Verify or expand on key data points found
2. Investigate specific claims or statistics mentioned
3. Find additional context for important findings
4. Cross-reference information from different sources
5. Explore specific aspects mentioned in the findings

Each query should be highly specific and target particular data points, companies, dates, or claims mentioned in the findings.

Respond with JSON format:
{{
  "queries": [
    {{
      "query": "specific follow-up search query",
      "research_goal": "What this depth query aims to verify or expand",
      "reliability_threshold": 0.6,
      "priority": 1
    }}
  ]
}}"""

            response = await self.gemini_model.generate_content_async(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get('queries', [])
            
            return []
            
        except Exception as e:
            print(f"❌ Error generating depth queries: {e}")
            return []
    
    def _prioritize_queries(self, queries: List[Dict[str, Any]], existing_learnings: List[str]) -> List[Dict[str, Any]]:
        """Prioritize queries based on potential value and existing knowledge"""
        if not queries:
            return []
        
        # Calculate priority scores for each query
        prioritized_queries = []
        for query in queries:
            priority_score = self._calculate_query_priority(query, existing_learnings)
            query['priority_score'] = priority_score
            prioritized_queries.append(query)
        
        # Sort by priority score (highest first)
        prioritized_queries.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return prioritized_queries
    
    def _calculate_query_priority(self, query: Dict[str, Any], existing_learnings: List[str]) -> float:
        """Calculate priority score for a query based on potential value"""
        priority_score = 0.0
        
        # Factor 1: Reliability threshold (higher is better)
        reliability_threshold = query.get('reliability_threshold', 0.5)
        priority_score += reliability_threshold * 0.3
        
        # Factor 2: Query specificity (longer, more specific queries are better)
        query_length = len(query.get('query', ''))
        specificity_score = min(query_length / 100.0, 1.0)
        priority_score += specificity_score * 0.2
        
        # Factor 3: Novelty (queries that don't overlap with existing learnings)
        query_words = set(query.get('query', '').lower().split())
        overlap_count = 0
        for learning in existing_learnings[:10]:  # Check against top 10 learnings
            learning_words = set(learning.lower().split())
            overlap = len(query_words.intersection(learning_words))
            overlap_count += overlap
        
        novelty_score = max(0.0, 1.0 - (overlap_count / 50.0))  # Less overlap = higher novelty
        priority_score += novelty_score * 0.3
        
        # Factor 4: Research goal clarity
        goal = query.get('research_goal', '')
        goal_clarity = min(len(goal) / 100.0, 1.0)
        priority_score += goal_clarity * 0.2
        
        return priority_score

    async def _make_search_request(self, query: str) -> Optional[Dict[str, Any]]:
        """Make the actual search request to Firecrawl API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.firecrawl_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": query,
                "limit": int(os.getenv('FIRECRAWL_SEARCH_LIMIT', 3)),
                "scrapeOptions": {
                    "formats": ["markdown"]
                }
            }
            
            response = requests.post(
                "https://api.firecrawl.dev/v1/search",
                headers=headers,
                json=payload,
                timeout=int(os.getenv('FIRECRAWL_REQUEST_TIMEOUT', 30))
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                return {"error": "rate limit"}
            elif response.status_code == 402:
                return {"error": "insufficient credits"}
            elif response.status_code == 401:
                return {"error": "unauthorized"}
            elif response.status_code == 403:
                return {"error": "forbidden"}
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}


# Example usage
async def main():
    """Example usage of FirecrawlResearch"""
    research = FirecrawlResearch()
    
    def progress_callback(progress: ResearchProgress):
        print(f"Progress: {progress.completed_queries}/{progress.total_queries} queries completed")
    
    result = await research.deep_research(
        query="Tesla electric vehicle market analysis",
        breadth=4,
        depth=2,
        on_progress=progress_callback
    )
    
    print("Research Results:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main()) 