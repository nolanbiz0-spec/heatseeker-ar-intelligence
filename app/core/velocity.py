from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.artist import Artist, ArtistSnapshot


class VelocityEngine:
    """Calculate growth velocity and momentum scores for artists"""
    
    @staticmethod
    async def calculate_growth_rate(
        current_value: int,
        previous_value: int,
        days: int
    ) -> float:
        """Calculate percentage growth rate over time period"""
        if previous_value <= 0:
            return 0.0
        
        growth = ((current_value - previous_value) / previous_value) * 100
        # Annualize the growth rate
        annual_multiplier = 365 / days
        return growth * annual_multiplier
    
    @staticmethod
    async def get_historical_snapshot(
        db: AsyncSession,
        artist_id: int,
        days_ago: int
    ) -> Optional[ArtistSnapshot]:
        """Get artist snapshot from N days ago"""
        target_date = datetime.utcnow() - timedelta(days=days_ago)
        
        # Find closest snapshot to target date
        stmt = select(ArtistSnapshot).where(
            and_(
                ArtistSnapshot.artist_id == artist_id,
                ArtistSnapshot.snapshot_date <= target_date
            )
        ).order_by(desc(ArtistSnapshot.snapshot_date)).limit(1)
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def calculate_velocity_scores(
        self,
        db: AsyncSession,
        artist: Artist,
        platform_metrics: Dict[str, int]
    ) -> Dict[str, float]:
        """Calculate 7/30/90-day velocity scores for an artist"""
        
        velocity_scores = {}
        
        for days in [7, 30, 90]:
            historical = await self.get_historical_snapshot(db, artist.id, days)
            
            if not historical:
                velocity_scores[f"velocity_{days}d"] = 0.0
                continue
            
            # Calculate velocity across multiple metrics
            platform_velocities = []
            
            # Spotify followers
            if platform_metrics.get("spotify_followers") and historical.spotify_followers:
                velocity = await self.calculate_growth_rate(
                    platform_metrics["spotify_followers"],
                    historical.spotify_followers,
                    days
                )
                platform_velocities.append(velocity)
            
            # Spotify monthly listeners  
            if platform_metrics.get("spotify_monthly_listeners") and historical.spotify_monthly_listeners:
                velocity = await self.calculate_growth_rate(
                    platform_metrics["spotify_monthly_listeners"],
                    historical.spotify_monthly_listeners,
                    days
                )
                platform_velocities.append(velocity * 2)  # Weight monthly listeners higher
            
            # YouTube subscribers
            if platform_metrics.get("youtube_subscribers") and historical.youtube_subscribers:
                velocity = await self.calculate_growth_rate(
                    platform_metrics["youtube_subscribers"],
                    historical.youtube_subscribers,
                    days
                )
                platform_velocities.append(velocity)
            
            # YouTube views
            if platform_metrics.get("youtube_views") and historical.youtube_views:
                velocity = await self.calculate_growth_rate(
                    platform_metrics["youtube_views"],
                    historical.youtube_views,
                    days
                )
                platform_velocities.append(velocity * 0.5)  # Weight views lower
            
            # Last.fm listeners
            if platform_metrics.get("lastfm_listeners") and historical.lastfm_listeners:
                velocity = await self.calculate_growth_rate(
                    platform_metrics["lastfm_listeners"],
                    historical.lastfm_listeners,
                    days
                )
                platform_velocities.append(velocity)
            
            # Calculate weighted average velocity
            if platform_velocities:
                velocity_scores[f"velocity_{days}d"] = sum(platform_velocities) / len(platform_velocities)
            else:
                velocity_scores[f"velocity_{days}d"] = 0.0
        
        return velocity_scores
    
    async def calculate_momentum_score(
        self,
        velocity_7d: float,
        velocity_30d: float,
        velocity_90d: float,
        cross_platform_correlation: float = 1.0
    ) -> float:
        """Calculate composite momentum score from velocity metrics"""
        
        # Weight recent velocity higher than long-term
        momentum = (
            velocity_7d * 0.5 +      # 50% weight on 7-day velocity
            velocity_30d * 0.3 +     # 30% weight on 30-day velocity  
            velocity_90d * 0.2       # 20% weight on 90-day velocity
        )
        
        # Apply cross-platform correlation multiplier
        momentum *= cross_platform_correlation
        
        # Normalize to 0-100 scale with logarithmic scaling for extreme values
        import math
        if momentum > 0:
            normalized = min(100, max(0, 50 + (math.log10(momentum + 1) * 10)))
        elif momentum < 0:
            normalized = max(0, min(50, 50 - (math.log10(abs(momentum) + 1) * 10)))
        else:
            normalized = 50
        
        return round(normalized, 2)


class CrossPlatformAnalyzer:
    """Analyze correlation and consistency across platforms"""
    
    @staticmethod
    async def calculate_platform_correlation(
        spotify_growth: float,
        youtube_growth: float,
        lastfm_growth: float
    ) -> float:
        """Calculate correlation coefficient between platform growth rates"""
        
        growth_rates = [rate for rate in [spotify_growth, youtube_growth, lastfm_growth] if rate is not None]
        
        if len(growth_rates) < 2:
            return 1.0  # Default to perfect correlation if insufficient data
        
        # Simple correlation: check if growth rates are in same direction
        positive_count = sum(1 for rate in growth_rates if rate > 0)
        negative_count = sum(1 for rate in growth_rates if rate < 0)
        
        if positive_count == len(growth_rates) or negative_count == len(growth_rates):
            return 1.0  # Perfect correlation - all platforms growing/declining together
        elif positive_count > 0 and negative_count > 0:
            return 0.5  # Mixed signals
        else:
            return 0.8  # Mostly consistent
    
    @staticmethod
    async def detect_geographic_anomalies(
        geographic_data: Dict[str, Any]
    ) -> bool:
        """Detect suspicious geographic concentration patterns"""
        
        if not geographic_data:
            return False
        
        # Check for over-concentration in single country (potential bot farms)
        total_listeners = sum(geographic_data.values())
        if total_listeners == 0:
            return False
        
        max_country_percentage = max(geographic_data.values()) / total_listeners
        
        # Flag if >80% of listeners from single country (excluding major markets)
        major_markets = ["US", "GB", "CA", "AU", "DE", "FR", "JP", "KR"]
        top_country = max(geographic_data, key=geographic_data.get)
        
        if max_country_percentage > 0.8 and top_country not in major_markets:
            return True
        
        return False


# Global instances
velocity_engine = VelocityEngine()
cross_platform_analyzer = CrossPlatformAnalyzer()