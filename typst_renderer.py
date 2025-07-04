#!/usr/bin/env python3
"""
Typst PDF Renderer for AI-Powered Report Generator
Handles PDF generation using Typst with enhanced error handling.
"""

import os
import json
import subprocess
import sys
import warnings
from typing import Dict, Any, Optional
from pathlib import Path

# Suppress gRPC and absl warnings that cause sys.excepthook errors
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*gRPC.*")
warnings.filterwarnings("ignore", message=".*absl.*")

# Set environment variables to suppress gRPC logging
os.environ['GRPC_PYTHON_LOG_LEVEL'] = 'error'
os.environ['ABSL_LOGGING_MIN_LEVEL'] = '1'

def render_to_pdf_with_typst(report_data: Dict[str, Any], template_path: str, output_path: str) -> bool:
    """
    Render a report to PDF using Typst with enhanced error handling.
    
    Args:
        report_data: Dictionary containing report data
        template_path: Path to the Typst template file
        output_path: Path where the PDF should be saved
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Write report data to JSON file for Typst
        data_file = os.path.join(os.path.dirname(template_path), "report_data.json")
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"  📄 Wrote report data to {data_file}")
        
        # Get template directory and project root
        template_dir = os.path.dirname(template_path)
        project_root = os.path.abspath(os.path.join(template_dir, ".."))
        
        print(f"  🔍 Debug: template_dir={template_dir}, project_root={project_root}")
        
        # Prepare Typst command with enhanced error handling
        cmd = [
            "typst", "compile",
            "--root", project_root,
            template_path,
            output_path
        ]
        
        print(f"  🚀 Executing Typst command: {' '.join(cmd)}")
        
        # Execute Typst with proper error handling
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=project_root,
            env={**os.environ, 'GRPC_PYTHON_LOG_LEVEL': 'error', 'ABSL_LOGGING_MIN_LEVEL': '1'}
        )
        
        # Check if compilation was successful
        if result.returncode == 0:
            print("  ✅ Typst compilation successful.")
            
            # Clean up temporary data file
            try:
                os.remove(data_file)
                print("  🗑️ Cleaned up temporary data file.")
            except Exception as cleanup_error:
                print(f"  ⚠️ Warning: Could not clean up temporary file: {cleanup_error}")
            
            return True
        else:
            print(f"  ❌ Typst compilation failed with return code {result.returncode}")
            print(f"  🔍 Error output: {result.stderr}")
            print(f"  🔍 Standard output: {result.stdout}")
            
            # Clean up temporary data file even on failure
            try:
                os.remove(data_file)
            except:
                pass
            
            return False
            
    except FileNotFoundError:
        print("  ❌ Error: Typst not found. Please install Typst first.")
        print("  📝 Installation: https://typst.app/docs/getting-started/installation")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error during PDF generation: {e}")
        
        # Clean up temporary data file
        try:
            if 'data_file' in locals():
                os.remove(data_file)
        except:
            pass
        
        return False

def validate_typst_installation() -> bool:
    """
    Validate that Typst is properly installed and accessible.
    
    Returns:
        bool: True if Typst is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["typst", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"  ✅ Typst version: {result.stdout.strip()}")
            return True
        else:
            print(f"  ❌ Typst version check failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("  ❌ Typst not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("  ❌ Typst version check timed out")
        return False
    except Exception as e:
        print(f"  ❌ Error checking Typst installation: {e}")
        return False