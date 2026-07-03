from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Date, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Artist(Base):
    __tablename__ = "artists"
    
    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String(50), unique=True, index=True)
    youtube_id = Column(String(50), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=False, index=True)
    genres = Column(JSON, nullable=True)  # Store as JSON for SQLite compatibility
    location = Column(String(255), nullable=True)
    discovery_date = Column(DateTime(timezone=True), server_default=func.now())
    independence_status = Column(String(50), nullable=True)  # unsigned, indie_dist, label_services, major, unknown
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    extra_data = Column(JSON, nullable=True)
    
    # Relationships
    metrics = relationship("ArtistMetric", back_populates="artist")
    songs = relationship("Song", back_populates="artist")
    daily_scores = relationship("DailyScore", back_populates="artist")
    authenticity_signals = relationship("AuthenticitySignal", back_populates="artist")

class Song(Base):
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    title = Column(String(255), nullable=False)
    spotify_id = Column(String(50), nullable=True, index=True)
    youtube_id = Column(String(50), nullable=True)
    release_date = Column(Date, nullable=True)
    isrc = Column(String(20), nullable=True)
    extra_data = Column(JSON, nullable=True)
    
    # Relationships
    artist = relationship("Artist", back_populates="songs")
    metrics = relationship("SongMetric", back_populates="song")
    playlist_placements = relationship("PlaylistPlacement", back_populates="song")

class ArtistMetric(Base):
    __tablename__ = "artist_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime(timezone=True), nullable=False, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False, index=True)
    platform = Column(String(20), nullable=False)  # spotify, youtube, tiktok, etc.
    metric_type = Column(String(30), nullable=False)  # monthly_listeners, followers, views
    value = Column(Integer, nullable=False)
    extra_data = Column(JSON, nullable=True)
    
    # Relationships
    artist = relationship("Artist", back_populates="metrics")

class SongMetric(Base):
    __tablename__ = "song_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime(timezone=True), nullable=False, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False, index=True)
    platform = Column(String(20), nullable=False)
    metric_type = Column(String(30), nullable=False)  # streams, saves, playlist_adds
    value = Column(Integer, nullable=False)
    extra_data = Column(JSON, nullable=True)
    
    # Relationships
    song = relationship("Song", back_populates="metrics")

class PlaylistPlacement(Base):
    __tablename__ = "playlist_placements"
    
    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    playlist_id = Column(String(50), nullable=False)
    playlist_name = Column(String(255), nullable=True)
    platform = Column(String(20), nullable=False)
    placement_date = Column(DateTime(timezone=True), nullable=False)
    playlist_followers = Column(Integer, nullable=True)
    is_editorial = Column(Boolean, default=False)
    curator_info = Column(JSON, nullable=True)
    
    # Relationships
    song = relationship("Song", back_populates="playlist_placements")

class AuthenticitySignal(Base):
    __tablename__ = "authenticity_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    signal_type = Column(String(50), nullable=False)  # bot_risk, engagement_quality, geographic_spread
    value = Column(DECIMAL(5,2), nullable=False)
    confidence = Column(DECIMAL(3,2), nullable=False)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(JSON, nullable=True)
    
    # Relationships
    artist = relationship("Artist", back_populates="authenticity_signals")

class DailyScore(Base):
    __tablename__ = "daily_scores"
    
    date = Column(Date, nullable=False, primary_key=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False, primary_key=True)
    overall_score = Column(Integer, nullable=True)
    momentum_score = Column(Integer, nullable=True)
    authenticity_score = Column(Integer, nullable=True)
    cultural_score = Column(Integer, nullable=True)
    commercial_score = Column(Integer, nullable=True)
    breakout_probability = Column(DECIMAL(3,2), nullable=True)
    urgency_level = Column(String(10), nullable=True)  # high, medium, low
    
    # Relationships
    artist = relationship("Artist", back_populates="daily_scores")

class IntelligenceReport(Base):
    __tablename__ = "intelligence_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    report_type = Column(String(20), nullable=False)  # daily_brief, weekly_deep, alert
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    content = Column(JSON, nullable=False)
    human_reviewed = Column(Boolean, default=False)
    reviewer_notes = Column(Text, nullable=True)