#!/bin/bash

# Heatseeker A&R Intelligence Platform Run Script

echo "🔥 Starting Heatseeker A&R Intelligence Platform..."

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run ./setup.sh first"
    exit 1
fi

# Start Redis if not running
if ! pgrep redis-server > /dev/null; then
    echo "Starting Redis server..."
    redis-server --daemonize yes
fi

# Start PostgreSQL if not running (on macOS)
if command -v brew &> /dev/null; then
    if ! pgrep postgres > /dev/null; then
        echo "Starting PostgreSQL..."
        brew services start postgresql
    fi
fi

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the FastAPI application
echo "Starting Heatseeker web application..."
echo "Dashboard will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the application"

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload