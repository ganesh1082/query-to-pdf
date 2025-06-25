"""
Google API Integration Module
Provides enhanced research capabilities using Google APIs
"""

import os
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class GoogleAPIClient:
    """Enhanced Google API client for research and data collection"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_web(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search the web using Google Custom Search API"""
        
        try:
            # Use Google Custom Search API
            search_url = f"{self.base_url}/customsearch/v1"
            params = {
                "key": self.api_key,
                "cx": os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID", ""),  # Custom Search Engine ID
                "q": query,
                "num": min(max_results, 10),  # Max 10 results per request
                "dateRestrict": "m6",  # Last 6 months
                "sort": "date"  # Sort by date
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_search_results(data)
                else:
                    print(f"⚠️ Google search failed: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"⚠️ Google search error: {e}")
            return []
    
    async def search_news(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Google News for recent articles"""
        
        try:
            # Use Google News API (if available) or fallback to web search
            news_url = f"{self.base_url}/news/v1/search"
            params = {
                "key": self.api_key,
                "q": query,
                "maxResults": max_results,
                "orderBy": "publishedAt"
            }
            
            async with self.session.get(news_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_news_results(data)
                else:
                    # Fallback to web search with news-specific query
                    news_query = f"{query} news recent"
                    return await self.search_web(news_query, max_results)
                    
        except Exception as e:
            print(f"⚠️ Google news search error: {e}")
            # Fallback to web search
            news_query = f"{query} news recent"
            return await self.search_web(news_query, max_results)
    
    async def get_trending_topics(self, category: str = "business") -> List[str]:
        """Get trending topics in a specific category"""
        
        try:
            # Use Google Trends API or similar
            trends_url = f"{self.base_url}/trends/v1/dailyTrends"
            params = {
                "key": self.api_key,
                "geo": "US",  # Default to US, can be made configurable
                "cat": category
            }
            
            async with self.session.get(trends_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_trending_topics(data)
                else:
                    return []
                    
        except Exception as e:
            print(f"⚠️ Google trends error: {e}")
            return []
    
    async def get_company_info(self, company_name: str) -> Dict[str, Any]:
        """Get comprehensive company information"""
        
        try:
            # Search for company information
            company_query = f"{company_name} company profile financial information"
            search_results = await self.search_web(company_query, 5)
            
            # Extract relevant information
            company_info = {
                "name": company_name,
                "search_results": search_results,
                "last_updated": datetime.now().isoformat(),
                "sources": [result.get("url", "") for result in search_results]
            }
            
            return company_info
            
        except Exception as e:
            print(f"⚠️ Company info error: {e}")
            return {"name": company_name, "error": str(e)}
    
    async def get_market_data(self, sector: str) -> Dict[str, Any]:
        """Get market data for a specific sector"""
        
        try:
            # Search for market data and reports
            market_query = f"{sector} market analysis trends 2024"
            search_results = await self.search_web(market_query, 8)
            
            # Also get news for recent developments
            news_results = await self.search_news(f"{sector} market", 5)
            
            market_data = {
                "sector": sector,
                "search_results": search_results,
                "news_results": news_results,
                "last_updated": datetime.now().isoformat(),
                "total_sources": len(search_results) + len(news_results)
            }
            
            return market_data
            
        except Exception as e:
            print(f"⚠️ Market data error: {e}")
            return {"sector": sector, "error": str(e)}
    
    def _parse_search_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Google search results"""
        
        results = []
        items = data.get("items", [])
        
        for item in items:
            result = {
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source": self._extract_domain(item.get("link", "")),
                "published_date": item.get("pagemap", {}).get("metatags", [{}])[0].get("article:published_time", ""),
                "search_rank": len(results) + 1
            }
            results.append(result)
        
        return results
    
    def _parse_news_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Google news results"""
        
        results = []
        articles = data.get("articles", [])
        
        for article in articles:
            result = {
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "snippet": article.get("description", ""),
                "source": article.get("source", {}).get("name", ""),
                "published_date": article.get("publishedAt", ""),
                "content_type": "news"
            }
            results.append(result)
        
        return results
    
    def _parse_trending_topics(self, data: Dict[str, Any]) -> List[str]:
        """Parse trending topics from Google Trends"""
        
        topics = []
        trending_searches = data.get("default", {}).get("trendingSearchesDays", [])
        
        for day in trending_searches:
            searches = day.get("trendingSearches", [])
            for search in searches:
                title = search.get("title", {}).get("query", "")
                if title:
                    topics.append(title)
        
        return topics[:10]  # Return top 10 trending topics
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url


class EnhancedGoogleResearch:
    """Enhanced research capabilities using Google APIs"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
    
    async def __aenter__(self):
        self.client = GoogleAPIClient(self.api_key)
        await self.client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def comprehensive_research(self, topic: str, keywords: List[str]) -> Dict[str, Any]:
        """Perform comprehensive research using Google APIs"""
        
        research_data = {
            "topic": topic,
            "keywords": keywords,
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "news_articles": [],
            "trending_topics": [],
            "market_insights": []
        }
        
        try:
            # Search for general information
            print(f"  🔍 Searching Google for: {topic}")
            search_results = await self.client.search_web(topic, 10)
            research_data["sources"].extend(search_results)
            
            # Search for news
            print(f"  📰 Searching news for: {topic}")
            news_results = await self.client.search_news(topic, 8)
            research_data["news_articles"].extend(news_results)
            
            # Get trending topics in related categories
            print(f"  📈 Getting trending topics...")
            trending_topics = await self.client.get_trending_topics("business")
            research_data["trending_topics"] = trending_topics
            
            # Search for each keyword
            for keyword in keywords[:5]:  # Limit to first 5 keywords
                print(f"  🔍 Searching keyword: {keyword}")
                keyword_results = await self.client.search_web(f"{topic} {keyword}", 5)
                research_data["sources"].extend(keyword_results)
            
            # Get market insights
            print(f"  📊 Getting market insights...")
            market_data = await self.client.get_market_data(topic)
            research_data["market_insights"] = market_data
            
            print(f"  ✅ Google research completed - {len(research_data['sources'])} sources found")
            
        except Exception as e:
            print(f"  ⚠️ Google research error: {e}")
            research_data["error"] = str(e)
        
        return research_data
    
    async def validate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and score sources based on credibility"""
        
        validated_sources = []
        
        for source in sources:
            credibility_score = self._calculate_credibility_score(source)
            
            validated_source = {
                **source,
                "credibility_score": credibility_score,
                "validation_status": "validated" if credibility_score > 0.6 else "low_credibility",
                "validation_timestamp": datetime.now().isoformat()
            }
            
            validated_sources.append(validated_source)
        
        # Sort by credibility score
        validated_sources.sort(key=lambda x: x["credibility_score"], reverse=True)
        
        return validated_sources
    
    def _calculate_credibility_score(self, source: Dict[str, Any]) -> float:
        """Calculate credibility score for a source"""
        
        score = 0.5  # Base score
        
        # Domain credibility
        domain = source.get("source", "").lower()
        credible_domains = [
            "reuters.com", "bloomberg.com", "wsj.com", "ft.com", "economist.com",
            "mckinsey.com", "bcg.com", "bain.com", "deloitte.com", "pwc.com",
            "statista.com", "marketresearch.com", "ibisworld.com", "forrester.com",
            "gartner.com", "idc.com", "crunchbase.com", "pitchbook.com"
        ]
        
        if any(credible_domain in domain for credible_domain in credible_domains):
            score += 0.3
        
        # Content length (longer content often more credible)
        snippet_length = len(source.get("snippet", ""))
        if snippet_length > 200:
            score += 0.1
        
        # Recency (newer content preferred)
        if source.get("published_date"):
            score += 0.1
        
        return min(score, 1.0)


# Utility functions for easy integration
async def get_google_research_data(topic: str, keywords: List[str], api_key: str) -> Dict[str, Any]:
    """Convenience function to get Google research data"""
    
    async with EnhancedGoogleResearch(api_key) as researcher:
        return await researcher.comprehensive_research(topic, keywords)


async def validate_google_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience function to validate sources"""
    
    # Create a temporary researcher for validation
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        return sources  # Return original sources if no API key
    
    async with EnhancedGoogleResearch(api_key) as researcher:
        return await researcher.validate_sources(sources) 