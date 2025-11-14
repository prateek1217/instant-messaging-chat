#!/bin/bash

echo "Starting Messaging Application..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Import data
echo ""
echo "Importing customer messages from Excel files..."
python3 import_data.py

# Start server
echo ""
echo "Starting server on http://localhost:5000"
echo "Agent Portal: http://localhost:5000/agent"
echo "Customer Form: http://localhost:5000/customer"
echo ""
python3 app.py

