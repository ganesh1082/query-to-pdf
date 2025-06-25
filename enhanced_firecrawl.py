# query-to-pdf copy/enhanced_firecrawl.py

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import aiohttp
import asyncio
import json

@dataclass
class ResearchQuery:
    topic: str
    keywords: List[str]
    sources: List[str] 
    depth: str
    timeframe: str

class AdvancedFirecrawlClient:
    """A robust research client using direct aiohttp requests for maximum control."""
    
    def __init__(self, api_key: Optional[str]):
        self.api_key = api_key
        self.base_url = "https://api.firecrawl.dev/v0"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def intelligent_research_pipeline(self, query: ResearchQuery) -> Dict[str, Any]:
        """Performs web research with Firecrawl using direct API calls."""
        if not self.api_key:
            print("⚠️ Firecrawl API key not found. Using mock research data.")
            return self._get_mock_research_data(query.topic)

        try:
            print("🔍 Phase 1a: Searching for relevant URLs with Firecrawl...")
            search_payload = {
                "query": f"in-depth market analysis and investment trends for {query.topic}",
                "searchOptions": {"limit": 5}
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            search_results = []
            async with self.session.post(f"{self.base_url}/search", json=search_payload, headers=headers, timeout=30) as response:
                if response.status == 200:
                    search_results = await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Firecrawl search failed with status {response.status}: {error_text}")

            if not search_results or not search_results.get('data'):
                raise ValueError("Search returned no results.")

            urls_to_scrape = [result['url'] for result in search_results['data'] if 'url' in result]
            print(f"  ✅ Found {len(urls_to_scrape)} relevant URLs to analyze.")

            print("🔍 Phase 1b: Scraping content from top URLs...")
            tasks = [self._scrape_url(url) for url in urls_to_scrape]
            scrape_results = await asyncio.gather(*tasks)

            scraped_data = [res for res in scrape_results if res]
            if not scraped_data:
                raise ValueError("Scraping the found URLs yielded no content.")

            print(f"  ✅ Successfully scraped content from {len(scraped_data)} sources.")
            return {"scraped_sources": scraped_data, "query": query.topic}

        except Exception as e:
            print(f"❌ Firecrawl pipeline failed: {e}")
            print("  ⚠️ Falling back to mock research data.")
            return self._get_mock_research_data(query.topic)

    async def _scrape_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrapes a single URL using a direct API call."""
        scrape_payload = {"url": url, "pageOptions": {"onlyMainContent": True}}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        try:
            async with self.session.post(f"{self.base_url}/scrape", json=scrape_payload, headers=headers, timeout=25) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "url": url,
                        "title": data.get("data", {}).get("metadata", {}).get("title", "No Title"),
                        "content": data.get("data", {}).get("markdown", "No content found.")
                    }
                return None
        except Exception as e:
            print(f"  ❌ Network or timeout error scraping {url}: {e}")
            return None

    def _get_mock_research_data(self, topic: str) -> Dict[str, Any]:
        """Provides high-quality mock research data as a fallback."""
        return {
            "query": topic,
            "scraped_sources": [
                {"url": "mock://forbes.com/market-analysis", "title": "Mock Analysis", "content": "**Market Analysis:** The market is projected to grow significantly."},
                {"url": "mock://techcrunch.com/investment-trends", "title": "Mock VC Funding", "content": "**VC Funding:** Funding for startups hit a record high."}
            ]
        }