#!/bin/bash

# Customer Support Helper Setup Script

echo "======================================"
echo "Customer Support Helper Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

version_compare() {
    # Returns 0 if $1 >= $2
    [ "$(printf '%s\n' "$REQUIRED_VERSION" "$1" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]
}

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python >= $REQUIRED_VERSION to continue."
    exit 1
fi

if ! version_compare $PYTHON_VERSION; then
    echo "Error: Python version $PYTHON_VERSION is installed."
    echo "The OpenAI library requires Python >= $REQUIRED_VERSION"
    echo "Please upgrade your Python installation."
    exit 1
fi

echo "Python $PYTHON_VERSION detected (>= $REQUIRED_VERSION required)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "Virtual environment created"
fi
echo ""

# Install requirements
echo "Installing requirements..."
venv/bin/pip install --upgrade pip > /dev/null 2>&1
venv/bin/pip install -r requirements.txt
echo "Requirements installed"
echo ""

# Create .env file
echo "Setting up environment variables..."
if [ -f ".env" ]; then
    echo "Note: .env file already exists. Skipping creation."
else
    cp .env.example .env
    echo ".env file created from .env.example"
fi
echo ""

# Final instructions
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Update .env with your API key"
echo "   Edit .env and replace 'your_api_key_here'"
echo ""
echo "2. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run a query:"
echo "   python3 src/run_query.py --query=\"Your question here\""
echo ""
echo "======================================"