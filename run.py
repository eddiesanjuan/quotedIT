#!/usr/bin/env python3
"""
Run the Quoted application.
"""

import os
import sys

# Add the project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn


def main():
    """Run the Quoted server."""
    print("Starting Quoted - Voice to Quote for Contractors")
    print("=" * 50)
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("Frontend: Open frontend/index.html in your browser")
    print("=" * 50)

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
