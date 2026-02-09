#!/bin/bash

echo "================================================"
echo "  JITU - Jaringan Informasi Transaksi UMKM"
echo "  Data to Duit"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"
echo ""

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo "Dependencies installed."
echo ""

# Run the application
echo "Starting JITU application..."
echo "Open your browser to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo "================================================"
echo ""

streamlit run app.py
