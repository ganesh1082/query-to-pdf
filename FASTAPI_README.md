# FastAPI Report Generator

This FastAPI server provides REST API endpoints for generating professional AI-driven research reports in both JSON and PDF formats.

## Features

- **JSON Report Generation**: Generate structured report data in JSON format
- **PDF Report Generation**: Generate complete PDF reports with charts and visualizations
- **File Downloads**: Download generated reports via API endpoints
- **Report Management**: List and manage all generated reports
- **Multiple Templates**: Support for different report templates
- **Web Research Integration**: Optional web research using Firecrawl
- **Firecrawl JSON Data**: Key findings and sources included in JSON output
- **Health Monitoring**: Health check endpoints

## Quick Start

### 1. Install Dependencies

```bash
# Install FastAPI dependencies
pip install fastapi uvicorn[standard]

# Or use the provided script
python run_fastapi.py
```

### 2. Set Environment Variables

Create a `.env` file with your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here  # Optional
COMPANY_NAME=Your Company Name
AUTHOR=Your Name
ORGANIZATION=Your Organization
COMPANY_LOGO_PATH=assets/logo.png
```

### 3. Start the Server

```bash
# Run the FastAPI server
python fastapi_server.py

# Or use the provided script
python run_fastapi.py
```

The server will start on `http://localhost:8000`

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

```http
GET /health
```

Returns server health status.

### Generate JSON Report

```http
POST /generate-json
```

Generate only the JSON report data without creating a PDF.

**Request Body:**

```json
{
  "prompt": "Tesla electric vehicle market analysis",
  "template": "template_1",
  "web_research": false,
  "breadth": 4,
  "depth": 2,
  "page_count": 8,
  "report_type": "market_research"
}
```

**Response:**

```json
{
  "success": true,
  "message": "JSON report generated successfully",
  "report_id": "001_Tesla_electric_vehicle_market_analysis",
  "pdf_path": null,
  "json_data": { ... },
  "timestamp": "2024-01-15T10:30:00"
}
```

### Generate Full Report (JSON + PDF)

```http
POST /generate-report
```

Generate a complete report in both JSON and PDF formats.

**Request Body:** Same as JSON generation endpoint.

**Response:**

```json
{
  "success": true,
  "message": "Report generated successfully",
  "report_id": "001_Tesla_electric_vehicle_market_analysis",
  "pdf_path": "generated_reports/001_Tesla_electric_vehicle_market_analysis.pdf",
  "json_data": { ... },
  "timestamp": "2024-01-15T10:30:00"
}
```

### Download PDF

```http
GET /download-pdf/{report_id}
```

Download a generated PDF report by report ID.

### Download JSON

```http
GET /download-json/{report_id}
```

Download a generated JSON report by report ID.

### List Reports

```http
GET /reports
```

List all generated reports (both PDF and JSON).

**Response:**

```json
{
  "pdf_reports": [
    {
      "filename": "001_Tesla_analysis.pdf",
      "report_id": "001_Tesla_analysis",
      "size": 1024000,
      "created": "2024-01-15T10:30:00"
    }
  ],
  "json_reports": [
    {
      "filename": "001_Tesla_analysis.json",
      "report_id": "001_Tesla_analysis",
      "size": 51200,
      "created": "2024-01-15T10:30:00"
    }
  ]
}
```

### Delete Report

```http
DELETE /reports/{report_id}
```

Delete a report by ID (both PDF and JSON if they exist).

## Request Parameters

### ReportRequest Model

| Parameter      | Type    | Default             | Description                                          |
| -------------- | ------- | ------------------- | ---------------------------------------------------- |
| `prompt`       | string  | **required**        | Research topic or prompt for the report              |
| `template`     | string  | `"template_1"`      | Template to use (template_0, template_1, template_2) |
| `web_research` | boolean | `false`             | Enable web research using Firecrawl                  |
| `breadth`      | integer | `4`                 | Research breadth (number of initial queries)         |
| `depth`        | integer | `2`                 | Research depth (number of follow-up levels)          |
| `page_count`   | integer | `8`                 | Number of pages for the report                       |
| `report_type`  | string  | `"market_research"` | Type of report to generate                           |

### Report Types

- `market_research` - Market research reports
- `company_analysis` - Company analysis reports
- `industry_report` - Industry analysis reports
- `technical_analysis` - Technical analysis reports

## Firecrawl JSON Data

When `web_research` is enabled, the JSON output includes additional Firecrawl research data in the `firecrawl_research` field:

### Firecrawl Research Structure

```json
{
  "firecrawl_research": {
    "key_findings": [
      "Finding 1: Tesla leads the global EV market with 18% market share",
      "Finding 2: Battery technology improvements driving 15% annual growth",
      "Finding 3: Competition intensifying with traditional automakers"
    ],
    "sources": [
      {
        "url": "https://example.com/tesla-analysis",
        "title": "Tesla Market Analysis 2024",
        "domain": "example.com",
        "reliability_score": 0.85,
        "reliability_reasoning": "Reputable financial analysis site",
        "content_length": 5000
      }
    ],
    "research_metrics": {
      "breadth_queries": 4,
      "depth_queries": 2,
      "total_sources": 12,
      "high_quality_sources": 8,
      "average_reliability": 0.78
    },
    "credits_used": 15,
    "total_sources": 12,
    "high_quality_sources": 8
  }
}
```

### Key Features

- **Key Findings**: AI-extracted insights from web research
- **Sources**: Complete list of research sources with reliability scores
- **Research Metrics**: Statistics about the research process
- **Template Compatibility**: PDF rendering remains unchanged (template_1 default)
- **Optional**: Only included when `web_research: true`

## Testing

Run the test script to verify all endpoints:

```bash
python test_fastapi.py
```

This will:

1. Test the health endpoint
2. Generate a JSON report
3. Generate a full report (JSON + PDF)
4. Download the generated files
5. List all reports

### Firecrawl Testing

Test the Firecrawl JSON integration:

```bash
python test_firecrawl_json.py
```

This will:

1. Test JSON generation with Firecrawl research enabled
2. Test full report generation with Firecrawl research
3. Download and verify Firecrawl data in JSON output
4. Display key findings and sources

## File Structure

```
├── fastapi_server.py      # Main FastAPI server
├── run_fastapi.py         # Setup and run script
├── test_fastapi.py        # Test script
├── generated_reports/     # Generated PDF reports
├── json_reports/          # Generated JSON reports
├── templates/             # Typst templates
└── assets/               # Assets (logos, etc.)
```

## Environment Variables

| Variable            | Description                        | Required |
| ------------------- | ---------------------------------- | -------- |
| `GEMINI_API_KEY`    | Google Gemini API key              | Yes      |
| `FIRECRAWL_API_KEY` | Firecrawl API key for web research | No       |
| `COMPANY_NAME`      | Company name for reports           | No       |
| `AUTHOR`            | Author name for reports            | No       |
| `ORGANIZATION`      | Organization name for reports      | No       |
| `COMPANY_LOGO_PATH` | Path to company logo               | No       |
| `FASTAPI_HOST`      | Server host (default: 0.0.0.0)     | No       |
| `FASTAPI_PORT`      | Server port (default: 8000)        | No       |

## Example Usage

### Using curl

```bash
# Generate a JSON report
curl -X POST "http://localhost:8000/generate-json" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Tesla electric vehicle market analysis",
    "template": "template_1",
    "page_count": 6,
    "report_type": "market_research"
  }'

# Generate a full report
curl -X POST "http://localhost:8000/generate-report" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Apple company analysis",
    "template": "template_2",
    "web_research": true,
    "page_count": 8,
    "report_type": "company_analysis"
  }'

# Download a PDF
curl -O "http://localhost:8000/download-pdf/001_Tesla_analysis"
```

### Using Python requests

```python
import requests

# Generate a report
response = requests.post("http://localhost:8000/generate-report", json={
    "prompt": "Tesla electric vehicle market analysis",
    "template": "template_1",
    "page_count": 6
})

if response.status_code == 200:
    result = response.json()
    print(f"Report generated: {result['report_id']}")

    # Download the PDF
    pdf_response = requests.get(f"http://localhost:8000/download-pdf/{result['report_id']}")
    with open(f"{result['report_id']}.pdf", "wb") as f:
        f.write(pdf_response.content)
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `404` - Resource not found
- `500` - Internal server error

Error responses include a `detail` field with error information.

## Production Deployment

For production deployment:

1. Set proper CORS origins in the FastAPI middleware
2. Use a production ASGI server like Gunicorn
3. Set up proper logging
4. Configure environment variables securely
5. Use HTTPS in production

```bash
# Example with Gunicorn
pip install gunicorn
gunicorn fastapi_server:app -w 4 -k uvicorn.workers.UvicornWorker
```
