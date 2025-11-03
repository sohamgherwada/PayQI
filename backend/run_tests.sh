#!/bin/bash

# Run Python tests
echo "?? Running Python tests..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "?? Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "?? Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run tests
echo "?? Running pytest..."
pytest tests/ -v --tb=short --color=yes

# Get exit code
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "? All tests passed!"
else
    echo "? Some tests failed"
fi

deactivate
exit $exit_code
