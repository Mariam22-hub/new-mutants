"""
PLEASE READ THIS FILE CAREFULLY BEFORE USING IT.

the UIUCPlus repo main branch needs to be formatted before using this:

find ~/UIUCPlus -name "*.java" -print0 | xargs -0 ./new-mutants/google-java-format_linux-x86-64 -i

and have a formatted main branch pushed to the repo.

This will avoid diff issues when comparing mutants.
"""
import os
import re
import subprocess
import requests
from typing import List, Tuple
from pathlib import Path

# Google Java Format download URL and local path
GJF_URL = "https://github.com/google/google-java-format/releases/download/v1.26.0/google-java-format_linux-x86-64"
GJF_PATH = Path(os.path.dirname(os.path.abspath(__file__))) / "google-java-format_linux-x86-64"

def download_google_java_format():
    """Download the Google Java Format tool if not already present."""
    if not GJF_PATH.exists():
        print("Downloading Google Java Format...")
        try:
            response = requests.get(GJF_URL, stream=True)
            response.raise_for_status()
            
            with open(GJF_PATH, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Make the file executable
            GJF_PATH.chmod(0o755)
            print(f"Google Java Format downloaded to {GJF_PATH}")
            return True
        except Exception as e:
            print(f"Failed to download Google Java Format: {str(e)}")
            return False
    return True

def format_java_code(code: str) -> str:
    """
    Format Java code using Google Java Format.
    
    If Google Java Format cannot be used, the original code is returned.
    
    Args:
        code: Java code to format
        
    Returns:
        Formatted Java code
    """
    # Make sure Google Java Format is available
    if not GJF_PATH.exists() and not download_google_java_format():
        print("Warning: Google Java Format not available. Returning original code.")
        return code
    
    try:
        # Create a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.java', mode='w+') as tmp:
            tmp.write(code)
            tmp.flush()
            
            # Run Google Java Format
            result = subprocess.run(
                [str(GJF_PATH), tmp.name],
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"Warning: Google Java Format failed: {result.stderr}")
                return ""
    except Exception as e:
        print(f"Error formatting code: {str(e)}")
        return code

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python format_mutants.py <java_file_path>")
        sys.exit(1)
    
    java_file_path = sys.argv[1]
    
    with open(java_file_path, 'r') as f:
        raw_code = f.read()
        
    formatted_code = format_java_code(raw_code)
    
    with open(java_file_path, 'w') as f:
        f.write(formatted_code)
        
    print(f"Formatted code written to {java_file_path}")
