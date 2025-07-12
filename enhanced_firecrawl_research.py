#!/usr/bin/env python3
"""
Enhanced Firecrawl Research Module - Real-time web scraping and AI-powered report generation
Adapted from TypeScript implementation to work with Python and Gemini
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
from concurrent.futures import ThreadPoolExecutor
import aiohttp

# Load environment variables from .env file
load_dotenv()


@dataclass
class SourceMetadata:
    """Enhanced metadata about a source"""
    url: str
    title: Optional[str] = None
    publish_date: Optional[str] = None
    domain: Optional[str] = None
    relevance_score: Optional[float] = None
    reliability_score: float = 0.5
    reliability_reasoning: str = ""
    content_length: int = 0
    last_checked: Optional[str] = None
    screenshots: Optional[List[str]] = None
    site_structure: Optional[Dict[str, Any]] = None
    extracted_data: Optional[Dict[str, Any]] = None
    content_formats: Optional[List[str]] = None
    change_history: Optional[List[Dict[str, Any]]] = None


@dataclass
class ResearchLearning:
    """A learning from research with reliability score"""
    content: str
    reliability: float
    sources: List[str]
    data_type: str = "regular"


@dataclass
class ResearchDirection:
    """Research direction with priority"""
    question: str
    priority: int
    parent_goal: Optional[str] = None


@dataclass
class ResearchProgress:
    """Progress tracking for research"""
    current_depth: int
    total_depth: int
    current_breadth: int
    total_breadth: int
    current_query: Optional[str] = None
    parent_query: Optional[str] = None
    total_queries: int = 0
    completed_queries: int = 0
    learnings_count: Optional[int] = None
    learnings: Optional[List[str]] = None
    follow_up_questions: Optional[List[str]] = None


class EnhancedFirecrawlResearch:
    """Enhanced real-time web research using Firecrawl URL and Gemini"""
    
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
        
        # Hobby plan limits (adapted from TypeScript)
        self.hobby_plan_limits = {
            'max_credits_per_query': int(os.getenv('MAX_CREDITS_PER_QUERY', '300')),
            'max_search_requests': int(os.getenv('MAX_SEARCH_REQUESTS', '20')),
            'max_scrape_requests': int(os.getenv('MAX_SCRAPE_REQUESTS', '10')),
            'max_depth': int(os.getenv('MAX_RESEARCH_DEPTH', '5')),
            'max_breadth': int(os.getenv('MAX_RESEARCH_BREADTH', '6')),
            'disable_enhanced_processing': os.getenv('DISABLE_ENHANCED_PROCESSING') != 'true',
            'disable_website_mapping': os.getenv('DISABLE_WEBSITE_MAPPING') != 'true',
            'disable_batch_scraping': os.getenv('DISABLE_BATCH_SCRAPING') != 'true',
            'disable_structured_extraction': os.getenv('DISABLE_STRUCTURED_EXTRACTION') != 'true',
        }
        
        # Credit tracking state
        self.credit_tracker = {
            'current_query_credits': 0,
            'total_credits': 0,
            'search_requests': 0,
            'scrape_requests': 0,
            'query_start_time': 0,
        }
        
        # Credit costs (based on Firecrawl pricing)
        self.credit_costs = {
            'search': 1,
            'scrape': 1,
            'map': 1,
            'crawl': 10,
        }
        
        # Rate limiting for Firecrawl URL access
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
            },
            'map': {
                'limit': int(os.getenv('FIRECRAWL_RATE_LIMIT_MAP', 100)),
                'window': int(os.getenv('FIRECRAWL_RATE_LIMIT_WINDOW', 60000)),
                'requests': 0,
                'reset_time': 0.0
            },
            'crawl': {
                'limit': int(os.getenv('FIRECRAWL_RATE_LIMIT_CRAWL', 15)),
                'window': int(os.getenv('FIRECRAWL_RATE_LIMIT_WINDOW', 60000)),
                'requests': 0,
                'reset_time': 0.0
            }
        }
        
        print(f"🔥 Enhanced Firecrawl Research initialized successfully")
        print(f"   - URL: {self.firecrawl_api_url}")
        print(f"   - Max credits per query: {self.hobby_plan_limits['max_credits_per_query']}")
        print(f"   - Max search requests: {self.hobby_plan_limits['max_search_requests']}")
        print(f"   - Max depth: {self.hobby_plan_limits['max_depth']}")
        print(f"   - Max breadth: {self.hobby_plan_limits['max_breadth']}")
    
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
        """Check if we can make another request within credit limits"""
        cost = self.credit_costs.get(operation, 1)
        would_exceed_limit = (
            self.credit_tracker['current_query_credits'] + cost > 
            self.hobby_plan_limits['max_credits_per_query']
        )
        
        if would_exceed_limit:
            print(f"🚫 Credit limit reached! Would use {self.credit_tracker['current_query_credits'] + cost} credits (max: {self.hobby_plan_limits['max_credits_per_query']})")
            return False
        
        # Check operation-specific limits
        if operation == 'search' and self.credit_tracker['search_requests'] >= self.hobby_plan_limits['max_search_requests']:
            print(f"🚫 Search request limit reached! ({self.credit_tracker['search_requests']}/{self.hobby_plan_limits['max_search_requests']})")
            return False
        
        if operation == 'scrape' and self.credit_tracker['scrape_requests'] >= self.hobby_plan_limits['max_scrape_requests']:
            print(f"🚫 Scrape request limit reached! ({self.credit_tracker['scrape_requests']}/{self.hobby_plan_limits['max_scrape_requests']})")
            return False
        
        return True
    
    def track_credit_usage(self, operation: str) -> None:
        """Track credit usage"""
        cost = self.credit_costs.get(operation, 1)
        self.credit_tracker['current_query_credits'] += cost
        self.credit_tracker['total_credits'] += cost
        
        if operation == 'search':
            self.credit_tracker['search_requests'] += 1
        if operation == 'scrape':
            self.credit_tracker['scrape_requests'] += 1
        
        # Log if approaching limits
        if self.credit_tracker['current_query_credits'] > self.hobby_plan_limits['max_credits_per_query'] * 0.8:
            percentage = (self.credit_tracker['current_query_credits'] / self.hobby_plan_limits['max_credits_per_query']) * 100
            print(f"⚠️ Credits: {self.credit_tracker['current_query_credits']}/{self.hobby_plan_limits['max_credits_per_query']} ({percentage:.0f}%)")
    
    def reset_query_credits(self) -> None:
        """Reset credit tracking for new query"""
        self.credit_tracker['current_query_credits'] = 0
        self.credit_tracker['search_requests'] = 0
        self.credit_tracker['scrape_requests'] = 0
        self.credit_tracker['query_start_time'] = time.time()
    
    async def search_with_retry(self, query: str, options: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Search with retry logic and credit/rate limit handling"""
        print(f"🔍 Searching for: '{query}'")
        
        # Check credit limit before making any requests
        if not self.check_credit_limit('search'):
            raise Exception(f"Credit limit exceeded ({self.credit_tracker['current_query_credits']}/{self.hobby_plan_limits['max_credits_per_query']})")
        
        for attempt in range(max_retries):
            try:
                # Check rate limit before making request
                await self.check_rate_limit('search')
                
                # Make the search request
                response = await self._make_search_request(query, options or {})
                
                if response and response.get("success"):
                    self.track_credit_usage('search')
                    print(f"  ✅ Search successful (attempt {attempt + 1})")
                    return response
                elif response and response.get("error"):
                    error_msg = response.get("error", "").lower()
                    if "rate limit" in error_msg or "429" in error_msg or "service error" in error_msg:
                        print(f"  ⏳ Rate limited or service error, waiting... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(min(2 ** attempt, 3))
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
                    await asyncio.sleep(0.5)
                else:
                    return None
        
        return None
    
    async def _make_search_request(self, query: str, options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a search request to Firecrawl"""
        try:
            # Prepare request payload
            payload = {
                "query": query,
                "limit": options.get('limit', 8),
                "scrapeOptions": {
                    "formats": options.get('formats', ['markdown'])
                }
            }
            
            # Add timeout
            timeout = options.get('timeout', 20000) / 1000  # Convert to seconds
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.firecrawl_api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": data.get("data", [])
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def evaluate_source_reliability(self, domain: str, context: str) -> Tuple[float, str]:
        """Evaluate source reliability using Gemini"""
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

Provide your response in JSON format:
{{
    "score": <reliability_score>,
    "reasoning": "<brief explanation>",
    "domainExpertise": "<assessment of domain expertise>"
}}"""

            response = await self.gemini_model.generate_content_async(prompt)
            response_text = response.text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result.get('score', 0.5), result.get('reasoning', 'No reasoning provided')
            else:
                # Fallback parsing
                score_match = re.search(r'"score":\s*([0-9.]+)', response_text)
                reasoning_match = re.search(r'"reasoning":\s*"([^"]+)"', response_text)
                
                score = float(score_match.group(1)) if score_match else 0.5
                reasoning = reasoning_match.group(1) if reasoning_match else 'No reasoning provided'
                
                return score, reasoning
                
        except Exception as e:
            print(f"Error evaluating source reliability: {e}")
            return 0.5, "Error in evaluation"
    
    async def generate_search_queries(self, query: str, learnings: Optional[List[str]] = None, 
                                    learning_reliabilities: Optional[List[float]] = None,
                                    research_directions: Optional[List[ResearchDirection]] = None) -> List[Dict[str, Any]]:
        """Generate search queries using Gemini"""
        try:
            # Enforce hobby plan limits
            max_queries = self.hobby_plan_limits['max_breadth']
            
            # Convert to weighted learnings
            weighted_learnings = []
            if learnings and learning_reliabilities:
                weighted_learnings = [
                    {"content": content, "reliability": reliability}
                    for content, reliability in zip(learnings, learning_reliabilities)
                ]
            
            # Build prompt
            learnings_text = ""
            if weighted_learnings:
                learnings_text = f"""Here are previous learnings with their reliability scores (higher score means more reliable):
{chr(10).join([f"[Reliability: {l['reliability']:.2f}] {l['content']}" for l in weighted_learnings])}

When generating new queries:
- Follow up on promising leads from reliable sources (reliability >= 0.7)
- For less reliable information (reliability < 0.7), consider generating verification queries that are likely to find authoritative sources
- Make each query specific and targeted to advance the research in a clear direction"""
            
            directions_text = ""
            if research_directions:
                sorted_directions = sorted(research_directions, key=lambda x: x.priority, reverse=True)
                directions_text = f"""Prioritized research directions to explore (higher priority = more important):
{chr(10).join([f"[Priority: {d.priority}] {d.question}{f' (From previous goal: {d.parent_goal})' if d.parent_goal else ''}" for d in sorted_directions])}

Focus on generating queries that address these research directions, especially the higher priority ones."""
            
            prompt = f"""Generate search queries to thoroughly research the following topic: "{query}"

Create specific, targeted search queries that will help find comprehensive information about this topic. Each query should be designed to uncover different aspects or angles of the research topic.

{learnings_text}

{directions_text}

Generate up to {max_queries} search queries that will effectively research different aspects of: {query}

Provide your response in JSON format:
{{
    "queries": [
        {{
            "query": "<the SERP query>",
            "researchGoal": "<detailed research goal and additional research directions>",
            "reliabilityThreshold": <minimum reliability score between 0 and 1>,
            "isVerificationQuery": <true/false>,
            "relatedDirection": "<related research direction or null>"
        }}
    ]
}}"""

            response = await self.gemini_model.generate_content_async(prompt)
            response_text = response.text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                queries = result.get('queries', [])
                
                # Ensure we don't exceed limits
                limited_queries = queries[:max_queries]
                
                if len(queries) > max_queries:
                    print(f"🚫 Limited queries to {max_queries} for Hobby plan (generated: {len(queries)})")
                
                # Validate reliability thresholds
                validated_queries = []
                for query_item in limited_queries:
                    reliability_threshold = max(0, min(1, query_item.get('reliabilityThreshold', 0.5)))
                    validated_queries.append({
                        **query_item,
                        'reliabilityThreshold': reliability_threshold
                    })
                
                return validated_queries
            else:
                print("Failed to parse search queries from Gemini response")
                return []
                
        except Exception as e:
            print(f"Error generating search queries: {e}")
            return []
    
    async def process_search_results(self, query: str, result: Dict[str, Any], 
                                   reliability_threshold: float = 0.3,
                                   research_goal: str = "") -> Tuple[List[str], List[float], List[SourceMetadata]]:
        """Process search results and extract learnings"""
        try:
            if not result.get("success") or not result.get("data"):
                return [], [], []
            
            contents = []
            urls = []
            
            # Extract content and URLs
            for item in result["data"]:
                if item.get("markdown"):
                    contents.append(item["markdown"][:25000])  # Limit content length
                if item.get("url"):
                    urls.append(item["url"])
            
            if not contents:
                return [], [], []
            
            # Evaluate source reliability for each domain
            source_metadata = []
            for item in result["data"]:
                if item.get("url"):
                    try:
                        domain = urlparse(item["url"]).netloc
                        reliability_score, reliability_reasoning = await self.evaluate_source_reliability(domain, query)
                        
                        source_metadata.append(SourceMetadata(
                            url=item["url"],
                            title=item.get("title"),
                            domain=domain,
                            reliability_score=reliability_score,
                            reliability_reasoning=reliability_reasoning,
                            content_length=len(item.get("markdown", "")),
                            last_checked=datetime.now().isoformat()
                        ))
                    except Exception as e:
                        print(f"Error processing source metadata: {e}")
                        continue
            
            # Sort and filter by reliability
            content_with_metadata = list(zip(contents, source_metadata))
            filtered_content = [
                (content, metadata) for content, metadata in content_with_metadata
                if metadata.reliability_score >= reliability_threshold
            ]
            
            if not filtered_content:
                return [], [], []
            
            # Sort by reliability
            filtered_content.sort(key=lambda x: x[1].reliability_score, reverse=True)
            
            # Extract learnings using Gemini
            learnings, learning_reliabilities = await self.extract_learnings(
                [content for content, _ in filtered_content], 
                query, 
                research_goal
            )
            
            print(f"Found {len(contents)} sources ({len(filtered_content)} above reliability threshold)")
            
            # Return ALL source metadata, not just filtered ones
            return learnings, learning_reliabilities, source_metadata
            
        except Exception as e:
            print(f"Error processing search results: {e}")
            return [], [], []
    
    async def extract_learnings(self, contents: List[str], query: str, research_goal: str = "") -> Tuple[List[str], List[float]]:
        """Extract learnings from content using Gemini"""
        try:
            if not contents:
                return [], []
            
            # Combine content with reliability information
            combined_content = "\n\n---\n\n".join([
                f"Content {i+1}:\n{content}" for i, content in enumerate(contents)
            ])
            
            prompt = f"""Given the following contents from a SERP search for the query "{query}", generate a list of learnings from the contents. Return a maximum of 20 learnings, but feel free to return less if the contents are clear. Make sure each learning is unique and not similar to each other. The learnings should be concise and to the point, as detailed and information dense as possible. Make sure to include any entities like people, places, companies, products, things, etc in the learnings, as well as any exact metrics, numbers, or dates.

{f'Research Goal: {research_goal}' if research_goal else ''}

Contents:
{combined_content}

Provide your response in JSON format:
{{
    "learnings": [
        {{
            "content": "<learning content>",
            "confidence": <confidence score between 0 and 1>,
            "sources": ["<source domains>"],
            "dataType": "<regular|structured|combined>"
        }}
    ],
    "followUpQuestions": [
        {{
            "question": "<follow-up question>",
            "priority": <priority 1-5>,
            "reason": "<why this follow-up is needed>"
        }}
    ]
}}"""

            response = await self.gemini_model.generate_content_async(prompt)
            response_text = response.text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                learnings_data = result.get('learnings', [])
                
                learnings = [item.get('content', '') for item in learnings_data]
                reliabilities = [item.get('confidence', 0.5) for item in learnings_data]
                
                return learnings, reliabilities
            else:
                # Fallback: simple extraction
                return self._extract_simple_learnings(response_text)
                
        except Exception as e:
            print(f"Error extracting learnings: {e}")
            return [], []
    
    def _extract_simple_learnings(self, response_text: str) -> Tuple[List[str], List[float]]:
        """Fallback method to extract learnings from text response"""
        try:
            # Look for numbered or bulleted lists
            lines = response_text.split('\n')
            learnings = []
            
            for line in lines:
                line = line.strip()
                # Remove numbering or bullets
                line = re.sub(r'^[\d\-•\*]+\.?\s*', '', line)
                if line and len(line) > 20:  # Minimum length for a learning
                    learnings.append(line)
            
            # Limit to 20 learnings
            learnings = learnings[:20]
            reliabilities = [0.5] * len(learnings)  # Default reliability
            
            return learnings, reliabilities
            
        except Exception as e:
            print(f"Error in simple learning extraction: {e}")
            return [], []
    
    async def generate_comprehensive_report(self, query: str, learnings: List[str], 
                                          source_metadata: List[SourceMetadata],
                                          learning_reliabilities: List[float]) -> str:
        """Generate comprehensive report using Gemini"""
        try:
            if not learnings:
                return "No learnings available to generate report."
            
            # Prepare learnings with reliability scores
            learnings_text = "\n".join([
                f"<learning reliability=\"{reliability:.2f}\">\n{learning}\n</learning>"
                for learning, reliability in zip(learnings, learning_reliabilities)
            ])
            
            # Group sources by reliability
            high_reliability = [s for s in source_metadata if s.reliability_score >= 0.8]
            medium_reliability = [s for s in source_metadata if 0.6 <= s.reliability_score < 0.8]
            low_reliability = [s for s in source_metadata if 0.3 <= s.reliability_score < 0.6]
            
            # Prepare source reliability context
            source_context = f"""HIGH RELIABILITY SOURCES (≥80%): {len(high_reliability)} sources
{chr(10).join([f"- {s.domain}: {s.reliability_score*100:.0f}% - {s.reliability_reasoning}" for s in high_reliability])}

MEDIUM RELIABILITY SOURCES (60-79%): {len(medium_reliability)} sources
{chr(10).join([f"- {s.domain}: {s.reliability_score*100:.0f}% - {s.reliability_reasoning}" for s in medium_reliability])}

LOW RELIABILITY SOURCES (30-59%): {len(low_reliability)} sources
{chr(10).join([f"- {s.domain}: {s.reliability_score*100:.0f}% - {s.reliability_reasoning}" for s in low_reliability])}"""

            now = datetime.now().strftime("%B %d, %Y")
            
            prompt = f"""You are **Ubik Executive-Composer AI**. Today is {now}.

Create a comprehensive research report for the query: "{query}"

COMPREHENSIVE RESEARCH DATA:

RESEARCH LEARNINGS ({len(learnings)} total findings):
{learnings_text}

SOURCE RELIABILITY ANALYSIS:
{source_context}

REQUIREMENTS FOR COMPREHENSIVE REPORT:
1. Create a complete 10-15 page research report (2500-4000 words)
2. Include executive summary, detailed analysis sections, and conclusions
3. Use specific data points, company names, metrics, and statistics
4. Include 2-4 relevant charts using the chart_stub format
5. Reference source reliability levels throughout
6. Provide actionable insights and strategic recommendations
7. Include methodology section explaining data sources and quality
8. Add complete source references with reliability scores

Focus on creating ONE comprehensive, cohesive report that synthesizes ALL the research data provided above. Do not create separate sections or chunks - generate the complete report in this single response.

Generate the complete research report now:"""

            response = await self.gemini_model.generate_content_async(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error generating comprehensive report: {e}")
            return f"Error generating report: {str(e)}"
    
    async def deep_research(self, query: str, breadth: Optional[int] = None, depth: Optional[int] = None,
                           learnings: Optional[List[str]] = None, learning_reliabilities: Optional[List[float]] = None,
                           visited_urls: Optional[List[str]] = None, research_directions: Optional[List[ResearchDirection]] = None,
                           on_progress: Optional[Callable[[ResearchProgress], None]] = None) -> Dict[str, Any]:
        """Perform deep research with enhanced features"""
        
        # Reset credit tracking for new query
        self.reset_query_credits()
        
        # Enforce hobby plan limits
        enforced_depth = min(depth or 2, self.hobby_plan_limits['max_depth'])
        enforced_breadth = min(breadth or 4, self.hobby_plan_limits['max_breadth'])
        
        if depth and depth > self.hobby_plan_limits['max_depth']:
            print(f"Depth limited to {self.hobby_plan_limits['max_depth']} (requested: {depth})")
        if breadth and breadth > self.hobby_plan_limits['max_breadth']:
            print(f"Breadth limited to {self.hobby_plan_limits['max_breadth']} (requested: {breadth})")
        
        progress = ResearchProgress(
            current_depth=enforced_depth,
            total_depth=enforced_depth,
            current_breadth=enforced_breadth,
            total_breadth=enforced_breadth,
            total_queries=0,
            completed_queries=0
        )
        
        def report_progress(update: Dict[str, Any]):
            for key, value in update.items():
                setattr(progress, key, value)
            if on_progress:
                on_progress(progress)
        
        print(f"🚀 Starting enhanced research (max {self.hobby_plan_limits['max_credits_per_query']} credits)")
        
        # Initialize collections
        all_learnings = learnings or []
        all_learning_reliabilities = learning_reliabilities or []
        all_visited_urls = visited_urls or []
        all_source_metadata = []
        all_research_directions = research_directions or []
        
        # Generate initial search queries
        serp_queries = await self.generate_search_queries(
            query, all_learnings, all_learning_reliabilities, all_research_directions
        )
        
        report_progress({
            'total_queries': len(serp_queries),
            'current_query': serp_queries[0]['query'] if serp_queries else None
        })
        
        # Process queries sequentially to respect rate limits
        for i, serp_query in enumerate(serp_queries):
            try:
                # Check if we can still make requests within credit limit
                if not self.check_credit_limit('search'):
                    print("💳 Credit limit reached, stopping research")
                    break
                
                current_query = serp_query['query']
                report_progress({
                    'current_query': current_query,
                    'completed_queries': i
                })
                
                # Perform search
                result = await self.search_with_retry(
                    current_query,
                    {
                        'timeout': 20000,
                        'limit': 8,
                        'formats': ['markdown']
                    }
                )
                
                if result and result.get('success'):
                    # Process search results
                    new_learnings, new_reliabilities, new_metadata = await self.process_search_results(
                        current_query,
                        result,
                        reliability_threshold=serp_query.get('reliabilityThreshold', 0.3),
                        research_goal=serp_query.get('researchGoal', '')
                    )
                    
                    # Add new data to collections
                    all_learnings.extend(new_learnings)
                    all_learning_reliabilities.extend(new_reliabilities)
                    all_source_metadata.extend(new_metadata)
                    
                    # Add new URLs
                    if result.get('data'):
                        new_urls = [item.get('url') for item in result['data'] if item.get('url')]
                        all_visited_urls.extend(new_urls)
                    
                    print(f"✅ Query {i+1}/{len(serp_queries)} completed: {len(new_learnings)} learnings")
                else:
                    print(f"⚠️ Query {i+1}/{len(serp_queries)} failed")
                
            except Exception as e:
                print(f"❌ Error processing query {i+1}: {e}")
                continue
        
        # Remove duplicates
        all_learnings = list(dict.fromkeys(all_learnings))  # Preserve order
        all_visited_urls = list(dict.fromkeys(all_visited_urls))
        
        # Generate comprehensive report
        print("📝 Generating comprehensive report...")
        comprehensive_report = await self.generate_comprehensive_report(
            query, all_learnings, all_source_metadata, all_learning_reliabilities
        )
        
        print(f"✅ Enhanced research completed: {len(all_learnings)} learnings from {len(all_source_metadata)} sources ({self.credit_tracker['current_query_credits']} credits)")
        
        return {
            "learnings": all_learnings,
            "learning_reliabilities": all_learning_reliabilities,
            "visited_urls": all_visited_urls,
            "source_metadata": all_source_metadata,
            "comprehensive_report": comprehensive_report,
            "requests_used": self.credit_tracker['current_query_credits'],
            "success": True
        }


async def main():
    """Test the enhanced Firecrawl research"""
    try:
        research = EnhancedFirecrawlResearch()
        
        def progress_callback(progress: ResearchProgress):
            print(f"Progress: {progress.completed_queries}/{progress.total_queries} queries completed")
        
        result = await research.deep_research(
            query="artificial intelligence trends 2024",
            breadth=3,
            depth=2,
            on_progress=progress_callback
        )
        
        print(f"Research completed successfully!")
        print(f"Learnings: {len(result['learnings'])}")
        print(f"Sources: {len(result['source_metadata'])}")
        print(f"Report length: {len(result['comprehensive_report'])} characters")
        
    except Exception as e:
        print(f"Error in main: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 