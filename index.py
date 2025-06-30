# query-to-pdf/index.py

import os
import asyncio
import argparse
from dotenv import load_dotenv
from main_application import ProfessionalReportGenerator
from advanced_content_generator import ReportConfig, ReportType

def get_next_report_number() -> str:
    """Gets the next sequential number for a report file."""
    reports_dir = "generated_reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    existing_files = [f for f in os.listdir(reports_dir) if f.endswith(".pdf")]
    if not existing_files:
        return "001"
    
    nums = [int(f.split('_')[0]) for f in existing_files if f.split('_')[0].isdigit()]
    return f"{max(nums) + 1:03d}" if nums else "001"

async def main():
    """Main function with command-line arguments for report generation."""
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Generate a professional AI-driven research report using Typst.")
    parser.add_argument(
        "--prompt",
        type=str,
        default="A deep dive into the global coffee bean supply chain",
        help="The central research topic for the report."
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=12,
        help="The approximate target number of pages for the report."
    )
    parser.add_argument(
        "--template",
        type=str,
        default="template_1",
        choices=["template_1", "template_2"],
        help="The template to use for the report layout (template_1: single column, template_2: two column)."
    )
    args = parser.parse_args()
    
    print("🚀 AI-Powered Report Generator v2.1 (Typst Edition)")
    print("======================================================")
    print(f"  Prompt: {args.prompt}")
    print(f"  Target Pages: ~{args.pages}")
    print(f"  Template: {args.template}")
    print("======================================================")
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("❌ FATAL: GEMINI_API_KEY not found in the .env file. Please add it.")
        return

    report_num = get_next_report_number()
    report_title_safe = args.prompt[:40].replace(' ', '_').replace(',', '')
    
    config = ReportConfig(
        title=f"{report_num}_{report_title_safe}",
        subtitle=f"A Strategic Analysis of: {args.prompt}",
        author="Ubik Enterprise",
        company="Ubik Enterprise",
        report_type=ReportType.MARKET_RESEARCH,
        target_audience="C-suite executives and investors",
        brand_colors={"primary": "#0D203D", "accent": "#4A90E2"},
        logo_path="assets/logo.png" # Optional: place your logo here
    )
    
    try:
        generator = ProfessionalReportGenerator(gemini_api_key=gemini_api_key)
        output_file = await generator.generate_comprehensive_report(config, args.prompt, args.pages, args.template)
        
        print("\n" + "=" * 54)
        print("🎉 SUCCESS! Professional PDF report generated successfully!")
        print(f"📁 Output File: {output_file}")
        print("=" * 54)

    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

def run_main():
    """Wrapper to run the async main function."""
    asyncio.run(main())

if __name__ == "__main__":
    run_main()