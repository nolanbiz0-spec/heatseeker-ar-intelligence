#!/usr/bin/env python3

"""
Heatseeker Demo Script
Demonstrates the platform's capabilities with sample data
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.models import Base, Artist, ArtistMetric, DailyScore
from app.collectors.spotify_collector import SpotifyCollector
from app.analysis.momentum_analyzer import MomentumAnalyzer
from app.analysis.authenticity_detector import AuthenticityDetector
from app.reports.intelligence_reporter import IntelligenceReporter

class HeatSeekerDemo:
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
        
        self.spotify_collector = SpotifyCollector()
    
    async def run_demo(self):
        """Run the complete Heatseeker demonstration"""
        print("🔥 Heatseeker A&R Intelligence Platform Demo")
        print("=" * 50)
        
        # Step 1: Add sample artists
        print("\n1. Adding sample artists to tracking system...")
        sample_artists = await self._add_sample_artists()
        
        # Step 2: Generate sample metrics
        print("\n2. Generating sample historical metrics...")
        await self._generate_sample_metrics(sample_artists)
        
        # Step 3: Run momentum analysis
        print("\n3. Running momentum analysis...")
        await self._run_momentum_analysis(sample_artists)
        
        # Step 4: Run authenticity analysis  
        print("\n4. Running authenticity analysis...")
        await self._run_authenticity_analysis(sample_artists)
        
        # Step 5: Generate intelligence reports
        print("\n5. Generating intelligence reports...")
        await self._generate_intelligence_reports()
        
        # Step 6: Display results
        print("\n6. Demo Results:")
        await self._display_demo_results()
        
        print("\n✅ Demo completed successfully!")
        print("\nNext steps:")
        print("1. Configure real API keys in .env file")
        print("2. Add real artists using the web interface")
        print("3. Start the scheduler for automated data collection")
        print("4. Access the dashboard at http://localhost:8000")
    
    async def _add_sample_artists(self):
        """Add sample artists for demonstration"""
        db = self.SessionLocal()
        
        sample_artists_data = [
            {
                "name": "Luna Eclipse",
                "spotify_id": "demo_luna_eclipse", 
                "genres": ["indie pop", "dream pop"],
                "location": "Brooklyn, NY",
                "independence_status": "unsigned"
            },
            {
                "name": "Neon Arcade",
                "spotify_id": "demo_neon_arcade",
                "genres": ["synthwave", "electronic"],
                "location": "Los Angeles, CA", 
                "independence_status": "indie_dist"
            },
            {
                "name": "Velvet Storm",
                "spotify_id": "demo_velvet_storm",
                "genres": ["alt rock", "indie"],
                "location": "Austin, TX",
                "independence_status": "unsigned"
            },
            {
                "name": "Digital Sunset",
                "spotify_id": "demo_digital_sunset",
                "genres": ["lo-fi", "chillwave"],
                "location": "Portland, OR",
                "independence_status": "unknown"
            }
        ]
        
        created_artists = []
        
        for artist_data in sample_artists_data:
            # Check if artist already exists
            existing = db.query(Artist).filter(Artist.spotify_id == artist_data["spotify_id"]).first()
            
            if not existing:
                artist = Artist(**artist_data)
                db.add(artist)
                db.commit()
                # Re-query to get the committed artist with ID
                artist = db.query(Artist).filter(Artist.spotify_id == artist_data["spotify_id"]).first()
                created_artists.append(artist)
                print(f"   ✓ Added {artist.name} to tracking")
            else:
                created_artists.append(existing)
                print(f"   ✓ {existing.name} already exists")
        
        db.close()
        return created_artists
    
    async def _generate_sample_metrics(self, artists):
        """Generate realistic sample metrics for demonstration"""
        db = self.SessionLocal()
        
        base_date = datetime.utcnow() - timedelta(days=30)
        
        for artist in artists:
            print(f"   Generating metrics for {artist.name}...")
            
            # Generate 30 days of sample data
            for day in range(30):
                metric_date = base_date + timedelta(days=day)
                
                # Simulate different growth patterns
                if artist.name == "Luna Eclipse":
                    # High growth trajectory (breakout candidate)
                    followers = 5000 + (day * 200) + (day ** 2 * 5)
                    popularity = min(85, 30 + day * 1.8)
                elif artist.name == "Neon Arcade": 
                    # Moderate steady growth
                    followers = 12000 + (day * 100)
                    popularity = min(70, 45 + day * 0.8)
                elif artist.name == "Velvet Storm":
                    # Explosive recent growth (urgent target)
                    if day < 20:
                        followers = 3000 + (day * 50)
                        popularity = 25 + day * 0.5
                    else:
                        followers = 4000 + ((day-20) * 400)
                        popularity = 35 + (day-20) * 3
                else:  # Digital Sunset
                    # Slow, authentic growth
                    followers = 8000 + (day * 80)
                    popularity = min(60, 40 + day * 0.6)
                
                # Add Spotify metrics
                spotify_followers = ArtistMetric(
                    time=metric_date,
                    artist_id=artist.id,
                    platform="spotify",
                    metric_type="followers", 
                    value=int(followers)
                )
                db.add(spotify_followers)
                
                spotify_popularity = ArtistMetric(
                    time=metric_date,
                    artist_id=artist.id,
                    platform="spotify",
                    metric_type="popularity",
                    value=int(popularity)
                )
                db.add(spotify_popularity)
                
                # Add YouTube metrics (correlated but different scale)
                youtube_subscribers = ArtistMetric(
                    time=metric_date,
                    artist_id=artist.id,
                    platform="youtube",
                    metric_type="subscribers",
                    value=int(followers * 0.3)  # YouTube typically lower than Spotify
                )
                db.add(youtube_subscribers)
        
        db.commit()
        db.close()
        print("   ✓ Sample metrics generated")
    
    async def _run_momentum_analysis(self, artists):
        """Run momentum analysis on sample artists"""
        db = self.SessionLocal()
        analyzer = MomentumAnalyzer(db)
        
        for artist in artists:
            print(f"   Analyzing momentum for {artist.name}...")
            
            momentum_data = analyzer.generate_momentum_insights(artist.id)
            
            # Store daily score
            daily_score = DailyScore(
                date=date.today(),
                artist_id=artist.id,
                momentum_score=int(momentum_data.get("velocity_score", 0)),
                breakout_probability=momentum_data.get("breakout_probability", 0.0),
                urgency_level=momentum_data.get("urgency_level", "low"),
                overall_score=int(momentum_data.get("velocity_score", 0))
            )
            
            db.add(daily_score)
            print(f"      Score: {daily_score.momentum_score}/100, Urgency: {daily_score.urgency_level}")
        
        db.commit()
        db.close()
        print("   ✓ Momentum analysis completed")
    
    async def _run_authenticity_analysis(self, artists):
        """Run authenticity analysis on sample artists"""
        db = self.SessionLocal()
        detector = AuthenticityDetector(db)
        
        for artist in artists:
            print(f"   Checking authenticity for {artist.name}...")
            
            authenticity_data = detector.analyze_artist_authenticity(artist.id)
            
            print(f"      Authenticity Score: {authenticity_data.get('authenticity_score', 0)}/100")
            print(f"      Risk Level: {authenticity_data.get('risk_level', 'unknown')}")
        
        db.close()
        print("   ✓ Authenticity analysis completed")
    
    async def _generate_intelligence_reports(self):
        """Generate sample intelligence reports"""
        db = self.SessionLocal()
        reporter = IntelligenceReporter(db)
        
        # Generate daily brief
        daily_brief = reporter.generate_daily_brief()
        
        print(f"   Generated daily brief with {len(daily_brief.get('top_artists_to_watch', []))} top artists")
        
        # Generate deep dive for first high-momentum artist
        high_momentum_artists = daily_brief.get('top_artists_to_watch', [])
        if high_momentum_artists:
            first_artist = high_momentum_artists[0]
            deep_dive = reporter.generate_artist_deep_dive(first_artist['artist_id'])
            print(f"   Generated deep dive report for {first_artist['name']}")
        
        db.close()
        print("   ✓ Intelligence reports generated")
    
    async def _display_demo_results(self):
        """Display demo results in a formatted way"""
        db = self.SessionLocal()
        reporter = IntelligenceReporter(db)
        
        # Get daily brief
        daily_brief = reporter.generate_daily_brief()
        
        print("\n" + "="*60)
        print("HEATSEEKER DAILY INTELLIGENCE BRIEF")
        print("="*60)
        
        print(f"\nDate: {daily_brief.get('date', 'Unknown')}")
        
        # Summary stats
        stats = daily_brief.get('summary_stats', {})
        print(f"\n📊 SUMMARY STATISTICS")
        print(f"   Total Artists Tracked: {stats.get('total_artists_tracked', 0)}")
        print(f"   High Momentum Artists: {stats.get('high_momentum_artists', 0)}")
        print(f"   Urgent Targets: {stats.get('urgent_targets', 0)}")
        print(f"   Average Momentum Score: {stats.get('average_momentum_score', 0)}")
        
        # Top artists to watch
        top_artists = daily_brief.get('top_artists_to_watch', [])
        if top_artists:
            print(f"\n🎯 TOP ARTISTS TO WATCH")
            for i, artist in enumerate(top_artists[:3], 1):
                print(f"   {i}. {artist['name']} ({artist.get('location', 'Unknown')})")
                print(f"      Momentum Score: {artist['momentum_score']}/100")
                print(f"      Breakout Probability: {artist.get('breakout_probability', 0):.1%}")
                print(f"      Urgency: {artist.get('urgency_level', 'unknown').upper()}")
                print(f"      Recommendation: {artist.get('recommendation', 'Monitor')}")
                print()
        
        # Biggest risers
        risers = daily_brief.get('biggest_risers', [])
        if risers:
            print(f"📈 BIGGEST RISERS (24H)")
            for riser in risers:
                print(f"   • {riser['name']}: +{riser.get('score_change', 0)} points")
        
        # Urgent targets
        urgent = daily_brief.get('urgent_outreach_targets', [])
        if urgent:
            print(f"\n🚨 URGENT OUTREACH TARGETS")
            for target in urgent:
                print(f"   • {target['name']}: {target.get('action_required', 'Contact required')}")
        
        # Market insights
        insights = daily_brief.get('market_insights', {})
        hot_genres = insights.get('hot_genres', [])
        if hot_genres:
            print(f"\n🔥 HOT GENRES")
            for genre in hot_genres[:3]:
                print(f"   • {genre.get('genre', 'Unknown')}: {genre.get('artist_count', 0)} artists")
        
        db.close()


async def main():
    """Main demo function"""
    demo = HeatSeekerDemo()
    
    try:
        await demo.run_demo()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running")
        print("2. Check database connection in .env file") 
        print("3. Run './setup.sh' to initialize the system")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())