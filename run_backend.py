#!/usr/bin/env python3
"""
Run script for the LLM Assistant Bot backend
"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    import uvicorn

    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"

    print(f"Starting LLM Assistant Bot backend on {host}:{port}")
    print(f"Debug mode: {debug}")

    uvicorn.run("main:app", host=host, port=port, reload=debug, log_level="info")
