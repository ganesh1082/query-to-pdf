# Google API Integration Setup Guide

This guide will help you set up Google API integration for enhanced research capabilities.

## Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account
- Google API key

## Step 1: Install Dependencies

First, install the required Google API dependencies:

```bash
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

Or update your requirements.txt and install:

```bash
pip install -r requirements.txt
```

## Step 2: Get Google API Key

### Option A: Google Cloud Console (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Custom Search API
   - Google News API (if available)
   - Google Trends API (if available)
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy your API key

### Option B: Google Custom Search Engine (Alternative)

1. Go to [Google Custom Search](https://cse.google.com/)
2. Create a new search engine
3. Get your Search Engine ID (cx parameter)
4. Use a simple API key from Google Cloud Console

## Step 3: Configure Environment Variables

Add your Google API key to your `.env` file:

```env
# Existing keys
OPENAI_API_KEY=your-openai-api-key
FIRECRAWL_API_KEY=your-firecrawl-api-key

# New Google API key
GOOGLE_API_KEY=your-google-api-key

# Optional: Google Custom Search Engine ID
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your-search-engine-id
```

## Step 4: Test the Integration

Run the demo to test your Google API integration:

```bash
python google_api_demo.py
```

This will:

- Test your API key
- Perform sample research
- Show source validation
- Display trending topics

## Step 5: Use in Main Application

The main application now supports Google API integration. Run it normally:

```bash
python index.py
```

The system will automatically:

- Use Google APIs for enhanced research
- Validate sources using Google data
- Get trending topics and market insights
- Provide more comprehensive research results

## Features Available

### 1. Enhanced Web Search

- Google Custom Search API integration
- Real-time web research
- Source credibility scoring
- Date-restricted searches

### 2. News Research

- Google News API integration
- Recent article discovery
- News trend analysis
- Source validation

### 3. Market Intelligence

- Company information gathering
- Sector-specific research
- Market trend analysis
- Competitive intelligence

### 4. Source Validation

- Automatic credibility scoring
- Domain reputation checking
- Content quality assessment
- Source ranking

## API Usage and Limits

### Google Custom Search API

- **Free tier**: 100 queries per day
- **Paid tier**: $5 per 1000 queries
- **Rate limit**: 10,000 queries per day

### Google News API

- **Availability**: Limited access
- **Rate limits**: Varies by plan
- **Fallback**: Web search with news keywords

### Google Trends API

- **Availability**: Limited access
- **Rate limits**: Varies by plan
- **Fallback**: Manual trend analysis

## Troubleshooting

### Common Issues

1. **API Key Not Working**

   - Verify the API key is correct
   - Check if APIs are enabled in Google Cloud Console
   - Ensure billing is set up (if required)

2. **Rate Limiting**

   - Check your API usage in Google Cloud Console
   - Implement rate limiting in your code
   - Consider upgrading to paid tier

3. **Import Errors**

   - Ensure all dependencies are installed
   - Check Python version compatibility
   - Verify import paths

4. **No Results**
   - Check if your search queries are too specific
   - Verify API quotas and limits
   - Test with simpler queries first

### Error Messages

- `"Google API integration not available"`: Install missing dependencies
- `"API key not found"`: Add GOOGLE_API_KEY to .env file
- `"Rate limit exceeded"`: Wait or upgrade API plan
- `"Invalid API key"`: Check key format and permissions

## Advanced Configuration

### Custom Search Engine Setup

1. Go to [Google Custom Search](https://cse.google.com/)
2. Create a new search engine
3. Add sites to search (optional)
4. Get your Search Engine ID
5. Add to .env file: `GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your-id`

### Rate Limiting

Add rate limiting to avoid hitting API limits:

```python
import asyncio
import time

class RateLimitedGoogleClient:
    def __init__(self, api_key: str, requests_per_second: int = 10):
        self.api_key = api_key
        self.requests_per_second = requests_per_second
        self.last_request_time = 0

    async def make_request(self, *args, **kwargs):
        # Rate limiting logic
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < 1.0 / self.requests_per_second:
            await asyncio.sleep(1.0 / self.requests_per_second - time_since_last)

        self.last_request_time = time.time()
        # Make actual request here
```

### Error Handling

Implement robust error handling:

```python
async def safe_google_search(self, query: str):
    try:
        return await self.google_client.search_web(query)
    except Exception as e:
        print(f"Google search failed: {e}")
        # Fallback to other sources
        return await self.fallback_search(query)
```

## Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables for all keys**
3. **Implement proper error handling**
4. **Monitor API usage and costs**
5. **Use least privilege principle for API permissions**

## Support

For issues with Google API integration:

1. Check the troubleshooting section above
2. Verify your API key and permissions
3. Test with the demo script
4. Check Google Cloud Console for usage and errors
5. Review Google API documentation

## Next Steps

After setting up Google API integration:

1. **Customize research topics** in your main application
2. **Adjust search parameters** for better results
3. **Monitor API usage** to optimize costs
4. **Integrate with other data sources** for comprehensive research
5. **Build custom research workflows** for your specific needs
