import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.models import Artist, ArtistMetric, SongMetric, DailyScore
import logging

logger = logging.getLogger(__name__)

class MomentumAnalyzer:
    def __init__(self, db: Session):
        self.db = db
        
    def calculate_velocity_score(self, artist_id: int, days: int = 30) -> Dict:
        """
        Calculate artist momentum based on growth velocity across platforms
        Returns score 0-100 with breakdown by platform
        """
        try:
            # Get recent metrics for the artist
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Query artist metrics over the specified period
            query = text("""
                SELECT 
                    platform,
                    metric_type,
                    time,
                    value
                FROM artist_metrics 
                WHERE artist_id = :artist_id 
                  AND time >= :start_date 
                  AND time <= :end_date
                ORDER BY platform, metric_type, time
            """)
            
            results = self.db.execute(
                query, 
                {"artist_id": artist_id, "start_date": start_date, "end_date": end_date}
            ).fetchall()
            
            if not results:
                return {"overall_score": 0, "reason": "insufficient_data", "platform_scores": {}}
            
            # Group by platform and metric type
            metrics_data = {}
            for row in results:
                key = f"{row.platform}_{row.metric_type}"
                if key not in metrics_data:
                    metrics_data[key] = []
                metrics_data[key].append({"time": row.time, "value": row.value})
            
            # Calculate growth rates for each metric
            platform_scores = {}
            growth_rates = {}
            
            for metric_key, data_points in metrics_data.items():
                if len(data_points) < 2:
                    continue
                    
                # Sort by time
                data_points.sort(key=lambda x: x["time"])
                
                # Calculate overall growth rate
                start_value = data_points[0]["value"]
                end_value = data_points[-1]["value"]
                
                if start_value > 0:
                    growth_rate = ((end_value - start_value) / start_value) * 100
                else:
                    growth_rate = 0 if end_value == 0 else 100
                    
                growth_rates[metric_key] = growth_rate
                
                # Calculate acceleration (growth of growth)
                acceleration = self._calculate_acceleration(data_points)
                
                # Combine growth rate and acceleration for score
                platform_scores[metric_key] = {
                    "growth_rate": growth_rate,
                    "acceleration": acceleration,
                    "score": min(100, max(0, growth_rate * 2 + acceleration * 10))
                }
            
            # Weight different platform metrics
            weights = {
                "spotify_followers": 0.25,
                "spotify_popularity": 0.20,
                "youtube_subscribers": 0.20,
                "youtube_view_count": 0.15,
                "instagram_followers": 0.10,
                "tiktok_followers": 0.10
            }
            
            # Calculate weighted overall score
            weighted_score = 0
            total_weight = 0
            
            for metric_key, weight in weights.items():
                if metric_key in platform_scores:
                    weighted_score += platform_scores[metric_key]["score"] * weight
                    total_weight += weight
            
            overall_score = weighted_score / total_weight if total_weight > 0 else 0
            
            return {
                "overall_score": round(overall_score, 2),
                "platform_scores": platform_scores,
                "growth_rates": growth_rates,
                "calculation_period_days": days,
                "data_points": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error calculating velocity score for artist {artist_id}: {e}")
            return {"overall_score": 0, "reason": "calculation_error", "platform_scores": {}}
    
    def _calculate_acceleration(self, data_points: List[Dict]) -> float:
        """Calculate acceleration in growth (second derivative)"""
        if len(data_points) < 3:
            return 0
            
        # Calculate growth rates between consecutive points
        growth_rates = []
        for i in range(1, len(data_points)):
            prev_val = data_points[i-1]["value"]
            curr_val = data_points[i]["value"]
            
            if prev_val > 0:
                growth_rate = ((curr_val - prev_val) / prev_val) * 100
            else:
                growth_rate = 0 if curr_val == 0 else 100
                
            growth_rates.append(growth_rate)
        
        # Calculate acceleration (change in growth rate)
        if len(growth_rates) < 2:
            return 0
            
        recent_growth = np.mean(growth_rates[-3:]) if len(growth_rates) >= 3 else growth_rates[-1]
        earlier_growth = np.mean(growth_rates[:3]) if len(growth_rates) >= 3 else growth_rates[0]
        
        acceleration = recent_growth - earlier_growth
        return acceleration
    
    def calculate_breakout_probability(self, artist_id: int) -> float:
        """
        Calculate probability of artist having significant growth in next 90 days
        Based on pattern matching with historical successful breakouts
        """
        try:
            # Get current velocity metrics
            velocity_data = self.calculate_velocity_score(artist_id, days=30)
            
            if velocity_data["overall_score"] == 0:
                return 0.0
            
            # Get cross-platform correlation
            correlation_score = self._calculate_platform_correlation(artist_id)
            
            # Get consistency score (regular growth vs. spiky)
            consistency_score = self._calculate_consistency_score(artist_id)
            
            # Simple probability model (can be enhanced with ML later)
            factors = {
                "velocity": velocity_data["overall_score"] / 100,
                "correlation": correlation_score,
                "consistency": consistency_score,
            }
            
            # Weighted probability calculation
            weights = {"velocity": 0.5, "correlation": 0.3, "consistency": 0.2}
            
            probability = sum(factors[key] * weights[key] for key in factors)
            
            # Apply sigmoid-like curve to normalize between 0-1
            probability = 1 / (1 + np.exp(-5 * (probability - 0.5)))
            
            return round(probability, 3)
            
        except Exception as e:
            logger.error(f"Error calculating breakout probability for artist {artist_id}: {e}")
            return 0.0
    
    def _calculate_platform_correlation(self, artist_id: int) -> float:
        """Calculate how well growth correlates across platforms"""
        try:
            query = text("""
                SELECT 
                    platform,
                    metric_type,
                    time::date as date,
                    AVG(value) as daily_avg
                FROM artist_metrics 
                WHERE artist_id = :artist_id 
                  AND time >= NOW() - INTERVAL '30 days'
                  AND metric_type IN ('followers', 'subscribers', 'popularity')
                GROUP BY platform, metric_type, time::date
                ORDER BY platform, metric_type, date
            """)
            
            results = self.db.execute(query, {"artist_id": artist_id}).fetchall()
            
            if len(results) < 4:  # Need at least 2 platforms with 2 data points each
                return 0.5  # Default moderate correlation
            
            # Convert to pandas for correlation analysis
            df = pd.DataFrame(results)
            
            # Pivot to get platforms as columns
            pivot_df = df.pivot_table(
                index='date', 
                columns=['platform', 'metric_type'], 
                values='daily_avg', 
                fill_method='ffill'
            )
            
            if pivot_df.empty or pivot_df.shape[1] < 2:
                return 0.5
            
            # Calculate correlation matrix and get mean correlation
            corr_matrix = pivot_df.corr()
            
            # Get upper triangle of correlation matrix (excluding diagonal)
            upper_triangle = np.triu(corr_matrix.values, k=1)
            correlations = upper_triangle[upper_triangle != 0]
            
            if len(correlations) == 0:
                return 0.5
            
            mean_correlation = np.mean(np.abs(correlations))  # Use absolute correlation
            return min(1.0, max(0.0, mean_correlation))
            
        except Exception as e:
            logger.error(f"Error calculating platform correlation for artist {artist_id}: {e}")
            return 0.5
    
    def _calculate_consistency_score(self, artist_id: int) -> float:
        """Calculate how consistent the growth pattern is (vs spiky/irregular)"""
        try:
            query = text("""
                SELECT 
                    time,
                    SUM(value) as total_metric_value
                FROM artist_metrics 
                WHERE artist_id = :artist_id 
                  AND time >= NOW() - INTERVAL '30 days'
                  AND metric_type IN ('followers', 'subscribers')
                GROUP BY time
                ORDER BY time
            """)
            
            results = self.db.execute(query, {"artist_id": artist_id}).fetchall()
            
            if len(results) < 5:
                return 0.5  # Default score for insufficient data
            
            values = [r.total_metric_value for r in results]
            
            # Calculate coefficient of variation (lower = more consistent)
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            if mean_val == 0:
                return 0.0
            
            cv = std_val / mean_val
            
            # Convert to consistency score (0-1, higher = more consistent)
            consistency_score = 1 / (1 + cv)
            
            return consistency_score
            
        except Exception as e:
            logger.error(f"Error calculating consistency score for artist {artist_id}: {e}")
            return 0.5
    
    def generate_momentum_insights(self, artist_id: int) -> Dict:
        """Generate detailed momentum analysis and insights"""
        velocity_data = self.calculate_velocity_score(artist_id)
        breakout_prob = self.calculate_breakout_probability(artist_id)
        
        # Determine urgency level
        if velocity_data["overall_score"] >= 80 and breakout_prob >= 0.7:
            urgency = "high"
        elif velocity_data["overall_score"] >= 60 and breakout_prob >= 0.4:
            urgency = "medium"
        else:
            urgency = "low"
        
        # Generate insights
        insights = []
        
        if velocity_data["overall_score"] > 70:
            insights.append("Strong momentum detected across multiple platforms")
        
        if breakout_prob > 0.6:
            insights.append("High probability of significant growth in next 90 days")
        
        platform_scores = velocity_data.get("platform_scores", {})
        top_platform = max(platform_scores.keys(), key=lambda k: platform_scores[k]["score"]) if platform_scores else None
        
        if top_platform:
            insights.append(f"Strongest growth on {top_platform.replace('_', ' ')}")
        
        return {
            "velocity_score": velocity_data["overall_score"],
            "breakout_probability": breakout_prob,
            "urgency_level": urgency,
            "insights": insights,
            "platform_breakdown": platform_scores,
            "recommendation": self._generate_recommendation(velocity_data["overall_score"], breakout_prob, urgency)
        }
    
    def _generate_recommendation(self, velocity_score: float, breakout_prob: float, urgency: str) -> str:
        """Generate action recommendation based on momentum analysis"""
        if velocity_score >= 80 and breakout_prob >= 0.7:
            return "IMMEDIATE ACTION: Contact artist/management within 48 hours"
        elif velocity_score >= 70 and breakout_prob >= 0.5:
            return "HIGH PRIORITY: Initiate contact within 1 week"
        elif velocity_score >= 60 and breakout_prob >= 0.3:
            return "MONITOR CLOSELY: Watch for 2-4 weeks, reassess momentum"
        elif velocity_score >= 40:
            return "WATCH LIST: Monthly monitoring, may develop into opportunity"
        else:
            return "LOW PRIORITY: Quarterly check-in sufficient"