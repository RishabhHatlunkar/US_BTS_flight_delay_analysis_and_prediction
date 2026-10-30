"""
V2 Pipeline Entrypoint Wrapper
Run via: python v2/run_pipeline.py --help
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from v2.src.pipeline.run_pipeline import main

if __name__ == "__main__":
    main()
