#!/bin/bash
echo "Installing dependencies..."
pip install fastapi uvicorn numpy requests

echo ""
echo "Starting Nexus-Quant server on http://localhost:8000"
echo "Open your browser and go to: http://localhost:8000"
echo ""
uvicorn main:app --host 0.0.0.0 --port 8000 --reload