from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..database import get_db
from ..models.artist import Artist, ArtistSnapshot
from ..services.spotify import spotify_client
from ..services.youtube import youtube_client
from ..services.lastfm import lastfm_client, musicbrainz_client
from ..core.velocity import velocity_engine, cross_platform_analyzer
from ..core.authenticity import authenticity_scorer
from ..core.scoring import opportunity_scorer


router = APIRouter()


# Pydantic models
class ArtistCreate(BaseModel):
    name: str
    spotify_id: Optional[str] = None
    youtube_channel_id: Optional[str] = None
    lastfm_name: Optional[str] = None
    musicbrainz_id: Optional[str] = None


class ArtistResponse(BaseModel):
    id: int
    name: str
    spotify_id: Optional[str]
    youtube_channel_id: Optional[str]
    lastfm_name: Optional[str]
    is_active: bool
    is_independent: Optional[bool]
    
    # Current metrics
    spotify_followers: Optional[int]
    spotify_monthly_listeners: Optional[int]
    youtube_subscribers: Optional[int]
    youtube_views: Optional[int]
    lastfm_listeners: Optional[int]
    
    # Scores
    velocity_7d: Optional[float]
    velocity_30d: Optional[float]
    velocity_90d: Optional[float]
    momentum_score: Optional[float]
    authenticity_score: Optional[float]
    opportunity_score: Optional[float]
    urgency_score: Optional[float]
    
    created_at: datetime
    updated_at: datetime
    last_analyzed: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/", response_model=ArtistResponse)
async def add_artist(
    artist_data: ArtistCreate,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Add a new artist to tracking system"""
    
    # Check if artist already exists
    existing_query = select(Artist).where(
        or_(
            Artist.name.ilike(f"%{artist_data.name}%"),
            Artist.spotify_id == artist_data.spotify_id
        )
    )
    result = await db.execute(existing_query)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Artist already being tracked")
    
    # Create new artist
    new_artist = Artist(
        name=artist_data.name,
        spotify_id=artist_data.spotify_id,
        youtube_channel_id=artist_data.youtube_channel_id,
        lastfm_name=artist_data.lastfm_name or artist_data.name,
        musicbrainz_id=artist_data.musicbrainz_id,
        is_active=True
    )
    
    db.add(new_artist)
    await db.flush()  # Get the ID
    
    # Schedule initial data collection
    if background_tasks:
        background_tasks.add_task(collect_artist_data, new_artist.id, db)
    
    await db.commit()
    await db.refresh(new_artist)
    
    return new_artist


@router.get("/", response_model=List[ArtistResponse])
async def list_artists(
    active_only: bool = Query(True, description="Only return active artists"),
    sort_by: str = Query("momentum_score", description="Sort field: momentum_score, opportunity_score, velocity_7d"),
    limit: int = Query(50, le=200, description="Number of artists to return"),
    offset: int = Query(0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db)
):
    """List tracked artists with current scores"""
    
    query = select(Artist)
    
    if active_only:
        query = query.where(Artist.is_active == True)
    
    # Sorting
    if sort_by == "momentum_score":
        query = query.order_by(desc(Artist.momentum_score))
    elif sort_by == "opportunity_score":
        query = query.order_by(desc(Artist.opportunity_score))
    elif sort_by == "velocity_7d":
        query = query.order_by(desc(Artist.velocity_7d))
    elif sort_by == "updated_at":
        query = query.order_by(desc(Artist.updated_at))
    else:
        query = query.order_by(desc(Artist.created_at))
    
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    artists = result.scalars().all()
    
    return artists


@router.get("/{artist_id}", response_model=ArtistResponse)
async def get_artist(artist_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed artist information"""
    
    query = select(Artist).where(Artist.id == artist_id)
    result = await db.execute(query)
    artist = result.scalar_one_or_none()
    
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    return artist


@router.put("/{artist_id}/analyze")
async def analyze_artist(
    artist_id: int,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Trigger comprehensive analysis for an artist"""
    
    query = select(Artist).where(Artist.id == artist_id)
    result = await db.execute(query)
    artist = result.scalar_one_or_none()
    
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    if background_tasks:
        background_tasks.add_task(comprehensive_analysis, artist_id, db)
    
    return {"status": "analysis_queued", "artist_id": artist_id}


@router.delete("/{artist_id}")
async def remove_artist(artist_id: int, db: AsyncSession = Depends(get_db)):
    """Remove artist from tracking"""
    
    query = select(Artist).where(Artist.id == artist_id)
    result = await db.execute(query)
    artist = result.scalar_one_or_none()
    
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    # Soft delete - mark as inactive
    artist.is_active = False
    artist.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"status": "removed", "artist_id": artist_id}


@router.get("/{artist_id}/history")
async def get_artist_history(
    artist_id: int,
    days: int = Query(90, description="Number of days of history"),
    db: AsyncSession = Depends(get_db)
):
    """Get historical data snapshots for an artist"""
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(ArtistSnapshot).where(
        and_(
            ArtistSnapshot.artist_id == artist_id,
            ArtistSnapshot.snapshot_date >= since_date
        )
    ).order_by(ArtistSnapshot.snapshot_date)
    
    result = await db.execute(query)
    snapshots = result.scalars().all()
    
    return [
        {
            "date": snapshot.snapshot_date,
            "spotify_followers": snapshot.spotify_followers,
            "spotify_monthly_listeners": snapshot.spotify_monthly_listeners,
            "youtube_subscribers": snapshot.youtube_subscribers,
            "youtube_views": snapshot.youtube_views,
            "lastfm_listeners": snapshot.lastfm_listeners
        }
        for snapshot in snapshots
    ]


# Background task functions
async def collect_artist_data(artist_id: int, db: AsyncSession):
    """Collect initial data for a new artist"""
    
    query = select(Artist).where(Artist.id == artist_id)
    result = await db.execute(query)
    artist = result.scalar_one_or_none()
    
    if not artist:
        return
    
    # Collect from all platforms
    platform_data = {}
    
    # Spotify data
    if artist.spotify_id:
        try:
            spotify_artist = await spotify_client.get_artist(artist.spotify_id)
            platform_data["spotify_followers"] = spotify_artist.get("followers", {}).get("total", 0)
        except Exception:
            pass
    elif artist.name:
        try:
            search_results = await spotify_client.search_artist(artist.name)
            if search_results:
                spotify_artist = search_results[0]
                artist.spotify_id = spotify_artist["id"]
                platform_data["spotify_followers"] = spotify_artist.get("followers", {}).get("total", 0)
        except Exception:
            pass
    
    # YouTube data
    if artist.youtube_channel_id:
        try:
            channel_stats = await youtube_client.get_channel_stats(artist.youtube_channel_id)
            stats = channel_stats.get("statistics", {})
            platform_data["youtube_subscribers"] = int(stats.get("subscriberCount", 0))
            platform_data["youtube_views"] = int(stats.get("viewCount", 0))
        except Exception:
            pass
    
    # Last.fm data
    if artist.lastfm_name:
        try:
            lastfm_info = await lastfm_client.get_artist_info(artist.lastfm_name)
            if lastfm_info:
                platform_data["lastfm_listeners"] = int(lastfm_info.get("stats", {}).get("listeners", 0))
                platform_data["lastfm_playcount"] = int(lastfm_info.get("stats", {}).get("playcount", 0))
        except Exception:
            pass
    
    # Update artist with collected data
    for key, value in platform_data.items():
        setattr(artist, key, value)
    
    artist.last_analyzed = datetime.utcnow()
    await db.commit()
    
    # Create initial snapshot
    snapshot = ArtistSnapshot(
        artist_id=artist.id,
        **platform_data
    )
    db.add(snapshot)
    await db.commit()


async def comprehensive_analysis(artist_id: int, db: AsyncSession):
    """Run full analysis pipeline for an artist"""
    
    # This would be implemented as part of the analysis engine
    # For now, just update the timestamp
    query = select(Artist).where(Artist.id == artist_id)
    result = await db.execute(query)
    artist = result.scalar_one_or_none()
    
    if artist:
        artist.last_analyzed = datetime.utcnow()
        await db.commit()