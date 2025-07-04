#!/usr/bin/env python3
"""
AI-Powered Report Generator v2.1 (Typst Edition)
Generates professional AI-driven research reports using Google's Gemini API and Typst for PDF rendering.
"""

import os
import sys
import asyncio
import argparse
import traceback
import signal
import atexit
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
    # Clear any existing environment variables that might be cached
    keys_to_clear = [
        'GEMINI_API_KEY', 'FIRECRAWL_API_KEY', 'OPENAI_API_KEY',
        'FIRECRAWL_RESEARCH_BREADTH', 'FIRECRAWL_RESEARCH_DEPTH'
    ]
    
    for key in keys_to_clear:
        if key in os.environ:
            del os.environ[key]
    
    # Reload from .env file
    env_file = find_dotenv()
    if env_file:
        load_dotenv(env_file, override=True)
        print(f"🔄 Environment reloaded from: {env_file}")

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
    # Reload environment at startup
    reload_environment()
    
    parser = argparse.ArgumentParser(description="AI-Powered Report Generator")
    parser.add_argument("--prompt", required=True, help="Research topic or prompt")
    parser.add_argument("--template", default="template_1", help="Template to use (template_0, template_1, template_2)")
    parser.add_argument("--web-research", action="store_true", help="Enable web research using Firecrawl")
    parser.add_argument("--breadth", type=int, default=4, help="Research breadth (number of initial queries)")
    parser.add_argument("--depth", type=int, default=2, help="Research depth (number of follow-up levels)")
    
    args = parser.parse_args()
    
    print("🚀 AI-Powered Report Generator v2.1 (Typst Edition)")
    print("=" * 54)
    print(f"  Prompt: {args.prompt}")
    print(f"  Template: {args.template}")
    print(f"  Web Research: {'Yes' if args.web_research else 'No'}")
    print("=" * 54)
    
    # Get API keys
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
    
    if not gemini_api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables")
        sys.exit(1)
    
    if args.web_research and not firecrawl_api_key:
        print("❌ Error: FIRECRAWL_API_KEY not found in environment variables")
        sys.exit(1)
    
    # Debug API key info
    print("🔑 API Key Debug Info:")
    print(f"  GEMINI_API_KEY: {gemini_api_key[:10]}...{gemini_api_key[-5:]} ✅")
    if firecrawl_api_key:
        print(f"  FIRECRAWL_API_KEY: {firecrawl_api_key[:10]}...{firecrawl_api_key[-5:]} ✅")
    
    # Get company/branding info from .env
    company_name = os.getenv("COMPANY_NAME", "Ubik Enterprise")
    author = os.getenv("AUTHOR", company_name)
    organization = os.getenv("ORGANIZATION", company_name)
    logo_path = os.getenv("COMPANY_LOGO_PATH", "assets/logo.png")
    
    report_num = get_next_report_number()
    report_title_safe = args.prompt[:40].replace(' ', '_').replace(',', '')
    
    # Create configuration
    config = ReportConfig(
        title=f"{report_num}_{report_title_safe}",
        subtitle=f"A Strategic Analysis of: {args.prompt}",
        author=author,
        company=organization,
        report_type=ReportType.MARKET_RESEARCH,
        target_audience="C-suite executives and investors",
        brand_colors={},  # Remove brand colors - will use template colors
        logo_path=logo_path
    )
    
    try:
        generator = ProfessionalReportGenerator(gemini_api_key=gemini_api_key, firecrawl_api_key=firecrawl_api_key)
        output_file = await generator.generate_comprehensive_report(config, args.prompt, 8, args.template, use_web_research=args.web_research)
        
        print("\n" + "=" * 54)
        print("🎉 SUCCESS! Professional PDF report generated successfully!")
        print(f"📁 Output File: {output_file}")
        print("=" * 54)
        
        # Cleanup and exit gracefully
        cleanup_and_exit()

    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("🔍 Error details:")
        traceback.print_exc()
        cleanup_and_exit()

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
            if any(keyword in error_str for keyword in ['grpc', 'absl', 'fork_posix']):
                # Silently ignore gRPC-related errors
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