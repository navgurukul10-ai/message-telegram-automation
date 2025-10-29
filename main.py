"""
Main Entry Point - Standardized Structure
Clean entry point for running the application
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

# Import and run
if __name__ == "__main__":
    from scripts.main import main
    import asyncio
    asyncio.run(main())

