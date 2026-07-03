import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.models import Artist, ArtistMetric, DailyScore
from app.analysis.momentum_analyzer import MomentumAnalyzer
from app.analysis.authenticity_detector import AuthenticityDetector

# Test database URL (use SQLite for testing)
TEST_DATABASE_URL = "sqlite:///./test_heatseeker.db"

@pytest.fixture
def test_db():
    """Create test database session"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    yield db
    
    # Cleanup
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_artist(test_db):
    """Create sample artist for testing"""
    artist = Artist(
        name="Test Artist",
        spotify_id="test_spotify_id",
        genres=["pop", "indie"],
        location="Test City",
        independence_status="unsigned"
    )
    test_db.add(artist)
    test_db.commit()
    test_db.refresh(artist)
    return artist

def test_artist_creation(test_db):
    """Test basic artist creation"""
    artist = Artist(
        name="Test Artist",
        spotify_id="test_id_123",
        genres=["rock", "alternative"],
        location="New York, NY",
        independence_status="unsigned"
    )
    
    test_db.add(artist)
    test_db.commit()
    
    # Verify artist was created
    retrieved_artist = test_db.query(Artist).filter(Artist.spotify_id == "test_id_123").first()
    assert retrieved_artist is not None
    assert retrieved_artist.name == "Test Artist"
    assert retrieved_artist.genres == ["rock", "alternative"]

def test_artist_metrics_creation(test_db, sample_artist):
    """Test artist metrics creation"""
    # Create sample metrics
    metric = ArtistMetric(
        time=datetime.utcnow(),
        artist_id=sample_artist.id,
        platform="spotify",
        metric_type="followers",
        value=10000
    )
    
    test_db.add(metric)
    test_db.commit()
    
    # Verify metric was created
    retrieved_metric = test_db.query(ArtistMetric).filter(
        ArtistMetric.artist_id == sample_artist.id
    ).first()
    
    assert retrieved_metric is not None
    assert retrieved_metric.platform == "spotify"
    assert retrieved_metric.metric_type == "followers"
    assert retrieved_metric.value == 10000

def test_momentum_analyzer(test_db, sample_artist):
    """Test momentum analysis functionality"""
    # Create sample metrics over time
    base_time = datetime.utcnow() - timedelta(days=10)
    
    for day in range(10):
        metric_time = base_time + timedelta(days=day)
        followers = 5000 + (day * 100)  # Growing follower count
        
        metric = ArtistMetric(
            time=metric_time,
            artist_id=sample_artist.id,
            platform="spotify",
            metric_type="followers",
            value=followers
        )
        test_db.add(metric)
    
    test_db.commit()
    
    # Run momentum analysis
    analyzer = MomentumAnalyzer(test_db)
    velocity_data = analyzer.calculate_velocity_score(sample_artist.id, days=10)
    
    # Verify analysis results
    assert "overall_score" in velocity_data
    assert velocity_data["overall_score"] >= 0
    assert "platform_scores" in velocity_data

def test_authenticity_detector(test_db, sample_artist):
    """Test authenticity detection functionality"""
    # Create sample metrics
    base_time = datetime.utcnow() - timedelta(days=5)
    
    for day in range(5):
        metric_time = base_time + timedelta(days=day)
        followers = 5000 + (day * 50)  # Normal growth pattern
        
        metric = ArtistMetric(
            time=metric_time,
            artist_id=sample_artist.id,
            platform="spotify",
            metric_type="followers",
            value=followers
        )
        test_db.add(metric)
    
    test_db.commit()
    
    # Run authenticity analysis
    detector = AuthenticityDetector(test_db)
    authenticity_data = detector.analyze_artist_authenticity(sample_artist.id)
    
    # Verify analysis results
    assert "authenticity_score" in authenticity_data
    assert "risk_level" in authenticity_data
    assert authenticity_data["authenticity_score"] >= 0
    assert authenticity_data["authenticity_score"] <= 100

def test_daily_score_creation(test_db, sample_artist):
    """Test daily score creation and retrieval"""
    from datetime import date
    
    daily_score = DailyScore(
        date=date.today(),
        artist_id=sample_artist.id,
        momentum_score=75,
        breakout_probability=0.65,
        urgency_level="high",
        overall_score=78
    )
    
    test_db.add(daily_score)
    test_db.commit()
    
    # Verify daily score was created
    retrieved_score = test_db.query(DailyScore).filter(
        DailyScore.artist_id == sample_artist.id,
        DailyScore.date == date.today()
    ).first()
    
    assert retrieved_score is not None
    assert retrieved_score.momentum_score == 75
    assert retrieved_score.urgency_level == "high"

@pytest.mark.asyncio
async def test_spotify_collector_initialization():
    """Test Spotify collector initialization"""
    from app.collectors.spotify_collector import SpotifyCollector
    
    collector = SpotifyCollector()
    assert collector is not None
    assert collector.base_url == "https://api.spotify.com/v1"

@pytest.mark.asyncio 
async def test_youtube_collector_initialization():
    """Test YouTube collector initialization"""
    from app.collectors.youtube_collector import YouTubeCollector
    
    collector = YouTubeCollector()
    assert collector is not None
    assert collector.base_url == "https://www.googleapis.com/youtube/v3"

def test_database_models_relationships(test_db, sample_artist):
    """Test database model relationships"""
    # Create related objects
    metric = ArtistMetric(
        time=datetime.utcnow(),
        artist_id=sample_artist.id,
        platform="spotify",
        metric_type="followers",
        value=5000
    )
    test_db.add(metric)
    
    daily_score = DailyScore(
        date=date.today(),
        artist_id=sample_artist.id,
        momentum_score=70,
        overall_score=70
    )
    test_db.add(daily_score)
    test_db.commit()
    
    # Test relationships
    assert len(sample_artist.metrics) > 0
    assert len(sample_artist.daily_scores) > 0
    assert metric.artist == sample_artist
    assert daily_score.artist == sample_artist

if __name__ == "__main__":
    pytest.main([__file__, "-v"])