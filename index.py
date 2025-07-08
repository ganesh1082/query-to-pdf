#!/usr/bin/env python3
"""
AI-Powered Report Generator v2.1 (Typst Edition)
Generates professional AI-driven research reports using Google's Gemini API and Typst for PDF rendering.
Uses FIRECRAWL_API_URL from .env for web research (no API key required).
"""

import os
import sys
import asyncio
import argparse
import traceback
import signal
import atexit
import json
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

# Set matplotlib backend to avoid GUI issues
import matplotlib
matplotlib.use('Agg')

# Suppress gRPC warnings that can cause sys.excepthook errors
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*gRPC.*")
warnings.filterwarnings("ignore", message=".*absl.*")

# Suppress specific gRPC and absl warnings
os.environ['GRPC_PYTHON_LOG_LEVEL'] = 'error'
os.environ['ABSL_LOGGING_MIN_LEVEL'] = '1'

# Force reload environment variables
def reload_environment():
    """Force reload environment variables from .env file"""
    print("🔄 Loading environment variables...")
    
    # Clear any existing environment variables that might be cached
    keys_to_clear = [
        'GEMINI_API_KEY', 'FIRECRAWL_API_KEY', 'OPENAI_API_KEY',
        'FIRECRAWL_RESEARCH_BREADTH', 'FIRECRAWL_RESEARCH_DEPTH',
        'FIRECRAWL_API_URL'
    ]
    
    for key in keys_to_clear:
        if key in os.environ:
            del os.environ[key]
    
    # Reload from .env file
    env_file = find_dotenv()
    if env_file:
        load_dotenv(env_file, override=True)
        print(f"✅ Environment loaded from: {env_file}")
        
        # Debug environment variables
        print("🔍 Environment Debug Info:")
        print(f"   GEMINI_API_KEY: {'✅ Set' if os.getenv('GEMINI_API_KEY') else '❌ Not set'}")
        print(f"   FIRECRAWL_API_URL: {'✅ Set' if os.getenv('FIRECRAWL_API_URL') else '❌ Not set'}")
        if os.getenv('FIRECRAWL_API_URL'):
            print(f"   FIRECRAWL_API_URL value: {os.getenv('FIRECRAWL_API_URL')}")
        print(f"   FIRECRAWL_API_KEY: {'✅ Set' if os.getenv('FIRECRAWL_API_KEY') else '❌ Not set (not needed)'}")
    else:
        print("❌ No .env file found")

# Global cleanup flag
_cleanup_done = False

def cleanup_and_exit(signum=None, frame=None):
    """Cleanup function to handle graceful exit."""
    global _cleanup_done
    if _cleanup_done:
        return
    
    _cleanup_done = True
    print("\n🧹 Cleaning up resources...")
    
    # Suppress stderr during cleanup to prevent gRPC errors
    import contextlib
    import io
    
    with contextlib.redirect_stderr(io.StringIO()):
        # Close any open matplotlib figures
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except:
            pass
        
        # Clear any remaining references
        try:
            import gc
            gc.collect()
        except:
            pass
    
    # Exit cleanly
    sys.exit(0)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Custom exception handler to prevent sys.excepthook errors."""
    if exc_type is KeyboardInterrupt:
        cleanup_and_exit()
        return
    
    # Only print traceback for actual errors, not cleanup-related issues
    if not _cleanup_done:
        print(f"\n❌ Unhandled exception: {exc_type.__name__}: {exc_value}")
        if exc_traceback:
            traceback.print_exception(exc_type, exc_value, exc_traceback)
    
    cleanup_and_exit()

# Register cleanup handlers
atexit.register(cleanup_and_exit)
signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)

# Set custom exception handler
sys.excepthook = handle_exception

# Import after setting up error handling
from main_application import ProfessionalReportGenerator
from advanced_content_generator import ReportConfig, ReportType
from report_planner import ReportPlanner

# Reset singleton instances to ensure fresh initialization
ReportPlanner.reset_instance()

def get_next_report_number() -> str:
    """Gets the next sequential number for a report file."""
    reports_dir = os.getenv("REPORTS_OUTPUT_DIR", "generated_reports")
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    existing_files = [f for f in os.listdir(reports_dir) if f.endswith(".pdf")]
    if not existing_files:
        return "001"
    
    nums = [int(f.split('_')[0]) for f in existing_files if f.split('_')[0].isdigit()]
    return f"{max(nums) + 1:03d}" if nums else "001"

async def main():
    """Main async function"""
    print("🚀 AI-Powered Report Generator v2.1 (Typst Edition)")
    print("=" * 60)
    print("🌐 Using FIRECRAWL_API_URL for web research (no API key required)")
    print("=" * 60)
    
    # Reload environment at startup
    reload_environment()
    
    parser = argparse.ArgumentParser(description="AI-Powered Report Generator")
    parser.add_argument("--prompt", required=True, help="Research topic or prompt")
    
    args = parser.parse_args()
    
    # Get configuration from environment variables
    prompt = args.prompt
    template = os.getenv('REPORT_TEMPLATE', 'template_1')
    web_research = os.getenv('WEB_RESEARCH', 'true').lower() == 'true'
    breadth = int(os.getenv('RESEARCH_BREADTH', '4'))
    depth = int(os.getenv('RESEARCH_DEPTH', '2'))
    
    print("📋 Report Configuration:")
    print(f"   Prompt: {prompt}")
    print(f"   Template: {template}")
    print(f"   Web Research: {'✅ Enabled' if web_research else '❌ Disabled'}")
    if web_research:
        print(f"   Research Breadth: {breadth}")
        print(f"   Research Depth: {depth}")
    print("=" * 60)
    
    # Get API keys
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    firecrawl_api_url = os.getenv('FIRECRAWL_API_URL')
    
    if not gemini_api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables")
        print("   Please set GEMINI_API_KEY in your .env file")
        sys.exit(1)
    
    if web_research and not firecrawl_api_url:
        print("❌ Error: FIRECRAWL_API_URL not found in environment variables")
        print("   Please set FIRECRAWL_API_URL in your .env file for web research")
        sys.exit(1)
    
    # Debug API key info
    print("🔑 API Configuration:")
    print(f"   GEMINI_API_KEY: {gemini_api_key[:10]}...{gemini_api_key[-5:]} ✅")
    if firecrawl_api_url:
        print(f"   FIRECRAWL_API_URL: {firecrawl_api_url} ✅")
    else:
        print(f"   FIRECRAWL_API_URL: Not set - web research disabled")
    
    # Get company/branding info from .env
    company_name = os.getenv("COMPANY_NAME", "Ubik Enterprise")
    author = os.getenv("AUTHOR", company_name)
    organization = os.getenv("ORGANIZATION", company_name)
    logo_path = os.getenv("COMPANY_LOGO_PATH", "assets/logo.png")
    
    report_num = get_next_report_number()
    report_title_safe = prompt[:40].replace(' ', '_').replace(',', '')
    
    print("📄 Report Details:")
    print(f"   Report Number: {report_num}")
    print(f"   Company: {company_name}")
    print(f"   Author: {author}")
    print(f"   Logo Path: {logo_path}")
    
    # Create configuration
    config = ReportConfig(
        title=f"{report_num}_{report_title_safe}",
        subtitle=f"A Strategic Analysis of: {prompt}",
        author=author,
        company=organization,
        report_type=ReportType.MARKET_RESEARCH,
        target_audience="C-suite executives and investors",
        brand_colors={},  # Remove brand colors - will use template colors
        logo_path=logo_path
    )
    
    try:
        print("\n🔧 Initializing report generator...")
        generator = ProfessionalReportGenerator(gemini_api_key=gemini_api_key)
        
        print("🎯 Starting report generation...")
        result = await generator.generate_comprehensive_report(
            config, 
            prompt, 
            8, 
            template, 
            use_web_research=web_research
        )
        
        output_file = result.get("pdf_path", "")
        report_data = result.get("report_data", {})
        
        # Save JSON report
        json_reports_dir = os.getenv("JSON_REPORTS_OUTPUT_DIR", "json_reports")
        os.makedirs(json_reports_dir, exist_ok=True)
        json_filename = f"{report_num}_{report_title_safe}.json"
        json_output_path = os.path.join(json_reports_dir, json_filename)
        
        if report_data:
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"📄 JSON Report: {json_output_path}")
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Professional reports generated successfully!")
        print(f"📁 PDF File: {output_file}")
        print(f"📄 JSON File: {json_output_path}")
        
        # Show additional info if available
        if "requests_used" in result:
            print(f"🌐 Web Research: {result.get('requests_used', 0)} requests used")
        if "learnings_count" in result:
            print(f"📚 Learnings: {result.get('learnings_count', 0)} found")
        if "sources_count" in result:
            print(f"🔗 Sources: {result.get('sources_count', 0)} found")
        
        print("=" * 60)
        
        # Cleanup and exit gracefully
        cleanup_and_exit()
        
    except Exception as e:
        print(f"\n❌ Report generation failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        sys.exit(1)

def run_main():
    """Wrapper to run the async main function."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        cleanup_and_exit()
    except Exception as e:
        print(f"\n❌ Fatal error in main execution: {e}")
        traceback.print_exc()
        cleanup_and_exit()
    finally:
        # Ensure cleanup happens even if there are unhandled exceptions
        if not _cleanup_done:
            cleanup_and_exit()

if __name__ == "__main__":
    # Suppress gRPC warnings at the very beginning
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", message=".*gRPC.*")
    warnings.filterwarnings("ignore", message=".*absl.*")
    
    # Set environment variables to suppress gRPC logging
    os.environ['GRPC_PYTHON_LOG_LEVEL'] = 'error'
    os.environ['ABSL_LOGGING_MIN_LEVEL'] = '1'
    
    # Completely suppress the sys.excepthook error
    original_excepthook = sys.excepthook
    
    def silent_excepthook(exc_type, exc_value, exc_traceback):
        """Silent exception hook to prevent gRPC errors from appearing."""
        if exc_type is KeyboardInterrupt:
            cleanup_and_exit()
            return
        
        # Only show actual errors, not cleanup-related gRPC warnings
        if not _cleanup_done and exc_type is not None:
            # Check if this is a gRPC-related error
            error_str = str(exc_value).lower()
            if any(keyword in error_str for keyword in ['grpc', 'absl', 'fork_posix', 'sys.excepthook']):
                # Silently ignore gRPC-related errors and sys.excepthook errors
                return
            
            # Show other errors normally
            print(f"\n❌ Unhandled exception: {exc_type.__name__}: {exc_value}")
            if exc_traceback:
                traceback.print_exception(exc_type, exc_value, exc_traceback)
        
        cleanup_and_exit()
    
    sys.excepthook = silent_excepthook
    
    try:
        run_main()
    except SystemExit:
        # Normal exit, do nothing
        pass
    except Exception as e:
        # Any other exception
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        # Restore original excepthook
        sys.excepthook = original_excepthook