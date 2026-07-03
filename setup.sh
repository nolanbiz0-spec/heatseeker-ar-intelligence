#!/bin/bash

# Heatseeker A&R Intelligence Platform Setup Script

echo "🔥 Setting up Heatseeker A&R Intelligence Platform..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install PostgreSQL first."
    echo "On macOS: brew install postgresql"
    echo "On Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# Check if Redis is installed
if ! command -v redis-cli &> /dev/null; then
    echo "Redis is not installed. Please install Redis first."
    echo "On macOS: brew install redis"
    echo "On Ubuntu: sudo apt-get install redis-server"
    exit 1
fi

# Create database if it doesn't exist
echo "Creating database..."
createdb heatseeker_dev 2>/dev/null || echo "Database heatseeker_dev already exists"

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your API keys and database credentials"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Create initial migration if none exist
if [ ! "$(ls -A alembic/versions)" ]; then
    echo "Creating initial migration..."
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API credentials:"
echo "   - Spotify Client ID and Secret (https://developer.spotify.com/)"
echo "   - YouTube API Key (https://console.developers.google.com/)"
echo "   - Last.fm API Key (https://www.last.fm/api/account/create)"
echo ""
echo "2. Start the application:"
echo "   ./run.sh"
echo ""
echo "3. Open http://localhost:8000 in your browser"