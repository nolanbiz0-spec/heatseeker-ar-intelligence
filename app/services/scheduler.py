import asyncio
import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.models.models import Artist, ArtistMetric, SongMetric, DailyScore
from app.collectors.spotify_collector import SpotifyCollector
from app.collectors.youtube_collector import YouTubeCollector
from app.analysis.momentum_analyzer import MomentumAnalyzer
from app.analysis.authenticity_detector import AuthenticityDetector
from app.reports.intelligence_reporter import IntelligenceReporter

logger = logging.getLogger(__name__)

class DataScheduler:
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        self.spotify_collector = SpotifyCollector()
        self.youtube_collector = YouTubeCollector()
        
        self.scheduler = AsyncIOScheduler()
        
    async def start(self):
        """Start the data collection scheduler"""
        logger.info("Starting Heatseeker data collection scheduler...")
        
        # Schedule daily data collection at 6 AM
        self.scheduler.add_job(
            self.collect_all_artist_data,
            CronTrigger(hour=6, minute=0),
            id="daily_data_collection",
            replace_existing=True
        )
        
        # Schedule daily analysis at 7 AM (after data collection)
        self.scheduler.add_job(
            self.run_daily_analysis,
            CronTrigger(hour=7, minute=0),
            id="daily_analysis",
            replace_existing=True
        )
        
        # Schedule daily report generation at 8 AM
        self.scheduler.add_job(
            self.generate_daily_reports,
            CronTrigger(hour=8, minute=0),
            id="daily_reports",
            replace_existing=True
        )
        
        # Schedule authenticity checks every 6 hours
        self.scheduler.add_job(
            self.run_authenticity_checks,
            CronTrigger(hour="*/6"),
            id="authenticity_checks",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Scheduler started successfully")
    
    async def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    async def collect_all_artist_data(self):
        """Collect current data for all tracked artists"""
        logger.info("Starting daily artist data collection...")
        
        db = self.SessionLocal()
        try:
            # Get all tracked artists
            artists = db.query(Artist).all()
            logger.info(f"Collecting data for {len(artists)} tracked artists")
            
            collected_count = 0
            error_count = 0
            
            for artist in artists:
                try:
                    await self._collect_artist_data(db, artist)
                    collected_count += 1
                    
                    # Rate limiting delay
                    await asyncio.sleep(settings.api_request_delay)
                    
                except Exception as e:
                    logger.error(f"Error collecting data for artist {artist.name} ({artist.id}): {e}")
                    error_count += 1
                    continue
            
            logger.info(f"Data collection completed. Success: {collected_count}, Errors: {error_count}")
            
        except Exception as e:
            logger.error(f"Error in daily data collection: {e}")
        finally:
            db.close()
    
    async def _collect_artist_data(self, db: Session, artist: Artist):
        """Collect data for a single artist"""
        timestamp = datetime.utcnow()
        
        # Collect Spotify data
        if artist.spotify_id:
            try:
                spotify_data = await self.spotify_collector.get_artist_data(artist.spotify_id)
                if spotify_data:
                    await self._store_spotify_metrics(db, artist, spotify_data, timestamp)
            except Exception as e:
                logger.error(f"Error collecting Spotify data for {artist.name}: {e}")
        
        # Collect YouTube data
        if artist.youtube_id:
            try:
                youtube_data = await self.youtube_collector.get_channel_data(artist.youtube_id)
                if youtube_data:
                    await self._store_youtube_metrics(db, artist, youtube_data, timestamp)
            except Exception as e:
                logger.error(f"Error collecting YouTube data for {artist.name}: {e}")
        
        # Update artist last_updated timestamp
        artist.last_updated = timestamp
        db.commit()
    
    async def _store_spotify_metrics(self, db: Session, artist: Artist, spotify_data: Dict, timestamp: datetime):
        """Store Spotify metrics in database"""
        try:
            artist_info = spotify_data.get("artist", {})
            
            # Store follower count
            followers = artist_info.get("followers", {}).get("total", 0)
            if followers > 0:
                metric = ArtistMetric(
                    time=timestamp,
                    artist_id=artist.id,
                    platform="spotify",
                    metric_type="followers",
                    value=followers,
                    extra_data={"raw_data": artist_info.get("followers", {})}
                )
                db.add(metric)
            
            # Store popularity score
            popularity = artist_info.get("popularity", 0)
            if popularity > 0:
                metric = ArtistMetric(
                    time=timestamp,
                    artist_id=artist.id,
                    platform="spotify",
                    metric_type="popularity",
                    value=popularity,
                    extra_data={"genres": artist_info.get("genres", [])}
                )
                db.add(metric)
            
            # Update artist genres if not set
            if not artist.genres and artist_info.get("genres"):
                artist.genres = artist_info["genres"]
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error storing Spotify metrics: {e}")
            db.rollback()
    
    async def _store_youtube_metrics(self, db: Session, artist: Artist, youtube_data: Dict, timestamp: datetime):
        """Store YouTube metrics in database"""
        try:
            channel_info = youtube_data.get("channel", {})
            stats = channel_info.get("statistics", {})
            
            # Store subscriber count
            subscribers = int(stats.get("subscriberCount", 0))
            if subscribers > 0:
                metric = ArtistMetric(
                    time=timestamp,
                    artist_id=artist.id,
                    platform="youtube",
                    metric_type="subscribers",
                    value=subscribers
                )
                db.add(metric)
            
            # Store view count
            view_count = int(stats.get("viewCount", 0))
            if view_count > 0:
                metric = ArtistMetric(
                    time=timestamp,
                    artist_id=artist.id,
                    platform="youtube",
                    metric_type="view_count",
                    value=view_count
                )
                db.add(metric)
            
            # Store video count
            video_count = int(stats.get("videoCount", 0))
            if video_count > 0:
                metric = ArtistMetric(
                    time=timestamp,
                    artist_id=artist.id,
                    platform="youtube",
                    metric_type="video_count",
                    value=video_count
                )
                db.add(metric)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error storing YouTube metrics: {e}")
            db.rollback()
    
    async def run_daily_analysis(self):
        """Run momentum and authenticity analysis for all artists"""
        logger.info("Starting daily artist analysis...")
        
        db = self.SessionLocal()
        try:
            artists = db.query(Artist).all()
            analyzer = MomentumAnalyzer(db)
            
            analysis_count = 0
            error_count = 0
            
            for artist in artists:
                try:
                    # Calculate momentum score
                    momentum_data = analyzer.generate_momentum_insights(artist.id)
                    
                    # Store daily score
                    await self._store_daily_score(db, artist.id, momentum_data)
                    analysis_count += 1
                    
                except Exception as e:
                    logger.error(f"Error analyzing artist {artist.name}: {e}")
                    error_count += 1
                    continue
            
            logger.info(f"Daily analysis completed. Success: {analysis_count}, Errors: {error_count}")
            
        except Exception as e:
            logger.error(f"Error in daily analysis: {e}")
        finally:
            db.close()
    
    async def _store_daily_score(self, db: Session, artist_id: int, momentum_data: Dict):
        """Store daily momentum score"""
        try:
            today = date.today()
            
            # Check if score already exists for today
            existing_score = db.query(DailyScore).filter(
                DailyScore.artist_id == artist_id,
                DailyScore.date == today
            ).first()
            
            if existing_score:
                # Update existing score
                existing_score.momentum_score = int(momentum_data.get("velocity_score", 0))
                existing_score.breakout_probability = momentum_data.get("breakout_probability", 0.0)
                existing_score.urgency_level = momentum_data.get("urgency_level", "low")
            else:
                # Create new score
                daily_score = DailyScore(
                    date=today,
                    artist_id=artist_id,
                    momentum_score=int(momentum_data.get("velocity_score", 0)),
                    breakout_probability=momentum_data.get("breakout_probability", 0.0),
                    urgency_level=momentum_data.get("urgency_level", "low"),
                    overall_score=int(momentum_data.get("velocity_score", 0))  # Simplified for MVP
                )
                db.add(daily_score)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error storing daily score for artist {artist_id}: {e}")
            db.rollback()
    
    async def run_authenticity_checks(self):
        """Run authenticity analysis for high-momentum artists"""
        logger.info("Starting authenticity checks...")
        
        db = self.SessionLocal()
        try:
            # Get artists with high momentum scores from recent daily scores
            high_momentum_artists = db.query(Artist).join(DailyScore).filter(
                DailyScore.date >= date.today() - timedelta(days=3),
                DailyScore.momentum_score >= 60
            ).distinct().all()
            
            detector = AuthenticityDetector(db)
            check_count = 0
            
            for artist in high_momentum_artists:
                try:
                    authenticity_data = detector.analyze_artist_authenticity(artist.id)
                    check_count += 1
                    
                    # Log any high-risk findings
                    if authenticity_data.get("risk_level") == "high":
                        logger.warning(f"High authenticity risk detected for artist {artist.name} (ID: {artist.id})")
                    
                except Exception as e:
                    logger.error(f"Error checking authenticity for artist {artist.name}: {e}")
                    continue
            
            logger.info(f"Authenticity checks completed for {check_count} artists")
            
        except Exception as e:
            logger.error(f"Error in authenticity checks: {e}")
        finally:
            db.close()
    
    async def generate_daily_reports(self):
        """Generate daily intelligence reports"""
        logger.info("Generating daily intelligence reports...")
        
        db = self.SessionLocal()
        try:
            reporter = IntelligenceReporter(db)
            
            # Generate daily brief
            daily_brief = reporter.generate_daily_brief()
            
            if daily_brief and not daily_brief.get("error"):
                logger.info("Daily intelligence brief generated successfully")
                
                # Log key statistics
                stats = daily_brief.get("summary_stats", {})
                logger.info(f"Daily stats - Total artists: {stats.get('total_artists_tracked', 0)}, "
                           f"High momentum: {stats.get('high_momentum_artists', 0)}, "
                           f"Urgent targets: {stats.get('urgent_targets', 0)}")
            else:
                logger.error("Failed to generate daily brief")
            
        except Exception as e:
            logger.error(f"Error generating daily reports: {e}")
        finally:
            db.close()
    
    async def run_manual_collection(self, artist_ids: List[int] = None):
        """Run manual data collection for specific artists or all"""
        logger.info("Running manual data collection...")
        
        db = self.SessionLocal()
        try:
            if artist_ids:
                artists = db.query(Artist).filter(Artist.id.in_(artist_ids)).all()
            else:
                artists = db.query(Artist).all()
            
            for artist in artists:
                await self._collect_artist_data(db, artist)
                await asyncio.sleep(0.5)  # Rate limiting
            
            logger.info(f"Manual collection completed for {len(artists)} artists")
            
        except Exception as e:
            logger.error(f"Error in manual collection: {e}")
        finally:
            db.close()


# Standalone scheduler application
async def main():
    """Main function to run the scheduler as a standalone service"""
    scheduler = DataScheduler()
    
    try:
        await scheduler.start()
        logger.info("Heatseeker data scheduler is running...")
        
        # Keep the scheduler running
        while True:
            await asyncio.sleep(60)  # Sleep for 1 minute
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal...")
    finally:
        await scheduler.stop()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the scheduler
    asyncio.run(main())