#!/usr/bin/env python3
"""
Firecrawl Research Module - Real-time web scraping and AI-powered report generation
Uses FIRECRAWL_API_URL from .env for direct URL access (no API key required)
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
import traceback

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
    """Real-time web research using Firecrawl URL and Gemini"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize with Gemini API key only (no Firecrawl API key needed)"""
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        
        # Get Firecrawl URL from environment
        self.firecrawl_api_url = os.getenv('FIRECRAWL_API_URL')
        if not self.firecrawl_api_url:
            print("❌ ERROR: FIRECRAWL_API_URL not found in environment variables")
            print("   Please set FIRECRAWL_API_URL in your .env file")
            raise ValueError("FIRECRAWL_API_URL is required")
        
        print(f"🌐 Firecrawl URL configured: {self.firecrawl_api_url}")
        
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
        else:
            print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY is required")
        
        # Rate limiting for Firecrawl URL access
        self.rate_limits = {
            'search': {
                'limit': int(os.getenv('FIRECRAWL_RATE_LIMIT_SEARCH', 50)), 
                'window': int(os.getenv('FIRECRAWL_RATE_LIMIT_WINDOW', 60000)), 
                'requests': 0, 
                'reset_time': 0.0
            }
        }
        
        # Request tracking
        self.request_count = 0
        self.max_requests_per_query = int(os.getenv('FIRECRAWL_MAX_CREDITS_PER_QUERY', 20))
        
        print(f"🔥 Firecrawl Research initialized successfully")
        print(f"   - URL: {self.firecrawl_api_url}")
        print(f"   - Max requests per query: {self.max_requests_per_query}")
        print(f"   - Rate limit: {self.rate_limits['search']['limit']} requests per {self.rate_limits['search']['window']/1000}s")
    
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
    
    def check_request_limit(self) -> bool:
        """Check if we can make another request"""
        if self.request_count >= self.max_requests_per_query:
            print(f"🚫 Request limit reached! ({self.request_count}/{self.max_requests_per_query})")
            return False
        return True
    
    def track_request(self) -> None:
        """Track request usage"""
        self.request_count += 1
        if self.request_count > self.max_requests_per_query * 0.8:
            print(f"⚠️ Requests: {self.request_count}/{self.max_requests_per_query}")
    
    def reset_requests(self) -> None:
        """Reset request tracking for new query"""
        self.request_count = 0
    
    async def search_with_retry(self, query: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Search with retry logic and better request management"""
        print(f"🔍 Searching for: '{query}'")
        
        for attempt in range(max_retries):
            try:
                # Check request limit before making request
                if not self.check_request_limit():
                    print(f"  ⚠️ Request limit reached ({self.request_count}/{self.max_requests_per_query})")
                    return None
                
                # Check rate limits
                await self.check_rate_limit("search")
                
                # Make the search request
                response = await self._make_search_request(query)
                
                if response and response.get("success"):
                    self.track_request()
                    print(f"  ✅ Search successful (attempt {attempt + 1})")
                    return response
                elif response and response.get("error"):
                    error_msg = response.get("error", "").lower()
                    if "rate limit" in error_msg or "433" in error_msg or "443" in error_msg or "service error" in error_msg:
                        print(f"  ⏳ Rate limited or service error, waiting... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(min(2 ** attempt, 3))  # Capped exponential backoff (max 3 seconds)
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
                    await asyncio.sleep(0.5)  # Reduced from 1 second to 0.5 seconds
                else:
                    return None
        
        return None
    
    def _get_cached_reliability_score(self, domain: str, context: str) -> Tuple[float, str]:
        """Get cached reliability score to reduce Gemini API calls"""
        # Common domain reliability cache
        domain_cache = {
            # High reliability domains
            'reuters.com': (0.9, 'Respected international news organization'),
            'bloomberg.com': (0.85, 'Leading financial news and data provider'),
            'cnn.com': (0.8, 'Major news network with editorial oversight'),
            'bbc.com': (0.9, 'Public service broadcaster with high editorial standards'),
            'nytimes.com': (0.9, 'Prestigious newspaper with fact-checking'),
            'wsj.com': (0.9, 'Leading business and financial news'),
            'forbes.com': (0.75, 'Business magazine with editorial oversight'),
            'techcrunch.com': (0.7, 'Technology news with industry expertise'),
            'statista.com': (0.85, 'Statistical data and market research'),
            'iea.org': (0.9, 'International Energy Agency - authoritative source'),
            'worldbank.org': (0.9, 'International financial institution'),
            'imf.org': (0.9, 'International Monetary Fund'),
            'oecd.org': (0.9, 'Organisation for Economic Co-operation and Development'),
            
            # Medium reliability domains
            'medium.com': (0.6, 'Platform with mixed content quality'),
            'linkedin.com': (0.65, 'Professional network with business content'),
            'reddit.com': (0.4, 'User-generated content platform'),
            'wikipedia.org': (0.7, 'Crowdsourced encyclopedia with citations'),
            
            # Low reliability domains
            'blogspot.com': (0.3, 'Personal blog platform'),
            'wordpress.com': (0.4, 'Mixed content quality'),
            'tumblr.com': (0.2, 'Social media platform'),
        }
        
        # Check cache first
        if domain in domain_cache:
            return domain_cache[domain]
        
        # Check for domain patterns
        domain_lower = domain.lower()
        
        # Government/educational domains
        if any(pattern in domain_lower for pattern in ['.gov', '.edu', '.ac.', 'university', 'college']):
            return (0.85, 'Government or educational institution')
        
        # News domains
        if any(pattern in domain_lower for pattern in ['.news', 'news', 'times', 'post', 'tribune', 'herald']):
            return (0.75, 'News organization')
        
        # Business/tech domains
        if any(pattern in domain_lower for pattern in ['.com', 'business', 'tech', 'industry', 'market']):
            return (0.6, 'Business or industry website')
        
        # Default score for unknown domains
        return (0.5, 'Unknown domain - default reliability score')

    async def evaluate_source_reliability(self, domain: str, context: str) -> Tuple[float, str]:
        """Evaluate source reliability using Gemini - kept for fallback"""
        # Use cached version for performance
        return self._get_cached_reliability_score(domain, context)
    
    def generate_search_queries(self, query: str, learnings: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Generate search queries using predefined patterns - OPTIMIZED to reduce Gemini calls"""
        print("🔍 DEBUG: generate_search_queries called (optimized)")
        
        # Predefined query patterns for common research topics
        base_queries = [
            {"query": query, "research_goal": "General overview and current status", "reliability_threshold": 0.6},
            {"query": f"{query} market analysis 2024", "research_goal": "Market analysis and trends", "reliability_threshold": 0.7},
            {"query": f"{query} statistics data", "research_goal": "Statistical data and metrics", "reliability_threshold": 0.8},
            {"query": f"{query} competitive landscape", "research_goal": "Competitive analysis", "reliability_threshold": 0.6},
            {"query": f"{query} future outlook forecast", "research_goal": "Future predictions and forecasts", "reliability_threshold": 0.6},
        ]
        
        # Add topic-specific queries based on keywords
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['tesla', 'electric', 'vehicle', 'ev']):
            base_queries.extend([
                {"query": "Tesla electric vehicle market share 2024", "research_goal": "Market share analysis", "reliability_threshold": 0.7},
                {"query": "Tesla EV sales statistics 2024", "research_goal": "Sales performance data", "reliability_threshold": 0.8},
            ])
        elif any(word in query_lower for word in ['apple', 'iphone', 'technology']):
            base_queries.extend([
                {"query": "Apple iPhone market performance 2024", "research_goal": "Product performance analysis", "reliability_threshold": 0.7},
                {"query": "Apple technology innovation trends", "research_goal": "Innovation analysis", "reliability_threshold": 0.6},
            ])
        elif any(word in query_lower for word in ['nvidia', 'ai', 'artificial intelligence']):
            base_queries.extend([
                {"query": "NVIDIA AI chip market dominance", "research_goal": "Market position analysis", "reliability_threshold": 0.7},
                {"query": "NVIDIA artificial intelligence growth 2024", "research_goal": "Growth analysis", "reliability_threshold": 0.7},
            ])
        
        # Limit to 6 queries maximum
        return base_queries[:6]

    async def generate_search_queries_ai(self, query: str, learnings: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Generate search queries using Gemini - kept for fallback"""
        print("🔍 DEBUG: generate_search_queries_ai called")
        
        if not self.gemini_model:
            print("🔍 DEBUG: No Gemini model available, returning basic query")
            return [{"query": query, "research_goal": "Basic research"}]
        
        try:
            print("🔍 DEBUG: About to create prompt for search queries")
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

            print("🔍 DEBUG: About to call Gemini model for search queries")
            response = await self.gemini_model.generate_content_async(prompt)
            print("🔍 DEBUG: Gemini model response received for search queries")
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                queries = data.get('queries', [{"query": query, "research_goal": "Basic research"}])
                print(f"🔍 DEBUG: Extracted {len(queries)} search queries from JSON")
                return queries
            
            print("🔍 DEBUG: No JSON found in response, returning basic query")
            return [{"query": query, "research_goal": "Basic research"}]
            
        except Exception as e:
            print(f"❌ DEBUG: Error generating queries: {e}")
            print("🔍 DEBUG: generate_search_queries traceback:")
            traceback.print_exc()
            return [{"query": query, "research_goal": "Basic research"}]
    
    async def process_search_results(self, query: str, result: Dict[str, Any], reliability_threshold: Optional[float] = None) -> Tuple[List[str], List[float], List[SourceMetadata]]:
        """Process search results and extract learnings"""
        if reliability_threshold is None:
            reliability_threshold = float(os.getenv('FIRECRAWL_RELIABILITY_THRESHOLD', 0.3))
        
        if not result or 'data' not in result:
            print(f"[DEBUG] No 'data' in Firecrawl result: {result}")
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
            
            # Evaluate reliability - OPTIMIZED: Use cached/default scores for common domains
            reliability_score, reasoning = self._get_cached_reliability_score(domain, query)
            
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
        print(f"[DEBUG] Extracted learnings: {learnings}")
        
        return learnings, learning_reliabilities, source_metadata
    
    async def extract_learnings(self, contents: List[str], query: str) -> Tuple[List[str], List[float]]:
        """Extract learnings from content using Gemini"""
        print("🔍 DEBUG: extract_learnings called")
        
        if not self.gemini_model or not contents:
            print("🔍 DEBUG: No Gemini model or contents available for learning extraction")
            return [], []
        
        try:
            print("🔍 DEBUG: About to combine content for learning extraction")
            # Combine content (limit to avoid token limits)
            combined_content = "\n\n---\n\n".join(contents[:5])  # Limit to 5 sources
            if len(combined_content) > 15000:
                combined_content = combined_content[:15000] + "..."
            
            prompt = f"""Given the following contents from a search for the query "{query}", generate a list of learnings from the contents. Return a maximum of 15 learnings, but feel free to return less if the contents are clear. Make sure each learning is unique and not similar to each other. The learnings should be concise and to the point, as detailed and information dense as possible. Make sure to include any entities like people, places, companies, products, things, etc in the learnings, as well as any exact metrics, numbers, or dates.

Content:
{combined_content}

IMPORTANT: Respond with ONLY valid JSON format, no additional text or explanations. Use this exact structure:

{{
  "learnings": [
    {{
      "content": "specific learning with facts, numbers, and entities",
      "confidence": 0.8,
      "sources": ["domain1.com", "domain2.com"]
    }}
  ]
}}

Ensure all property names are in double quotes and all string values are properly escaped."""

            print("🔍 DEBUG: About to call Gemini model for learning extraction")
            response = await self.gemini_model.generate_content_async(prompt)
            print("🔍 DEBUG: Gemini model response received for learning extraction")
            
            # Multiple strategies to extract JSON from response
            print("🔍 DEBUG: About to extract learnings from response")
            learnings, reliabilities = self._extract_learnings_from_response(response.text)
            
            if learnings:
                print(f"🔍 DEBUG: Extracted {len(learnings)} learnings from JSON response")
                return learnings, reliabilities
            
            # Fallback: try to extract simple list format
            print("🔍 DEBUG: Trying fallback simple learning extraction")
            fallback_learnings, fallback_reliabilities = self._extract_simple_learnings(response.text)
            print(f"🔍 DEBUG: Fallback extracted {len(fallback_learnings)} learnings")
            return fallback_learnings, fallback_reliabilities
            
        except Exception as e:
            print(f"❌ DEBUG: Error extracting learnings: {e}")
            print("🔍 DEBUG: extract_learnings traceback:")
            traceback.print_exc()
            return [], []
    
    def _extract_learnings_from_response(self, response_text: str) -> Tuple[List[str], List[float]]:
        """Extract learnings from AI response using multiple strategies"""
        if not response_text:
            return [], []
        
        print(f"🔍 DEBUG: Raw response text length: {len(response_text)}")
        print(f"🔍 DEBUG: Response preview: {response_text[:200]}...")
        
        # Strategy 1: Try to find JSON object with code block markers
        try:
            code_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if code_match:
                json_str = code_match.group(1)
                print(f"🔍 DEBUG: Found JSON in code block, length: {len(json_str)}")
                data = json.loads(json_str)
                learnings = [item['content'] for item in data.get('learnings', [])]
                reliabilities = [item.get('confidence', 0.7) for item in data.get('learnings', [])]
                print(f"🔍 DEBUG: Strategy 1 (code block) extracted {len(learnings)} learnings")
                return learnings, reliabilities
        except Exception as e:
            print(f"  ⚠️ Strategy 1 (code block) failed: {e}")
        
        # Strategy 2: Try to find JSON object without code block markers
        try:
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                print(f"🔍 DEBUG: Found JSON object, length: {len(json_str)}")
                # Try to clean and parse
                cleaned_json = self._clean_json_string_robust(json_str)
                data = json.loads(cleaned_json)
                learnings = [item['content'] for item in data.get('learnings', [])]
                reliabilities = [item.get('confidence', 0.7) for item in data.get('learnings', [])]
                print(f"🔍 DEBUG: Strategy 2 (JSON object) extracted {len(learnings)} learnings")
                return learnings, reliabilities
        except Exception as e:
            print(f"  ⚠️ Strategy 2 (JSON object) failed: {e}")
        
        # Strategy 3: Try to find array of learnings
        try:
            array_match = re.search(r'\[[^\[\]]*(?:\{[^{}]*\}[^\[\]]*)*\]', response_text, re.DOTALL)
            if array_match:
                array_str = array_match.group()
                print(f"🔍 DEBUG: Found array, length: {len(array_str)}")
                # Try to clean and parse
                cleaned_array = self._clean_json_string_robust(array_str)
                learnings = json.loads(cleaned_array)
                if isinstance(learnings, list) and all(isinstance(x, str) for x in learnings):
                    reliabilities = [0.7] * len(learnings)
                    print(f"🔍 DEBUG: Strategy 3 (array) extracted {len(learnings)} learnings")
                    return learnings, reliabilities
        except Exception as e:
            print(f"  ⚠️ Strategy 3 (array) failed: {e}")
        
        # Strategy 4: Try to extract simple list format
        try:
            lines = response_text.split('\n')
            learnings = []
            for line in lines:
                line = line.strip()
                # Look for numbered or bulleted items
                if re.match(r'^[\d\-•*]+\.?\s*', line):
                    # Remove the marker
                    content = re.sub(r'^[\d\-•*]+\.?\s*', '', line)
                    # Remove quotes
                    content = re.sub(r'^["\']|["\']$', '', content)
                    if content and len(content) > 10:
                        learnings.append(content)
            
            if learnings:
                reliabilities = [0.6] * len(learnings)
                print(f"🔍 DEBUG: Strategy 4 (simple list) extracted {len(learnings)} learnings")
                return learnings[:15], reliabilities[:15]  # Limit to 15
        except Exception as e:
            print(f"  ⚠️ Strategy 4 (simple list) failed: {e}")
        
        print("🔍 DEBUG: All JSON extraction strategies failed")
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
    
    def _clean_json_string_robust(self, json_str: str) -> str:
        """More robust JSON string cleaning that preserves structure"""
        if not json_str:
            return "{}"
        
        # Remove control characters but preserve newlines in strings
        json_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_str)
        
        # Fix missing quotes around property names (more carefully)
        # Only fix if it's not already quoted
        json_str = re.sub(r'(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*):', r'\1"\2"\3:', json_str)
        
        # Fix trailing commas before closing braces/brackets
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Handle escaped quotes properly
        json_str = re.sub(r'\\"', r'__ESCAPED_QUOTE__', json_str)
        json_str = re.sub(r'(?<!\\)"(?=.*":)', r'\\"', json_str)
        json_str = re.sub(r'__ESCAPED_QUOTE__', r'\\"', json_str)
        
        # Fix common unicode issues
        json_str = json_str.replace('\\u2019', "'")
        json_str = json_str.replace('\\u201c', '"')
        json_str = json_str.replace('\\u201d', '"')
        json_str = json_str.replace('\\u2013', '-')
        json_str = json_str.replace('\\u2014', '-')
        
        # Ensure the string starts and ends properly
        if not json_str.strip().startswith('{') and not json_str.strip().startswith('['):
            # Try to find the actual start
            start_match = re.search(r'[{\[]', json_str)
            if start_match:
                json_str = json_str[start_match.start():]
        
        if not json_str.strip().endswith('}') and not json_str.strip().endswith(']'):
            # Try to find the actual end
            end_match = re.search(r'[}\]]', json_str[::-1])
            if end_match:
                json_str = json_str[:-end_match.start()-1]
        
        return json_str
    
    async def generate_comprehensive_report(self, query: str, learnings: List[str], source_metadata: List[SourceMetadata], 
                                          learning_reliabilities: List[float]) -> Dict[str, Any]:
        """
        DEPRECATED: This method is no longer used.
        Report generation is now handled by ReportPlanner in firecrawl_integration.py
        This method is kept for backward compatibility but should not be used.
        """
        print("⚠️ WARNING: generate_comprehensive_report is deprecated. Use ReportPlanner instead.")
        return {"error": "This method is deprecated. Use ReportPlanner for report generation."}
    
    def _extract_report_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        DEPRECATED: This method is no longer used.
        Report extraction is now handled by ReportPlanner in firecrawl_integration.py
        This method is kept for backward compatibility but should not be used.
        """
        print("⚠️ WARNING: _extract_report_from_response is deprecated. Use ReportPlanner instead.")
        return None
    
    async def deep_research(self, query: str, breadth: Optional[int] = None, depth: Optional[int] = None, 
                           on_progress: Optional[Callable] = None) -> Dict[str, Any]:
        """Perform deep research using Firecrawl URL and Gemini with adaptive breadth and true depth"""
        print(f"🚀 Starting deep research for: {query}")
        
        # Add debug traceback printing
        print("🔍 DEBUG: Starting deep_research with traceback monitoring...")
        
        try:
            # Use environment variables if not provided
            if breadth is None:
                breadth = int(os.getenv('FIRECRAWL_RESEARCH_BREADTH', 4))
            if depth is None:
                depth = int(os.getenv('FIRECRAWL_RESEARCH_DEPTH', 2))
            
            # Reset requests
            self.reset_requests()
            
            # Generate initial search queries
            print("🔍 DEBUG: About to call generate_search_queries...")
            initial_queries = self.generate_search_queries(query)
            print(f"🔍 DEBUG: generate_search_queries completed, got {len(initial_queries)} queries")
            
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
                    try:
                        print("🔍 DEBUG: About to call on_progress callback...")
                        on_progress(progress)
                        print("🔍 DEBUG: on_progress callback completed successfully")
                    except Exception as callback_error:
                        print(f"❌ DEBUG: on_progress callback failed with error: {callback_error}")
                        print("🔍 DEBUG: on_progress callback traceback:")
                        traceback.print_exc()
                
                print(f"🔍 Processing query {i+1}/{len(search_queries)}: {search_query['query']}")
                
                # Perform search
                print("🔍 DEBUG: About to call search_with_retry...")
                result = await self.search_with_retry(search_query['query'])
                print("🔍 DEBUG: search_with_retry completed")
                
                if result:
                    # Process results
                    print("🔍 DEBUG: About to call process_search_results...")
                    learnings, reliabilities, metadata = await self.process_search_results(
                        search_query['query'], 
                        result, 
                        search_query.get('reliability_threshold', 0.3)
                    )
                    print("🔍 DEBUG: process_search_results completed")
                    
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
                print("🔍 DEBUG: About to call _generate_depth_queries...")
                depth_queries = self._generate_depth_queries(all_learnings, query, depth - 1)
                print("🔍 DEBUG: _generate_depth_queries completed")
                
                # Prioritize depth queries based on potential value
                print("🔍 DEBUG: About to call _prioritize_queries...")
                prioritized_depth_queries = self._prioritize_queries(depth_queries, all_learnings)
                print("🔍 DEBUG: _prioritize_queries completed")
                
                # Limit depth queries based on remaining requests and quality
                max_depth_queries = min(
                    len(prioritized_depth_queries),
                    self.max_requests_per_query - self.request_count,
                    6  # Maximum 6 depth queries
                )
                
                depth_queries_to_execute = prioritized_depth_queries[:max_depth_queries]
                
                print(f"🎯 Executing {len(depth_queries_to_execute)} prioritized depth queries")
                
                for i, depth_query in enumerate(depth_queries_to_execute):
                    progress.current_depth = 1
                    progress.current_query = depth_query['query']
                    
                    if on_progress:
                        try:
                            print("🔍 DEBUG: About to call on_progress callback for depth query...")
                            on_progress(progress)
                            print("🔍 DEBUG: on_progress callback for depth query completed successfully")
                        except Exception as callback_error:
                            print(f"❌ DEBUG: on_progress callback for depth query failed with error: {callback_error}")
                            print("🔍 DEBUG: on_progress callback for depth query traceback:")
                            traceback.print_exc()
                    
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
                    
                    # Check request limit
                    if self.request_count >= self.max_requests_per_query * 0.9:
                        print(f"⚠️ Request limit reached during depth search")
                        break
                    
                    await asyncio.sleep(1)
            
            print(f"✅ Research completed: {len(all_learnings)} learnings from {len(all_visited_urls)} sources")
            print(f"💳 Requests used: {self.request_count}/{self.max_requests_per_query}")
            
            # Report generation is now handled by ReportPlanner in firecrawl_integration.py
            # This method only returns research data
            
            return {
                "query": query,
                "learnings": all_learnings,
                "learning_reliabilities": all_learning_reliabilities,
                "source_metadata": [vars(m) for m in all_source_metadata],
                "visited_urls": all_visited_urls,
                "query_results": all_query_results,
                "requests_used": self.request_count,
                "research_metrics": {
                    "breadth_queries": len(search_queries),
                    "depth_queries": depth - 1 if depth > 1 else 0,
                    "total_sources": len(all_visited_urls),
                    "high_quality_sources": len([s for s in all_source_metadata if s.reliability_score >= 0.7]),
                    "average_reliability": sum(s.reliability_score for s in all_source_metadata) / len(all_source_metadata) if all_source_metadata else 0
                }
            }
            
        except Exception as e:
            print(f"❌ DEBUG: deep_research failed with error: {e}")
            print("🔍 DEBUG: deep_research traceback:")
            traceback.print_exc()
            raise
    
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
    
    def _generate_depth_queries(self, learnings: List[str], original_query: str, depth_levels: int) -> List[Dict[str, Any]]:
        """Generate follow-up queries based on initial learnings - OPTIMIZED to reduce Gemini calls"""
        if not learnings:
            return []
        
        try:
            # Extract key entities and numbers from learnings
            key_entities = []
            key_numbers = []
            
            for learning in learnings[:5]:  # Use top 5 learnings
                # Extract numbers (percentages, years, etc.)
                numbers = re.findall(r'\d+(?:\.\d+)?%?', learning)
                key_numbers.extend(numbers)
                
                # Extract potential entities (companies, products, etc.)
                # Simple pattern matching for common entities
                if any(word in learning.lower() for word in ['tesla', 'apple', 'nvidia', 'google', 'amazon']):
                    key_entities.extend(['Tesla', 'Apple', 'NVIDIA', 'Google', 'Amazon'])
            
            # Generate depth queries based on extracted information
            depth_queries = []
            
            # Add queries for key numbers found
            for number in set(key_numbers[:3]):  # Limit to 3 unique numbers
                depth_queries.append({
                    "query": f"{original_query} {number} verification",
                    "research_goal": f"Verify the {number} statistic or data point",
                    "reliability_threshold": 0.7,
                    "priority": 1
                })
            
            # Add queries for key entities
            for entity in set(key_entities[:2]):  # Limit to 2 entities
                depth_queries.append({
                    "query": f"{entity} {original_query} detailed analysis",
                    "research_goal": f"Detailed analysis of {entity} in this context",
                    "reliability_threshold": 0.6,
                    "priority": 2
                })
            
            # Add general verification queries
            depth_queries.extend([
                {
                    "query": f"{original_query} latest data 2024",
                    "research_goal": "Find the most recent data and statistics",
                    "reliability_threshold": 0.8,
                    "priority": 1
                },
                {
                    "query": f"{original_query} market share comparison",
                    "research_goal": "Compare market shares and competitive positions",
                    "reliability_threshold": 0.7,
                    "priority": 2
                }
            ])
            
            # Limit to depth_levels * 2 queries
            return depth_queries[:depth_levels * 2]
            
        except Exception as e:
            print(f"❌ Error generating depth queries: {e}")
            return []

    async def _generate_depth_queries_ai(self, learnings: List[str], original_query: str, depth_levels: int) -> List[Dict[str, Any]]:
        """Generate follow-up queries using Gemini - kept for fallback"""
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
        """Make the actual search request to Firecrawl URL (direct access, no API key)"""
        try:
            print(f"🌐 Making request to Firecrawl URL: {self.firecrawl_api_url}")
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"
            }
            
            payload = {
                "query": query,
                "limit": int(os.getenv('FIRECRAWL_SEARCH_LIMIT', 3)),
                "scrapeOptions": {
                    "formats": ["markdown"]
                }
            }
            
            print(f"📤 Request payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                self.firecrawl_api_url,
                headers=headers,
                json=payload,
                timeout=int(os.getenv('FIRECRAWL_REQUEST_TIMEOUT', 30))
            )
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"✅ Request successful - Found {len(response_data.get('data', []))} results")
                return response_data
            elif response.status_code == 429:
                print("⏳ Rate limited by server")
                return {"error": "rate limit"}
            elif response.status_code == 433:
                print("🚫 433 error - likely rate limiting or service-specific error")
                print(f"📋 Response: {response.text[:200]}...")
                return {"error": "rate limit or service error"}
            elif response.status_code == 401:
                print("🔐 Unauthorized - check URL configuration")
                return {"error": "unauthorized"}
            elif response.status_code == 403:
                print("🚫 Forbidden - access denied")
                return {"error": "forbidden"}
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            print(f"❌ Exception in _make_search_request: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
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