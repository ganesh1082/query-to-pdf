# Changelog

## [2.1.0] - 2025-07-07

### 🚀 Major Changes

#### FIRECRAWL_API_URL Integration

- **Removed API key dependency**: The system now works with `FIRECRAWL_API_URL` only, no API key required
- **Direct URL access**: Uses direct HTTP requests to the Firecrawl endpoint
- **Simplified configuration**: Only need to set `FIRECRAWL_API_URL` in `.env` file

#### Enhanced Debug Logging

- **Comprehensive logging**: Added detailed debug information throughout the entire process
- **Environment validation**: Clear feedback on configuration status
- **Request/response tracking**: Detailed logging of web research requests
- **Progress indicators**: Real-time progress updates during report generation

### 🔧 Technical Improvements

#### FirecrawlResearch Class

- Removed `firecrawl_api_key` parameter from constructor
- Added validation for `FIRECRAWL_API_URL` environment variable
- Simplified request handling to use direct URL access only
- Replaced credit tracking with request tracking
- Enhanced error handling and logging

#### FirecrawlReportGenerator Class

- Updated constructor to only require `gemini_api_key`
- Improved initialization error handling
- Enhanced debug output for research process
- Better fallback handling when web research fails

#### Main Application

- Updated `ProfessionalReportGenerator` to work without Firecrawl API key
- Improved error messages and validation
- Enhanced debug logging throughout the pipeline

#### Index.py

- Added comprehensive environment validation
- Enhanced debug output for configuration
- Improved error handling and user feedback
- Added detailed progress reporting

### 📝 Documentation Updates

#### README.md

- Complete rewrite to reflect new FIRECRAWL_API_URL approach
- Added comprehensive usage examples
- Included debug logging documentation
- Added troubleshooting section
- Updated configuration instructions

### 🐛 Bug Fixes

- Fixed type annotation issues in main application
- Improved error handling for missing environment variables
- Enhanced JSON parsing error handling in web research
- Fixed chart path resolution issues

### 🔄 Migration Guide

#### From v2.0 to v2.1

1. **Update .env file**:

   ```env
   # Remove this line (no longer needed)
   # FIRECRAWL_API_KEY=your_api_key_here

   # Add this line (required for web research)
   FIRECRAWL_API_URL=https://firecrawl.solarpunk.technology/v1/search
   ```

2. **Update code usage**:

   ```python
   # Old way (v2.0)
   generator = ProfessionalReportGenerator(gemini_api_key, firecrawl_api_key)

   # New way (v2.1)
   generator = ProfessionalReportGenerator(gemini_api_key)
   ```

3. **Command line usage remains the same**:
   ```bash
   python index.py --prompt "Your topic" --web-research
   ```

### ✨ New Features

- **No API key required**: Web research works with URL only
- **Enhanced debugging**: Comprehensive logging for troubleshooting
- **Better error messages**: Clear feedback on configuration issues
- **Improved reliability**: Better fallback handling

### 📊 Performance

- Reduced API key management complexity
- Improved error recovery
- Enhanced monitoring capabilities
- Better resource tracking

---

## [2.0.0] - Previous Version

### Features

- AI-powered report generation with Gemini API
- Typst PDF rendering
- Dynamic chart generation
- Multiple template support
- Basic web research with Firecrawl API key
