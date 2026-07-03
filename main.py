from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List, Optional
import logging

from app.core.config import settings
from app.core.database import get_db, engine, Base
from app.models.models import Artist, DailyScore, IntelligenceReport
from app.collectors.spotify_collector import SpotifyCollector
from app.collectors.youtube_collector import YouTubeCollector
from app.analysis.momentum_analyzer import MomentumAnalyzer
from app.analysis.authenticity_detector import AuthenticityDetector
from app.reports.intelligence_reporter import IntelligenceReporter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Heatseeker A&R Intelligence Platform",
    description="AI-powered artist discovery and momentum analysis for record labels",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize collectors
spotify_collector = SpotifyCollector()
youtube_collector = YouTubeCollector()

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the main dashboard"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Heatseeker A&R Intelligence</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: #1a1a1a; 
                color: #fff;
            }
            .header { 
                background: linear-gradient(135deg, #ff6600, #cc5500); 
                padding: 20px; 
                border-radius: 8px; 
                margin-bottom: 30px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
            .card { 
                background: #2a2a2a; 
                border: 1px solid #404040; 
                border-radius: 8px; 
                padding: 20px;
            }
            .artist-card { 
                background: #2a2a2a; 
                border: 1px solid #404040; 
                margin: 10px 0; 
                padding: 15px; 
                border-radius: 8px;
            }
            .score { 
                font-size: 24px; 
                color: #ff6600; 
                font-weight: bold; 
            }
            .urgency-high { color: #ff4444; }
            .urgency-medium { color: #ffaa00; }
            .urgency-low { color: #44ff44; }
            button {
                background: #ff6600;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                margin: 5px;
            }
            button:hover { background: #cc5500; }
            .loading { color: #888; font-style: italic; }
            .api-section { margin-top: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔥 Heatseeker A&R Intelligence</h1>
                <p>Early artist detection and momentum analysis platform</p>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h2>Daily Brief</h2>
                    <button onclick="loadDailyBrief()">Generate Today's Brief</button>
                    <div id="daily-brief" class="loading">Click to load daily intelligence...</div>
                </div>
                
                <div class="card">
                    <h2>Top Momentum Artists</h2>
                    <div id="top-artists" class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>Add Artist to Track</h2>
                <input type="text" id="artist-search" placeholder="Search artist name or Spotify ID" style="padding: 10px; width: 300px; margin-right: 10px;">
                <button onclick="searchAndAddArtist()">Search & Add</button>
                <div id="search-results"></div>
            </div>
            
            <div class="api-section">
                <div class="card">
                    <h2>API Endpoints</h2>
                    <p><strong>GET</strong> <code>/api/daily-brief</code> - Get today's intelligence brief</p>
                    <p><strong>GET</strong> <code>/api/artists/{id}/analysis</code> - Get full artist analysis</p>
                    <p><strong>POST</strong> <code>/api/artists/track</code> - Add artist to tracking</p>
                    <p><strong>GET</strong> <code>/docs</code> - Full API documentation</p>
                </div>
            </div>
        </div>
        
        <script>
            async function loadDailyBrief() {
                document.getElementById('daily-brief').innerHTML = '<div class="loading">Generating daily brief...</div>';
                
                try {
                    const response = await fetch('/api/daily-brief');
                    const data = await response.json();
                    
                    if (data.error) {
                        document.getElementById('daily-brief').innerHTML = `<p style="color: #ff4444;">Error: ${data.error}</p>`;
                        return;
                    }
                    
                    const briefHtml = `
                        <h3>Brief for ${data.date}</h3>
                        <p><strong>Summary:</strong></p>
                        <ul>
                            <li>Total artists tracked: ${data.summary_stats?.total_artists_tracked || 0}</li>
                            <li>High momentum: ${data.summary_stats?.high_momentum_artists || 0}</li>
                            <li>Urgent targets: ${data.summary_stats?.urgent_targets || 0}</li>
                        </ul>
                        
                        <h4>Top Artists to Watch:</h4>
                        ${data.top_artists_to_watch?.map(artist => `
                            <div class="artist-card">
                                <strong>${artist.name}</strong> (${artist.location || 'Unknown'})
                                <div class="score">Score: ${artist.momentum_score}</div>
                                <div class="urgency-${artist.urgency_level}">Urgency: ${artist.urgency_level?.toUpperCase()}</div>
                                <p>${artist.recommendation || 'No recommendation'}</p>
                            </div>
                        `).join('') || '<p>No high-momentum artists found</p>'}
                    `;
                    
                    document.getElementById('daily-brief').innerHTML = briefHtml;
                } catch (error) {
                    document.getElementById('daily-brief').innerHTML = `<p style="color: #ff4444;">Error loading brief: ${error.message}</p>`;
                }
            }
            
            async function searchAndAddArtist() {
                const query = document.getElementById('artist-search').value;
                if (!query) return;
                
                document.getElementById('search-results').innerHTML = '<div class="loading">Searching...</div>';
                
                try {
                    const response = await fetch(`/api/artists/search?q=${encodeURIComponent(query)}`);
                    const data = await response.json();
                    
                    if (data.length === 0) {
                        document.getElementById('search-results').innerHTML = '<p>No artists found</p>';
                        return;
                    }
                    
                    const resultsHtml = data.map(artist => `
                        <div class="artist-card">
                            <strong>${artist.name}</strong>
                            <p>Followers: ${artist.followers?.total || 'Unknown'}</p>
                            <p>Popularity: ${artist.popularity || 'Unknown'}</p>
                            <button onclick="trackArtist('${artist.id}', '${artist.name}')">Track This Artist</button>
                        </div>
                    `).join('');
                    
                    document.getElementById('search-results').innerHTML = resultsHtml;
                } catch (error) {
                    document.getElementById('search-results').innerHTML = `<p style="color: #ff4444;">Error: ${error.message}</p>`;
                }
            }
            
            async function trackArtist(spotifyId, name) {
                try {
                    const response = await fetch('/api/artists/track', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ spotify_id: spotifyId, name: name })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        alert(`Successfully added ${name} to tracking!`);
                        document.getElementById('search-results').innerHTML = '';
                        document.getElementById('artist-search').value = '';
                    } else {
                        alert(`Error: ${data.message}`);
                    }
                } catch (error) {
                    alert(`Error tracking artist: ${error.message}`);
                }
            }
            
            // Load top artists on page load
            window.onload = function() {
                loadDailyBrief();
            };
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/daily-brief")
async def get_daily_brief(
    target_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get daily A&R intelligence brief"""
    try:
        brief_date = date.fromisoformat(target_date) if target_date else date.today()
        
        reporter = IntelligenceReporter(db)
        brief = reporter.generate_daily_brief(brief_date)
        
        return brief
    except Exception as e:
        logger.error(f"Error generating daily brief: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/artists/{artist_id}/analysis")
async def get_artist_analysis(
    artist_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive analysis for a specific artist"""
    try:
        reporter = IntelligenceReporter(db)
        analysis = reporter.generate_artist_deep_dive(artist_id)
        
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating artist analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/artists/search")
async def search_artists(q: str):
    """Search for artists using Spotify API"""
    try:
        if not q:
            raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
        
        artists = await spotify_collector.search_artists(q, limit=10)
        return artists
    except Exception as e:
        logger.error(f"Error searching artists: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/artists/track")
async def track_artist(
    artist_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Add an artist to tracking system"""
    try:
        spotify_id = artist_data.get("spotify_id")
        name = artist_data.get("name")
        
        if not spotify_id or not name:
            raise HTTPException(
                status_code=400, 
                detail="Both 'spotify_id' and 'name' are required"
            )
        
        # Check if artist already exists
        existing_artist = db.query(Artist).filter(Artist.spotify_id == spotify_id).first()
        if existing_artist:
            return {
                "success": False, 
                "message": f"Artist {name} is already being tracked",
                "artist_id": existing_artist.id
            }
        
        # Create new artist record
        new_artist = Artist(
            spotify_id=spotify_id,
            name=name,
            independence_status="unknown",
            genres=artist_data.get("genres", []),
            location=artist_data.get("location")
        )
        
        db.add(new_artist)
        db.commit()
        db.refresh(new_artist)
        
        # Schedule initial data collection
        background_tasks.add_task(collect_initial_artist_data, new_artist.id, spotify_id)
        
        return {
            "success": True,
            "message": f"Successfully added {name} to tracking",
            "artist_id": new_artist.id
        }
        
    except Exception as e:
        logger.error(f"Error tracking artist: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/artists")
async def list_tracked_artists(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List all tracked artists"""
    try:
        artists = (
            db.query(Artist)
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        return [
            {
                "id": artist.id,
                "name": artist.name,
                "location": artist.location,
                "genres": artist.genres,
                "independence_status": artist.independence_status,
                "discovery_date": artist.discovery_date.isoformat() if artist.discovery_date else None,
                "spotify_id": artist.spotify_id
            }
            for artist in artists
        ]
        
    except Exception as e:
        logger.error(f"Error listing artists: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analysis/run")
async def run_analysis(
    background_tasks: BackgroundTasks,
    artist_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db)
):
    """Trigger momentum and authenticity analysis"""
    try:
        if not artist_ids:
            # Run analysis for all tracked artists
            artists = db.query(Artist).all()
            artist_ids = [artist.id for artist in artists]
        
        # Schedule analysis tasks
        for artist_id in artist_ids[:10]:  # Limit to 10 artists to prevent overload
            background_tasks.add_task(run_artist_analysis, artist_id)
        
        return {
            "success": True,
            "message": f"Analysis scheduled for {len(artist_ids[:10])} artists"
        }
        
    except Exception as e:
        logger.error(f"Error running analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/recent")
async def get_recent_reports(
    limit: int = 10,
    report_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get recent intelligence reports"""
    try:
        query = db.query(IntelligenceReport)
        
        if report_type:
            query = query.filter(IntelligenceReport.report_type == report_type)
        
        reports = (
            query.order_by(IntelligenceReport.generated_at.desc())
            .limit(limit)
            .all()
        )
        
        return [
            {
                "id": report.id,
                "report_type": report.report_type,
                "artist_id": report.artist_id,
                "generated_at": report.generated_at.isoformat(),
                "human_reviewed": report.human_reviewed,
                "content": report.content
            }
            for report in reports
        ]
        
    except Exception as e:
        logger.error(f"Error getting recent reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task functions
async def collect_initial_artist_data(artist_id: int, spotify_id: str):
    """Collect initial data for a newly tracked artist"""
    try:
        logger.info(f"Collecting initial data for artist {artist_id} (Spotify: {spotify_id})")
        
        # Get Spotify data
        artist_data = await spotify_collector.get_artist_data(spotify_id)
        
        if artist_data:
            # Store metrics in database
            # This would be implemented with proper metric storage logic
            logger.info(f"Successfully collected Spotify data for artist {artist_id}")
        
        # Get YouTube data if channel can be found
        # This would require YouTube channel discovery logic
        
    except Exception as e:
        logger.error(f"Error collecting initial data for artist {artist_id}: {e}")

async def run_artist_analysis(artist_id: int):
    """Run momentum and authenticity analysis for an artist"""
    try:
        logger.info(f"Running analysis for artist {artist_id}")
        
        # This would implement the full analysis pipeline
        # Including momentum calculation, authenticity detection, etc.
        
        logger.info(f"Analysis completed for artist {artist_id}")
        
    except Exception as e:
        logger.error(f"Error running analysis for artist {artist_id}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )