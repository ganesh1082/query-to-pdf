# AI-Powered Report Generator v2.1 (Typst Edition)

A professional AI-driven research report generator that uses Google's Gemini API and Typst for PDF rendering. Now supports real-time web research using **FIRECRAWL_API_URL** (no API key required).

## 🌟 Key Features

- **AI-Powered Content Generation**: Uses Google's Gemini API for intelligent report creation
- **Real-Time Web Research**: Integrates with Firecrawl for live web data collection
- **Professional PDF Output**: Generates beautiful reports using Typst
- **Dynamic Visualizations**: Creates charts and graphs based on content
- **Multiple Templates**: Choose from different professional report styles
- **Comprehensive Debug Logging**: Detailed logging for easy troubleshooting

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Typst compiler installed
- Google Gemini API key
- Firecrawl API URL (optional, for web research)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd query-to-pdf
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (for web research)
FIRECRAWL_API_URL=https://firecrawl.solarpunk.technology/v1/search

# Company Configuration
COMPANY_NAME=Your Company
AUTHOR=Your Name
ORGANIZATION=Your Organization
COMPANY_LOGO_PATH=assets/logo.png
```

### Usage

#### Basic Report Generation

```bash
python index.py --prompt "Your research topic here"
```

#### With Web Research

```bash
python index.py --prompt "Your research topic here" --web-research
```

#### Custom Template

```bash
python index.py --prompt "Your research topic here" --template template_2 --web-research
```

#### Advanced Options

```bash
python index.py \
  --prompt "Tesla electric vehicle market analysis" \
  --web-research \
  --breadth 6 \
  --depth 3 \
  --template template_1
```

## 🔧 Configuration

### Environment Variables

| Variable            | Required | Description                             |
| ------------------- | -------- | --------------------------------------- |
| `GEMINI_API_KEY`    | ✅       | Your Google Gemini API key              |
| `FIRECRAWL_API_URL` | ❌       | Firecrawl API endpoint for web research |
| `COMPANY_NAME`      | ❌       | Your company name for reports           |
| `AUTHOR`            | ❌       | Report author name                      |
| `ORGANIZATION`      | ❌       | Organization name                       |
| `COMPANY_LOGO_PATH` | ❌       | Path to company logo                    |

### Command Line Options

| Option           | Description                | Default    |
| ---------------- | -------------------------- | ---------- |
| `--prompt`       | Research topic or prompt   | Required   |
| `--web-research` | Enable web research        | False      |
| `--template`     | Template to use            | template_1 |
| `--breadth`      | Research breadth (queries) | 4          |
| `--depth`        | Research depth (levels)    | 2          |

## 📊 Web Research Features

### Firecrawl Integration

- **No API Key Required**: Uses direct URL access via `FIRECRAWL_API_URL`
- **Real-Time Data**: Fetches current information from the web
- **Source Reliability**: Evaluates and scores source credibility
- **Intelligent Queries**: Generates optimized search queries
- **Comprehensive Coverage**: Combines breadth and depth research

### Research Process

1. **Query Generation**: AI creates optimized search queries
2. **Web Scraping**: Fetches content from multiple sources
3. **Reliability Assessment**: Evaluates source credibility
4. **Content Extraction**: Extracts key learnings and insights
5. **Report Integration**: Incorporates findings into final report

## 🎨 Templates

### Available Templates

- `template_0`: Professional business style
- `template_1`: Modern corporate design (default)
- `template_2`: Academic/research style

### Customization

Templates can be customized by modifying the `.typ` files in the `templates/` directory.

## 📈 Debug Logging

The system provides comprehensive debug logging to help troubleshoot issues:

### Environment Debug

```
🔄 Loading environment variables...
✅ Environment loaded from: /path/to/.env
🔍 Environment Debug Info:
   GEMINI_API_KEY: ✅ Set
   FIRECRAWL_API_URL: ✅ Set
   FIRECRAWL_API_URL value: https://firecrawl.solarpunk.technology/v1/search
```

### Web Research Debug

```
🌐 Making request to Firecrawl URL: https://firecrawl.solarpunk.technology/v1/search
📤 Request payload: {"query": "...", "limit": 5, "scrapeOptions": {"formats": ["markdown"]}}
📥 Response status: 200
✅ Request successful - Found 5 results
```

### Report Generation Debug

```
🔧 Initializing report generator...
✅ Firecrawl research initialized successfully
🎯 Starting report generation...
📊 Phase 2: Creating dynamic data visualizations...
🚀 Phase 3: Compiling the final PDF report with Typst...
```

## 📁 Output

Reports are generated in the `generated_reports/` directory with the following naming convention:

```
{report_number}_{sanitized_title}.pdf
```

Example: `1751878321_Tesla_electric_vehicle_market_analysis.pdf`

## 🔍 Troubleshooting

### Common Issues

1. **Missing GEMINI_API_KEY**

   ```
   ❌ Error: GEMINI_API_KEY not found in environment variables
   ```

   Solution: Set your Gemini API key in the `.env` file

2. **Missing FIRECRAWL_API_URL**

   ```
   ❌ Error: FIRECRAWL_API_URL not found in environment variables
   ```

   Solution: Set the Firecrawl URL in your `.env` file or disable web research

3. **Typst Not Found**
   ```
   ❌ Typst compiler not found
   ```
   Solution: Install Typst from https://typst.app/

### Debug Mode

The system automatically provides detailed logging. Look for:

- 🔍 Debug messages for detailed process information
- ✅ Success indicators
- ❌ Error messages with context
- ⚠️ Warning messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- Firecrawl for web research integration
- Typst for PDF generation
- The open-source community for various dependencies
