# query_to_pdf/typst_renderer.py

import os
import json
import subprocess
from typing import Dict, Any

def render_to_pdf_with_typst(report_data: Dict[str, Any], template_path: str, output_path: str) -> bool:
    """
    Renders a report to PDF using Typst by creating a temporary JSON data file.

    Args:
        report_data (Dict[str, Any]): The dictionary containing all data for the report.
        template_path (str): The path to the .typ template file.
        output_path (str): The desired path for the final PDF.

    Returns:
        bool: True if PDF generation was successful, False otherwise.
    """
    data_json_path = "report_data.json"
    success = False
    
    try:
        # 1. Write the dynamic data to a JSON file that Typst can read.
        with open(data_json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print("  📄 Wrote report data to report_data.json")

        # 2. Construct the Typst compile command.
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        command = [
            "typst",
            "compile",
            template_path,
            output_path
        ]
        
        print(f"  🚀 Executing Typst command: {' '.join(command)}")

        # 3. Run the Typst compiler.
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            print("❌ CRITICAL: Typst compilation failed.")
            print("   [Typst STDERR]:", result.stderr)
            return False

        print("  ✅ Typst compilation successful.")
        if result.stdout:
            print("  [Typst STDOUT]:", result.stdout)
        
        success = True

    except FileNotFoundError:
        print("❌ CRITICAL: 'typst' command not found.")
        print("   Please ensure Typst is installed and in your system's PATH.")
        print("   Installation: https://github.com/typst/typst")
        
    except Exception as e:
        print(f"❌ An unexpected error occurred during PDF rendering: {e}")
        
    finally:
        # 4. Clean up the temporary JSON file.
        if os.path.exists(data_json_path):
            os.remove(data_json_path)
            print("  🗑️ Cleaned up temporary data file.")
    
    return success