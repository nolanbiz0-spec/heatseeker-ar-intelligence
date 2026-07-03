from sqlalchemy import String, Integer, DateTime, Float, Boolean, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional, Dict, Any
from ..database import Base


class Artist(Base):
    """Artist tracking and analytics model"""
    
    __tablename__ = "artists"
    
    # Primary identifiers
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    spotify_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)
    youtube_channel_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)
    lastfm_name: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    musicbrainz_id: Mapped[Optional[str]] = mapped_column(String(36), unique=True, index=True)
    
    # Status tracking
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_independent: Mapped[Optional[bool]] = mapped_column(Boolean, index=True)
    label_name: Mapped[Optional[str]] = mapped_column(String(255))
    distributor: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_analyzed: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True)
    
    # Current metrics (latest snapshot)
    spotify_followers: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    spotify_monthly_listeners: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    youtube_subscribers: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    youtube_views: Mapped[Optional[int]] = mapped_column(Integer)
    lastfm_listeners: Mapped[Optional[int]] = mapped_column(Integer)
    lastfm_playcount: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Velocity scores (7/30/90 day growth rates)
    velocity_7d: Mapped[Optional[float]] = mapped_column(Float, index=True)
    velocity_30d: Mapped[Optional[float]] = mapped_column(Float, index=True)
    velocity_90d: Mapped[Optional[float]] = mapped_column(Float, index=True)
    
    # Composite scores
    momentum_score: Mapped[Optional[float]] = mapped_column(Float, index=True)
    authenticity_score: Mapped[Optional[float]] = mapped_column(Float, index=True)
    opportunity_score: Mapped[Optional[float]] = mapped_column(Float, index=True)
    urgency_score: Mapped[Optional[float]] = mapped_column(Float, index=True)
    
    # Metadata
    genres: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)  # List of genre tags
    countries: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)  # Geographic breakdown
    recent_playlists: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)  # Playlist placements
    social_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)  # Cross-platform data
    
    # Analysis flags
    bot_farm_risk: Mapped[Optional[float]] = mapped_column(Float)
    geographic_anomaly: Mapped[Optional[bool]] = mapped_column(Boolean)
    engagement_ratio: Mapped[Optional[float]] = mapped_column(Float)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_artist_momentum_active', 'momentum_score', 'is_active'),
        Index('ix_artist_opportunity_independent', 'opportunity_score', 'is_independent'),
        Index('ix_artist_velocity_compound', 'velocity_7d', 'velocity_30d', 'velocity_90d'),
        Index('ix_artist_updated_active', 'updated_at', 'is_active'),
    )


class ArtistSnapshot(Base):
    """Historical snapshots for velocity calculations"""
    
    __tablename__ = "artist_snapshots"
    
    # Primary identifiers
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    artist_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Platform metrics at snapshot time
    spotify_followers: Mapped[Optional[int]] = mapped_column(Integer)
    spotify_monthly_listeners: Mapped[Optional[int]] = mapped_column(Integer)
    youtube_subscribers: Mapped[Optional[int]] = mapped_column(Integer)
    youtube_views: Mapped[Optional[int]] = mapped_column(Integer)
    lastfm_listeners: Mapped[Optional[int]] = mapped_column(Integer)
    lastfm_playcount: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Additional snapshot data
    top_tracks: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    playlist_adds: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    geographic_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Performance indexes
    __table_args__ = (
        Index('ix_snapshot_artist_date', 'artist_id', 'snapshot_date'),
        Index('ix_snapshot_date_only', 'snapshot_date'),
    )