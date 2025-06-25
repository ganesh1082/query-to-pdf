"""
Google API Integration Demo
Shows how to use the Google API integration with the research system
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def demo_google_api_integration():
    """Demo the Google API integration"""
    
    print("🔍 Google API Integration Demo")
    print("=" * 50)
    
    # Get API keys
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if not google_api_key:
        print("❌ Google API key not found in environment variables")
        print("Please set GOOGLE_API_KEY in your .env file")
        return
    
    try:
        # Import the Google API integration
        from google_api_integration import EnhancedGoogleResearch, get_google_research_data
        
        print(f"✅ Google API key found: {google_api_key[:10]}...")
        
        # Example research topic
        topic = "Anthill Ventures investment portfolio analysis"
        keywords = ["venture capital", "startup funding", "Southeast Asia", "B2B SaaS"]
        
        print(f"\n📊 Research Topic: {topic}")
        print(f"🔑 Keywords: {', '.join(keywords)}")
        
        # Perform comprehensive research
        print(f"\n🔍 Starting Google API research...")
        
        async with EnhancedGoogleResearch(google_api_key) as researcher:
            # Get comprehensive research data
            research_data = await researcher.comprehensive_research(topic, keywords)
            
            print(f"\n✅ Research completed!")
            print(f"📊 Sources found: {len(research_data.get('sources', []))}")
            print(f"📰 News articles: {len(research_data.get('news_articles', []))}")
            print(f"📈 Trending topics: {len(research_data.get('trending_topics', []))}")
            
            # Show some sample results
            if research_data.get('sources'):
                print(f"\n📋 Sample Sources:")
                for i, source in enumerate(research_data['sources'][:3]):
                    print(f"  {i+1}. {source.get('title', 'No title')}")
                    print(f"     URL: {source.get('url', 'No URL')}")
                    print(f"     Source: {source.get('source', 'Unknown')}")
                    print()
            
            if research_data.get('news_articles'):
                print(f"📰 Recent News:")
                for i, article in enumerate(research_data['news_articles'][:2]):
                    print(f"  {i+1}. {article.get('title', 'No title')}")
                    print(f"     Source: {article.get('source', 'Unknown')}")
                    print(f"     Date: {article.get('published_date', 'Unknown')}")
                    print()
            
            if research_data.get('trending_topics'):
                print(f"📈 Trending Topics:")
                for i, topic in enumerate(research_data['trending_topics'][:5]):
                    print(f"  {i+1}. {topic}")
                print()
            
            # Validate sources
            print(f"🔍 Validating sources...")
            validated_sources = await researcher.validate_sources(research_data.get('sources', []))
            
            print(f"✅ Source validation completed!")
            print(f"📊 High credibility sources: {len([s for s in validated_sources if s.get('credibility_score', 0) > 0.8])}")
            
            # Show credibility scores
            if validated_sources:
                print(f"\n📊 Top Sources by Credibility:")
                for i, source in enumerate(validated_sources[:3]):
                    score = source.get('credibility_score', 0)
                    print(f"  {i+1}. {source.get('title', 'No title')}")
                    print(f"     Credibility: {score:.2f}")
                    print(f"     Status: {source.get('validation_status', 'Unknown')}")
                    print()
        
        print(f"🎉 Google API integration demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Google API integration not available: {e}")
        print("Please install the required dependencies:")
        print("pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2")
        
    except Exception as e:
        print(f"❌ Error during Google API demo: {e}")
        print("Please check your API key and internet connection")


async def demo_company_research():
    """Demo company-specific research"""
    
    print("\n🏢 Company Research Demo")
    print("=" * 30)
    
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if not google_api_key:
        print("❌ Google API key not found")
        return
    
    try:
        from google_api_integration import GoogleAPIClient
        
        async with GoogleAPIClient(google_api_key) as client:
            # Research a specific company
            company_name = "Anthill Ventures"
            
            print(f"🔍 Researching company: {company_name}")
            
            company_info = await client.get_company_info(company_name)
            
            print(f"✅ Company research completed!")
            print(f"📊 Sources found: {len(company_info.get('search_results', []))}")
            
            if company_info.get('search_results'):
                print(f"\n📋 Company Information Sources:")
                for i, result in enumerate(company_info['search_results'][:3]):
                    print(f"  {i+1}. {result.get('title', 'No title')}")
                    print(f"     URL: {result.get('url', 'No URL')}")
                    print(f"     Source: {result.get('source', 'Unknown')}")
                    print()
            
            # Get market data for a sector
            sector = "venture capital"
            print(f"📊 Getting market data for: {sector}")
            
            market_data = await client.get_market_data(sector)
            
            print(f"✅ Market data retrieved!")
            print(f"📊 Total sources: {market_data.get('total_sources', 0)}")
            print(f"📰 News articles: {len(market_data.get('news_results', []))}")
            
    except Exception as e:
        print(f"❌ Error during company research: {e}")


async def main():
    """Main demo function"""
    
    print("🚀 Google API Integration Demo")
    print("Enhanced Research System with Google APIs")
    print("=" * 60)
    
    # Run the demos
    await demo_google_api_integration()
    await demo_company_research()
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Add your Google API key to .env file")
    print(f"   2. Set up Google Custom Search Engine (optional)")
    print(f"   3. Run the main application with Google integration")
    print(f"   4. Customize research topics and keywords")


if __name__ == "__main__":
    asyncio.run(main()) 