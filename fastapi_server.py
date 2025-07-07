#!/usr/bin/env python3
"""
FastAPI Server for AI-Powered Report Generator
Provides REST API endpoints for generating reports in JSON and PDF formats.
"""

import os
import sys
import asyncio
import json
import shutil
from datetime import datetime
from typing import Optional, Dict, Any, cast
from pathlib import Path

# Set matplotlib backend to avoid GUI issues
import matplotlib
matplotlib.use('Agg')

# Suppress gRPC warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*gRPC.*")
warnings.filterwarnings("ignore", message=".*absl.*")

# Set environment variables to suppress gRPC logging
os.environ['GRPC_PYTHON_LOG_LEVEL'] = 'error'
os.environ['ABSL_LOGGING_MIN_LEVEL'] = '1'

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv, find_dotenv

# Import the existing report generation modules
from main_application import ProfessionalReportGenerator
from advanced_content_generator import ReportConfig, ReportType as ContentReportType
from report_planner import ReportPlanner, ReportType
from firecrawl_research import FirecrawlResearch

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Report Generator API",
    description="Generate professional AI-driven research reports in JSON and PDF formats",
    version="2.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ReportRequest(BaseModel):
    prompt: str = Field(..., description="Research topic or prompt for the report")
    template: str = Field(default="template_1", description="Template to use (template_0, template_1, template_2)")
    breadth: int = Field(default=4, description="Research breadth (number of initial queries)")
    depth: int = Field(default=2, description="Research depth (number of follow-up levels)")
    report_type: str = Field(default="market_research", description="Type of report to generate")

class ReportResponse(BaseModel):
    success: bool
    message: str
    report_id: Optional[str] = None
    pdf_path: Optional[str] = None
    json_data: Optional[Dict[str, Any]] = None
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

# Global variables
generator = None
reports_dir = "generated_reports"
json_reports_dir = "json_reports"

# Ensure directories exist
os.makedirs(reports_dir, exist_ok=True)
os.makedirs(json_reports_dir, exist_ok=True)

def get_next_report_number() -> str:
    """Gets the next sequential number for a report file."""
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    existing_files = [f for f in os.listdir(reports_dir) if f.endswith(".pdf")]
    if not existing_files:
        return "001"
    
    nums = [int(f.split('_')[0]) for f in existing_files if f.split('_')[0].isdigit()]
    return f"{max(nums) + 1:03d}" if nums else "001"

def initialize_generator():
    """Initialize the report generator with API keys."""
    global generator
    
    # Reload environment variables
    env_file = find_dotenv()
    if env_file:
        load_dotenv(env_file, override=True)
    
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    generator = ProfessionalReportGenerator(
        gemini_api_key=gemini_api_key
    )
    
    # Reset singleton instances
    ReportPlanner.reset_instance()
    
    return generator

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    try:
        initialize_generator()
        print("✅ FastAPI server initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize server: {e}")
        sys.exit(1)

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="2.1.0",
        timestamp=datetime.now().isoformat()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="2.1.0",
        timestamp=datetime.now().isoformat()
    )

@app.post("/generate-report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """Generate a complete report in both JSON and PDF formats."""
    try:
        if not generator:
            raise HTTPException(status_code=500, detail="Report generator not initialized")
        
        # Get report number and create safe title
        report_num = get_next_report_number()
        report_title_safe = request.prompt[:40].replace(' ', '_').replace(',', '')
        
        # Get company/branding info from environment
        company_name = os.getenv("COMPANY_NAME", "Ubik Enterprise")
        author = os.getenv("AUTHOR", company_name)
        organization = os.getenv("ORGANIZATION", company_name)
        logo_path = os.getenv("COMPANY_LOGO_PATH", "assets/logo.png")
        
        # Map report type string to enum for ReportConfig
        report_type_map = {
            "market_research": ContentReportType.MARKET_RESEARCH,
            "company_analysis": ContentReportType.MARKET_RESEARCH,  # Fallback to market research
            "industry_report": ContentReportType.MARKET_RESEARCH,   # Fallback to market research
            "technical_analysis": ContentReportType.MARKET_RESEARCH  # Fallback to market research
        }
        
        content_report_type = report_type_map.get(request.report_type, ContentReportType.MARKET_RESEARCH)
        
        # Create configuration
        config = ReportConfig(
            title=f"{report_num}_{report_title_safe}",
            subtitle=f"A Strategic Analysis of: {request.prompt}",
            author=author,
            company=organization,
            report_type=content_report_type,
            target_audience="C-suite executives and investors",
            brand_colors={},
            logo_path=logo_path
        )
        
        # Initialize Firecrawl research (always enabled)
        firecrawl_data = None
        if generator.firecrawl_generator:
            try:
                print("🔍 Performing Firecrawl web research...")
                firecrawl_research = FirecrawlResearch(
                    gemini_api_key=os.getenv('GEMINI_API_KEY')
                )
                
                # Perform deep research
                research_result = await firecrawl_research.deep_research(
                    query=request.prompt,
                    breadth=request.breadth,
                    depth=request.depth
                )
                
                # Extract key findings and sources
                source_metadata = research_result.get("source_metadata", [])
                if not isinstance(source_metadata, list):
                    source_metadata = []
                
                firecrawl_data = {
                    "key_findings": research_result.get("learnings", []),
                    "sources": [
                        {
                            "url": source.get("url", ""),
                            "title": source.get("title", ""),
                            "domain": source.get("domain", ""),
                            "reliability_score": source.get("reliability_score", 0.5),
                            "reliability_reasoning": source.get("reliability_reasoning", ""),
                            "content_length": source.get("content_length", 0)
                        }
                        for source in source_metadata
                        if isinstance(source, dict)
                    ],
                    "research_metrics": research_result.get("research_metrics", {}),
                    "credits_used": research_result.get("credits_used", 0),
                    "total_sources": len(source_metadata),
                    "high_quality_sources": len([
                        s for s in source_metadata
                        if isinstance(s, dict) and s.get("reliability_score", 0) >= 0.7
                    ])
                }
                
                key_findings = firecrawl_data.get('key_findings', [])
                total_sources = firecrawl_data.get('total_sources', 0)
                print(f"✅ Firecrawl research completed: {len(key_findings) if isinstance(key_findings, list) else 0} findings from {total_sources} sources")
                
            except Exception as e:
                print(f"⚠️ Firecrawl research failed: {e}")
                firecrawl_data = {
                    "key_findings": [],
                    "sources": [],
                    "research_metrics": {},
                    "credits_used": 0,
                    "total_sources": 0,
                    "high_quality_sources": 0,
                    "error": str(e)
                }
        
        # Generate the report
        result = await generator.generate_comprehensive_report(
            config, 
            request.prompt, 
            12,  # Default page count
            request.template, 
            use_web_research=True
        )
        
        # Extract PDF path and report data from result
        output_file = result.get("pdf_path", "")
        json_data = result.get("report_data", {})
        
        # Add Firecrawl research data to JSON if available
        if firecrawl_data:
            new_json_data = dict(json_data) if isinstance(json_data, dict) else {}
            new_json_data["firecrawl_research"] = firecrawl_data  # type: ignore
            json_data = new_json_data
        
        # Save JSON data to reports directory
        json_filename = f"{report_num}_{report_title_safe}.json"
        json_output_path = os.path.join(json_reports_dir, json_filename)
        
        if json_data:
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return ReportResponse(
            success=True,
            message="Report generated successfully",
            report_id=f"{report_num}_{report_title_safe}",
            pdf_path=output_file,
            json_data=json_data,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@app.post("/generate-json", response_model=ReportResponse)
async def generate_json_only(request: ReportRequest):
    """Generate only the JSON report data without creating a PDF."""
    try:
        if not generator:
            raise HTTPException(status_code=500, detail="Report generator not initialized")
        
        # Get report number and create safe title
        report_num = get_next_report_number()
        report_title_safe = request.prompt[:40].replace(' ', '_').replace(',', '')
        
        # Get company/branding info from environment
        company_name = os.getenv("COMPANY_NAME", "Ubik Enterprise")
        author = os.getenv("AUTHOR", company_name)
        organization = os.getenv("ORGANIZATION", company_name)
        logo_path = os.getenv("COMPANY_LOGO_PATH", "assets/logo.png")
        
        # Map report type string to enum for ReportConfig
        report_type_map = {
            "market_research": ContentReportType.MARKET_RESEARCH,
            "company_analysis": ContentReportType.MARKET_RESEARCH,  # Fallback to market research
            "industry_report": ContentReportType.MARKET_RESEARCH,   # Fallback to market research
            "technical_analysis": ContentReportType.MARKET_RESEARCH  # Fallback to market research
        }
        
        content_report_type = report_type_map.get(request.report_type, ContentReportType.MARKET_RESEARCH)
        
        # Create configuration
        config = ReportConfig(
            title=f"{report_num}_{report_title_safe}",
            subtitle=f"A Strategic Analysis of: {request.prompt}",
            author=author,
            company=organization,
            report_type=content_report_type,
            target_audience="C-suite executives and investors",
            brand_colors={},
            logo_path=logo_path
        )
        
        # Initialize Firecrawl research (always enabled)
        firecrawl_data = None
        if generator.firecrawl_generator:
            try:
                print("🔍 Performing Firecrawl web research for JSON report...")
                firecrawl_research = FirecrawlResearch(
                    gemini_api_key=os.getenv('GEMINI_API_KEY')
                )
                
                # Perform deep research
                research_result = await firecrawl_research.deep_research(
                    query=request.prompt,
                    breadth=request.breadth,
                    depth=request.depth
                )
                
                # Extract key findings and sources
                source_metadata = research_result.get("source_metadata", [])
                if not isinstance(source_metadata, list):
                    source_metadata = []
                
                firecrawl_data = {
                    "key_findings": research_result.get("learnings", []),
                    "sources": [
                        {
                            "url": source.get("url", ""),
                            "title": source.get("title", ""),
                            "domain": source.get("domain", ""),
                            "reliability_score": source.get("reliability_score", 0.5),
                            "reliability_reasoning": source.get("reliability_reasoning", ""),
                            "content_length": source.get("content_length", 0)
                        }
                        for source in source_metadata
                        if isinstance(source, dict)
                    ],
                    "research_metrics": research_result.get("research_metrics", {}),
                    "credits_used": research_result.get("credits_used", 0),
                    "total_sources": len(source_metadata),
                    "high_quality_sources": len([
                        s for s in source_metadata
                        if isinstance(s, dict) and s.get("reliability_score", 0) >= 0.7
                    ])
                }
                
                key_findings = firecrawl_data.get('key_findings', [])
                total_sources = firecrawl_data.get('total_sources', 0)
                print(f"✅ Firecrawl research completed: {len(key_findings) if isinstance(key_findings, list) else 0} findings from {total_sources} sources")
                
            except Exception as e:
                print(f"⚠️ Firecrawl research failed: {e}")
                firecrawl_data = {
                    "key_findings": [],
                    "sources": [],
                    "research_metrics": {},
                    "credits_used": 0,
                    "total_sources": 0,
                    "high_quality_sources": 0,
                    "error": str(e)
                }
        
        # Generate report blueprint only (without PDF)
        report_blueprint = await generator.report_planner.generate_report_blueprint(
            request.prompt, 
            8,  # Default page count
            ReportType.MARKET_RESEARCH
        )
        
        if not report_blueprint:
            raise HTTPException(status_code=500, detail="Failed to generate report blueprint")
        
        # Prepare JSON data
        json_data = {
            "title": config.title,
            "subtitle": config.subtitle,
            "author": config.author,
            "company": config.company,
            "logo_path": config.logo_path,
            "date": datetime.now().strftime('%B %d, %Y'),
            "sections": report_blueprint.get("sections", [])
        }
        
        # Add Firecrawl research data to JSON if available
        if firecrawl_data:
            new_json_data = dict(json_data) if isinstance(json_data, dict) else {}
            new_json_data["firecrawl_research"] = firecrawl_data  # type: ignore
            json_data = new_json_data
        
        # Save JSON data to reports directory
        json_filename = f"{report_num}_{report_title_safe}.json"
        json_output_path = os.path.join(json_reports_dir, json_filename)
        
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return ReportResponse(
            success=True,
            message="JSON report generated successfully",
            report_id=f"{report_num}_{report_title_safe}",
            pdf_path=None,
            json_data=json_data,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate JSON report: {str(e)}")

@app.get("/download-pdf/{report_id}")
async def download_pdf(report_id: str):
    """Download a generated PDF report by report ID."""
    try:
        # Look for the PDF file in the reports directory
        pdf_files = [f for f in os.listdir(reports_dir) if f.startswith(report_id) and f.endswith('.pdf')]
        
        if not pdf_files:
            raise HTTPException(status_code=404, detail="PDF report not found")
        
        pdf_path = os.path.join(reports_dir, pdf_files[0])
        
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        return FileResponse(
            path=pdf_path,
            filename=pdf_files[0],
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download PDF: {str(e)}")

@app.get("/download-json/{report_id}")
async def download_json(report_id: str):
    """Download a generated JSON report by report ID."""
    try:
        # Look for the JSON file in the json_reports directory
        json_files = [f for f in os.listdir(json_reports_dir) if f.startswith(report_id) and f.endswith('.json')]
        
        if not json_files:
            raise HTTPException(status_code=404, detail="JSON report not found")
        
        json_path = os.path.join(json_reports_dir, json_files[0])
        
        if not os.path.exists(json_path):
            raise HTTPException(status_code=404, detail="JSON file not found")
        
        return FileResponse(
            path=json_path,
            filename=json_files[0],
            media_type='application/json'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download JSON: {str(e)}")

@app.get("/reports")
async def list_reports():
    """List all generated reports."""
    try:
        pdf_reports = []
        json_reports = []
        
        # List PDF reports
        if os.path.exists(reports_dir):
            for file in os.listdir(reports_dir):
                if file.endswith('.pdf'):
                    file_path = os.path.join(reports_dir, file)
                    stat = os.stat(file_path)
                    pdf_reports.append({
                        "filename": file,
                        "report_id": file.replace('.pdf', ''),
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
        
        # List JSON reports
        if os.path.exists(json_reports_dir):
            for file in os.listdir(json_reports_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(json_reports_dir, file)
                    stat = os.stat(file_path)
                    json_reports.append({
                        "filename": file,
                        "report_id": file.replace('.json', ''),
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
        
        return {
            "pdf_reports": sorted(pdf_reports, key=lambda x: x["created"], reverse=True),
            "json_reports": sorted(json_reports, key=lambda x: x["created"], reverse=True)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")

@app.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    """Delete a report by ID (both PDF and JSON if they exist)."""
    try:
        deleted_files = []
        
        # Delete PDF file
        pdf_files = [f for f in os.listdir(reports_dir) if f.startswith(report_id) and f.endswith('.pdf')]
        for pdf_file in pdf_files:
            pdf_path = os.path.join(reports_dir, pdf_file)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                deleted_files.append(f"PDF: {pdf_file}")
        
        # Delete JSON file
        json_files = [f for f in os.listdir(json_reports_dir) if f.startswith(report_id) and f.endswith('.json')]
        for json_file in json_files:
            json_path = os.path.join(json_reports_dir, json_file)
            if os.path.exists(json_path):
                os.remove(json_path)
                deleted_files.append(f"JSON: {json_file}")
        
        if not deleted_files:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "success": True,
            "message": f"Deleted {len(deleted_files)} file(s)",
            "deleted_files": deleted_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("FASTAPI_PORT", 8000))
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    
    print(f"🚀 Starting FastAPI server on {host}:{port}")
    print("📚 API Documentation available at:")
    print(f"   - Swagger UI: http://{host}:{port}/docs")
    print(f"   - ReDoc: http://{host}:{port}/redoc")
    
    uvicorn.run(
        "fastapi_server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    ) 