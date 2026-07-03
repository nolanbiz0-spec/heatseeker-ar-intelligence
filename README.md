# Heatseeker A&R Intelligence MVP

**Find emerging artists 3-6 months before they break out**

Real momentum detection vs fake hype through velocity analysis, authenticity scoring, and cross-platform correlation.

## Quick Start

```bash
# 1. Start infrastructure
docker-compose up -d postgres redis

# 2. Install dependencies  
pip install -r requirements.txt

# 3. Run the API
uvicorn app.main:app --reload
```

**API will be available at:** http://localhost:8000

## Architecture

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL/TimescaleDB
- **Caching:** Redis for API rate limits and response caching
- **APIs:** Spotify, YouTube, Last.fm, MusicBrainz with authenticated clients
- **Analytics:** Velocity engine, authenticity detection, momentum scoring

## Core Features

### 🎯 **Artist Discovery**
- Track 100+ emerging artists across platforms
- Real-time momentum detection with 7/30/90-day velocity windows
- Cross-platform correlation analysis

### 🔍 **Authenticity Detection** 
- Bot farm and fake engagement detection
- Geographic listening pattern analysis
- Engagement ratio validation

### 📊 **Intelligence Reports**
- Daily momentum briefs with top opportunities
- Artist deep-dive reports with commercial scoring
- Independence status and deal timing analysis

### ⚡ **Real-Time API**
- `/api/artists` - Artist management and tracking
- `/api/intelligence` - Daily briefs and scoring reports
- Rate-limited, cached API clients for all platforms

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
# Your API credentials (required)
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_secret  
YOUTUBE_API_KEY=your_api_key
LASTFM_API_KEY=your_api_key
LASTFM_SECRET=your_secret
MUSICBRAINZ_EMAIL=your@email.com

# Database (defaults work with docker-compose)
DATABASE_URL=postgresql+asyncpg://heatseeker:password@localhost:5432/heatseeker
REDIS_URL=redis://localhost:6379/0
```

## Development Timeline

- ✅ **Week 1:** Infrastructure (FastAPI, PostgreSQL, Redis, API clients)
- ⏳ **Week 2:** Analysis engine (velocity, authenticity, scoring)
- ⏳ **Week 3:** Intelligence reports (daily briefs, artist deep-dives)  
- ⏳ **Week 4:** Dashboard (React frontend, charts, watchlists)

## API Endpoints

### Artist Management
- `POST /api/artists` - Add artist to tracking
- `GET /api/artists` - List tracked artists with scores
- `GET /api/artists/{id}` - Artist details and metrics
- `PUT /api/artists/{id}` - Update artist data
- `DELETE /api/artists/{id}` - Remove from tracking

### Intelligence  
- `GET /api/intelligence/daily-brief` - Top momentum artists
- `GET /api/intelligence/artist-report/{id}` - Deep-dive analysis
- `GET /api/intelligence/trending` - Cross-platform trending analysis

Built for A&R professionals at Interscope/UMG. Direct, actionable intelligence without the fluff.# Enhanced A&R Intelligence Platform with full diagnostics and testing capabilities


# Production A&R Intelligence Platform
Deployed at: https://heatseeker-ar-intelligence-production.up.railway.app

 
# Testing live A&R intelligence with real streaming data

