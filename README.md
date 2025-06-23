# Deep Research Report Generator

A comprehensive professional research report generator that combines OpenAI's GPT models with Firecrawl web scraping to create detailed, visually appealing PDF reports with AI-generated images and data visualizations.

## Features

- 🔍 **Comprehensive Web Research**: Uses Firecrawl for intelligent web scraping and data collection
- 🤖 **AI-Powered Content Generation**: Leverages OpenAI GPT-4 for professional report writing
- 🎨 **AI Image Generation**: Creates custom illustrations using DALL-E 3
- 📊 **Data Visualizations**: Generates professional charts and graphs with Matplotlib/Seaborn
- 📄 **Professional PDF Generation**: Creates polished reports with ReportLab
- 🎯 **Multiple Report Types**: Market research, industry analysis, competitive analysis, and more

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Firecrawl API key

## Quick Setup

### 1. Clone and Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your API keys
nano .env  # or use any text editor
```

Add your API keys to the `.env` file:
```
OPENAI_API_KEY=your-actual-openai-api-key
FIRECRAWL_API_KEY=your-actual-firecrawl-api-key
```

### 3. Create Assets Directory (Optional)

```bash
mkdir -p assets
# Add your company logo to assets/logo.png if desired
```

## Usage

### Running the Default Example

```bash
python index.py
```

### Customizing Your Report

Edit the `main()` function in `index.py` to customize:

- **Report Configuration**: Title, subtitle, company info, branding colors
- **Research Query**: Topic, keywords, sources, depth of research
- **Report Type**: Choose from market research, industry analysis, etc.

Example customization:

```python
# Configuration
config = ReportConfig(
    title="Your Custom Report Title",
    subtitle="Your Custom Subtitle",
    author="Your Name",
    company="Your Company",
    report_type=ReportType.MARKET_RESEARCH,
    research_objectives=[
        "Your first objective",
        "Your second objective"
    ],
    target_audience="Your target audience",
    brand_colors={
        "primary": "#your-primary-color",
        "secondary": "#your-secondary-color",
        "accent": "#your-accent-color"
    }
)

# Research query
research_query = ResearchQuery(
    topic="Your Research Topic",
    keywords=["keyword1", "keyword2", "keyword3"],
    sources=["industry reports", "academic papers"],
    depth="comprehensive",
    timeframe="current"
)
```

## Project Structure

```
deep-research/
├── index.py              # Main application file
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Your actual environment variables (create this)
├── README.md            # This file
├── setup.py             # Package setup
└── assets/              # Optional: logos and images
    └── logo.png         # Your company logo
```

## Report Types Available

- `MARKET_RESEARCH`: Comprehensive market analysis
- `INDUSTRY_ANALYSIS`: Industry trends and outlook
- `COMPETITIVE_ANALYSIS`: Competitor landscape analysis
- `CONSUMER_INSIGHTS`: Consumer behavior and preferences
- `FINANCIAL_REPORT`: Financial analysis and projections

## API Keys Setup

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account and navigate to API keys
3. Create a new API key
4. Add it to your `.env` file

### Firecrawl API Key
1. Visit [Firecrawl](https://firecrawl.dev/)
2. Sign up for an account
3. Get your API key from the dashboard
4. Add it to your `.env` file

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've activated your virtual environment and installed all dependencies
2. **API Key Errors**: Verify your API keys are correctly set in the `.env` file
3. **Permission Errors**: Ensure you have write permissions in the directory for PDF generation

### Dependencies Issues

If you encounter issues with specific packages, try:

```bash
# Update pip
pip install --upgrade pip

# Install packages individually if needed
pip install openai requests reportlab matplotlib seaborn pandas pillow python-dotenv
```

## Output

The script will generate:
- A comprehensive PDF report with professional formatting
- AI-generated cover and section images
- Data visualizations and charts
- File saved as: `{Report_Title}_{YYYYMMDD}.pdf`

## Advanced Customization

### Custom Branding
- Add your logo to `assets/logo.png`
- Customize colors in the ReportConfig
- Modify PDF styles in the ProfessionalPDFGenerator class

### Additional Data Sources
- Modify the FirecrawlClient to include specific domains
- Add custom research strategies
- Integrate additional APIs for data collection

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please create an issue in the repository or contact the development team. 