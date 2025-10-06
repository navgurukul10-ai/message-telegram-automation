#!/bin/bash

# Telegram Job Fetcher - Setup Script

echo "================================"
echo "Telegram Job Fetcher - Setup"
echo "================================"

# Create directories
echo "Creating directory structure..."
mkdir -p data/csv data/json data/database logs sessions

# Create .gitkeep files
touch data/csv/.gitkeep
touch data/json/.gitkeep
touch data/database/.gitkeep
touch logs/.gitkeep
touch sessions/.gitkeep

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete! ✅"
echo ""
echo "Next steps:"
echo "1. Verify your accounts in config.py"
echo "2. Run: python main.py --auth (to authorize accounts)"
echo "3. Run: python main.py (to start fetching)"
echo ""
echo "Check README.md for detailed instructions."
echo "================================"

