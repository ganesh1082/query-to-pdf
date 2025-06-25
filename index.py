# query-to-pdf copy/index.py

import os
import re
import asyncio
import argparse
from dotenv import load_dotenv

from main_application import ProfessionalReportGenerator
from advanced_content_generator import ReportConfig, ReportType

def get_next_report_number() -> str:
    # This function remains the same
    reports_dir = "generated_reports"
    if not os.path.exists(reports_dir): os.makedirs(reports_dir)
    existing = [f for f in os.listdir(reports_dir) if f.endswith(".pdf")]
    if not existing: return "000"
    nums = [int(f.split('_')[0]) for f in existing if f.split('_')[0].isdigit()]
    return f"{max(nums) + 1:03d}" if nums else "000"

async def main():
    """Main function with command-line arguments for customization."""
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Generate a professional AI-driven research report.")
    parser.add_argument("--prompt", type=str, default="Analyze market trends for AI in the renewable energy sector.",
                        help="The research topic for the report.")
    parser.add_argument("--pages", type=int, default=10,
                        help="The approximate number of pages for the report.")
    args = parser.parse_args()
    
    print("🚀 AI-Driven Report Generator v10.0 (Customizable)")
    print("======================================================")
    print(f"  Prompt: {args.prompt}")
    print(f"  Target Pages: {args.pages}")
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("❌ FATAL: GEMINI_API_KEY not found in .env file.")
        return

    report_num = get_next_report_number()
    config = ReportConfig(
        title=f"{report_num}_AI_Report_{args.prompt[:20].replace(' ', '_')}",
        subtitle=f"Dynamic Analysis based on: {args.prompt}",
        author="Gemini-Powered Analyst",
        company="Ubik Research",
        report_type=ReportType.MARKET_RESEARCH,
        target_audience="C-suite executives and investors",
        brand_colors={"primary": "#1a365d", "accent": "#3182ce"},
        logo_path=""
    )
    
    try:
        generator = ProfessionalReportGenerator(gemini_api_key=gemini_api_key)
        output_file = await generator.generate_comprehensive_report(config, args.prompt, args.pages)
        
        print("\n" + "=" * 50)
        print("🎉 SUCCESS! Dynamically generated PDF created successfully!")
        print(f"📁 Output File: {output_file}")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())