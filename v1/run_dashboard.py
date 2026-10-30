"""
Convenience launcher for the Databricks Flight Delay Analytics Dashboard.
Runs: streamlit run v1/src/app.py
"""

import sys
import os
import subprocess
from pathlib import Path

V1_DIR = Path(__file__).resolve().parent
APP_PATH = V1_DIR / "src" / "app.py"

def main():
    print("=" * 70)
    print("Launching US BTS Flight Delay Analytics Dashboard (Databricks Gold)")
    print(f"App Path: {APP_PATH}")
    print("=" * 70)
    
    cmd = [sys.executable, "-m", "streamlit", "run", str(APP_PATH), "--server.headless", "true"]
    try:
        subprocess.run(cmd, cwd=str(V1_DIR.parent))
    except KeyboardInterrupt:
        print("\n[INFO] Dashboard stopped by user.")

if __name__ == "__main__":
    main()
