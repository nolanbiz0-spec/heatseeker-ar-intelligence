from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, desc
from app.models.models import Artist, DailyScore, ArtistMetric, IntelligenceReport
from app.analysis.momentum_analyzer import MomentumAnalyzer
from app.analysis.authenticity_detector import AuthenticityDetector
import logging

logger = logging.getLogger(__name__)

class IntelligenceReporter:
    def __init__(self, db: Session):
        self.db = db
        self.momentum_analyzer = MomentumAnalyzer(db)
        self.authenticity_detector = AuthenticityDetector(db)
    
    def generate_daily_brief(self, target_date: date = None) -> Dict:
        """Generate comprehensive daily A&R intelligence brief"""
        if not target_date:
            target_date = date.today()
        
        try:
            logger.info(f"Generating daily brief for {target_date}")
            
            brief = {
                "date": target_date.isoformat(),
                "generated_at": datetime.utcnow().isoformat(),
                "top_artists_to_watch": self._get_top_velocity_artists(target_date, limit=10),
                "biggest_risers": self._get_biggest_risers(target_date, limit=5),
                "urgent_outreach_targets": self._get_urgent_opportunities(target_date, limit=3),
                "red_flag_alerts": self._get_authenticity_alerts(target_date, limit=5),
                "market_insights": self._get_market_trends(target_date),
                "summary_stats": self._get_summary_statistics(target_date)
            }
            
            # Store the brief in the database
            self._store_intelligence_report("daily_brief", None, brief)
            
            return brief
            
        except Exception as e:
            logger.error(f"Error generating daily brief: {e}")
            return {
                "date": target_date.isoformat(),
                "error": "Failed to generate daily brief",
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def _get_top_velocity_artists(self, target_date: date, limit: int = 10) -> List[Dict]:
        """Get artists with highest momentum scores"""
        try:
            query = text("""
                SELECT 
                    a.id,
                    a.name,
                    a.location,
                    a.genres,
                    a.independence_status,
                    ds.momentum_score,
                    ds.breakout_probability,
                    ds.urgency_level,
                    ds.overall_score
                FROM daily_scores ds
                JOIN artists a ON ds.artist_id = a.id
                WHERE ds.date = :target_date
                  AND ds.momentum_score >= 60
                  AND a.independence_status IN ('unsigned', 'indie_dist', 'unknown')
                ORDER BY ds.momentum_score DESC, ds.breakout_probability DESC
                LIMIT :limit
            """)
            
            results = self.db.execute(
                query, 
                {"target_date": target_date, "limit": limit}
            ).fetchall()
            
            artists = []
            for row in results:
                # Get recent momentum insights
                momentum_data = self.momentum_analyzer.generate_momentum_insights(row.id)
                
                artists.append({
                    "artist_id": row.id,
                    "name": row.name,
                    "location": row.location,
                    "primary_genre": row.genres[0] if row.genres else "Unknown",
                    "independence_status": row.independence_status,
                    "momentum_score": row.momentum_score,
                    "breakout_probability": float(row.breakout_probability) if row.breakout_probability else 0,
                    "urgency_level": row.urgency_level,
                    "overall_score": row.overall_score,
                    "key_insights": momentum_data.get("insights", [])[:2],  # Top 2 insights
                    "recommendation": momentum_data.get("recommendation", "Monitor")
                })
            
            return artists
            
        except Exception as e:
            logger.error(f"Error getting top velocity artists: {e}")
            return []
    
    def _get_biggest_risers(self, target_date: date, limit: int = 5) -> List[Dict]:
        """Get artists with biggest momentum increase in last 24-48 hours"""
        try:
            yesterday = target_date - timedelta(days=1)
            
            query = text("""
                SELECT 
                    a.id,
                    a.name,
                    a.location,
                    a.genres,
                    ds_today.momentum_score as today_score,
                    ds_yesterday.momentum_score as yesterday_score,
                    (ds_today.momentum_score - COALESCE(ds_yesterday.momentum_score, 0)) as score_change,
                    ds_today.urgency_level
                FROM daily_scores ds_today
                JOIN artists a ON ds_today.artist_id = a.id
                LEFT JOIN daily_scores ds_yesterday ON (
                    ds_yesterday.artist_id = ds_today.artist_id 
                    AND ds_yesterday.date = :yesterday
                )
                WHERE ds_today.date = :target_date
                  AND (ds_today.momentum_score - COALESCE(ds_yesterday.momentum_score, 0)) >= 15
                  AND a.independence_status IN ('unsigned', 'indie_dist', 'unknown')
                ORDER BY score_change DESC
                LIMIT :limit
            """)
            
            results = self.db.execute(
                query, 
                {"target_date": target_date, "yesterday": yesterday, "limit": limit}
            ).fetchall()
            
            risers = []
            for row in results:
                # Get recent velocity data to understand what's driving the rise
                velocity_data = self.momentum_analyzer.calculate_velocity_score(row.id, days=7)
                
                risers.append({
                    "artist_id": row.id,
                    "name": row.name,
                    "location": row.location,
                    "primary_genre": row.genres[0] if row.genres else "Unknown",
                    "score_change": row.score_change,
                    "current_score": row.today_score,
                    "previous_score": row.yesterday_score or 0,
                    "urgency_level": row.urgency_level,
                    "top_platform": self._identify_top_growth_platform(velocity_data)
                })
            
            return risers
            
        except Exception as e:
            logger.error(f"Error getting biggest risers: {e}")
            return []
    
    def _get_urgent_opportunities(self, target_date: date, limit: int = 3) -> List[Dict]:
        """Get artists requiring immediate action"""
        try:
            query = text("""
                SELECT 
                    a.id,
                    a.name,
                    a.location,
                    a.genres,
                    a.independence_status,
                    ds.momentum_score,
                    ds.breakout_probability,
                    ds.urgency_level
                FROM daily_scores ds
                JOIN artists a ON ds.artist_id = a.id
                WHERE ds.date = :target_date
                  AND ds.urgency_level = 'high'
                  AND ds.momentum_score >= 75
                  AND a.independence_status IN ('unsigned', 'unknown')
                ORDER BY ds.breakout_probability DESC, ds.momentum_score DESC
                LIMIT :limit
            """)
            
            results = self.db.execute(
                query, 
                {"target_date": target_date, "limit": limit}
            ).fetchall()
            
            urgent_targets = []
            for row in results:
                momentum_insights = self.momentum_analyzer.generate_momentum_insights(row.id)
                
                urgent_targets.append({
                    "artist_id": row.id,
                    "name": row.name,
                    "location": row.location,
                    "primary_genre": row.genres[0] if row.genres else "Unknown",
                    "momentum_score": row.momentum_score,
                    "breakout_probability": float(row.breakout_probability) if row.breakout_probability else 0,
                    "independence_status": row.independence_status,
                    "action_required": "Contact within 48 hours",
                    "contact_method": "Direct artist outreach" if row.independence_status == "unsigned" else "Management contact",
                    "reason": momentum_insights.get("insights", ["High momentum detected"])[0]
                })
            
            return urgent_targets
            
        except Exception as e:
            logger.error(f"Error getting urgent opportunities: {e}")
            return []
    
    def _get_authenticity_alerts(self, target_date: date, limit: int = 5) -> List[Dict]:
        """Get artists with authenticity red flags"""
        try:
            # Get recent authenticity signals
            query = text("""
                SELECT 
                    a.id,
                    a.name,
                    a.location,
                    auths.signal_type,
                    auths.value,
                    auths.confidence,
                    auths.details,
                    auths.detected_at
                FROM authenticity_signals auths
                JOIN artists a ON auths.artist_id = a.id
                WHERE auths.detected_at >= :start_date
                  AND auths.signal_type = 'overall_authenticity'
                  AND auths.value <= 40  -- Low authenticity scores
                ORDER BY auths.detected_at DESC, auths.value ASC
                LIMIT :limit
            """)
            
            start_date = target_date - timedelta(days=1)
            
            results = self.db.execute(
                query, 
                {"start_date": start_date, "limit": limit}
            ).fetchall()
            
            alerts = []
            for row in results:
                details = row.details if isinstance(row.details, dict) else {}
                red_flags = details.get("red_flags", {})
                
                # Identify primary concern
                primary_concern = "Unknown"
                max_severity = 0
                for flag_type, flag_data in red_flags.items():
                    if isinstance(flag_data, dict) and flag_data.get("severity", 0) > max_severity:
                        max_severity = flag_data["severity"]
                        primary_concern = flag_type.replace("_", " ").title()
                
                alerts.append({
                    "artist_id": row.id,
                    "name": row.name,
                    "location": row.location,
                    "authenticity_score": row.value,
                    "risk_level": details.get("risk_level", "unknown"),
                    "primary_concern": primary_concern,
                    "detected_at": row.detected_at.strftime("%Y-%m-%d %H:%M"),
                    "action_required": "Investigate before pursuing" if row.value < 30 else "Monitor closely"
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting authenticity alerts: {e}")
            return []
    
    def _get_market_trends(self, target_date: date) -> Dict:
        """Analyze overall market trends and patterns"""
        try:
            # Get genre distribution of high-momentum artists
            query = text("""
                SELECT 
                    a.genres[1] as primary_genre,
                    COUNT(*) as artist_count,
                    AVG(ds.momentum_score) as avg_momentum
                FROM daily_scores ds
                JOIN artists a ON ds.artist_id = a.id
                WHERE ds.date = :target_date
                  AND ds.momentum_score >= 60
                  AND a.genres IS NOT NULL
                  AND array_length(a.genres, 1) > 0
                GROUP BY a.genres[1]
                HAVING COUNT(*) >= 2
                ORDER BY artist_count DESC, avg_momentum DESC
                LIMIT 10
            """)
            
            genre_results = self.db.execute(query, {"target_date": target_date}).fetchall()
            
            # Get location trends
            location_query = text("""
                SELECT 
                    a.location,
                    COUNT(*) as artist_count,
                    AVG(ds.momentum_score) as avg_momentum
                FROM daily_scores ds
                JOIN artists a ON ds.artist_id = a.id
                WHERE ds.date = :target_date
                  AND ds.momentum_score >= 60
                  AND a.location IS NOT NULL
                GROUP BY a.location
                HAVING COUNT(*) >= 2
                ORDER BY artist_count DESC, avg_momentum DESC
                LIMIT 10
            """)
            
            location_results = self.db.execute(location_query, {"target_date": target_date}).fetchall()
            
            return {
                "hot_genres": [
                    {
                        "genre": row.primary_genre,
                        "artist_count": row.artist_count,
                        "avg_momentum": round(row.avg_momentum, 1)
                    }
                    for row in genre_results
                ],
                "emerging_scenes": [
                    {
                        "location": row.location,
                        "artist_count": row.artist_count,
                        "avg_momentum": round(row.avg_momentum, 1)
                    }
                    for row in location_results
                ],
                "total_tracked_artists": self._get_total_tracked_count(),
                "high_momentum_count": len([r for r in genre_results])  # Artists with 60+ momentum
            }
            
        except Exception as e:
            logger.error(f"Error getting market trends: {e}")
            return {}
    
    def _get_summary_statistics(self, target_date: date) -> Dict:
        """Get summary statistics for the day"""
        try:
            query = text("""
                SELECT 
                    COUNT(*) as total_artists,
                    COUNT(CASE WHEN ds.momentum_score >= 80 THEN 1 END) as high_momentum,
                    COUNT(CASE WHEN ds.momentum_score >= 60 THEN 1 END) as medium_momentum,
                    COUNT(CASE WHEN ds.urgency_level = 'high' THEN 1 END) as urgent_targets,
                    AVG(ds.momentum_score) as avg_momentum_score,
                    AVG(ds.breakout_probability) as avg_breakout_prob
                FROM daily_scores ds
                WHERE ds.date = :target_date
            """)
            
            result = self.db.execute(query, {"target_date": target_date}).fetchone()
            
            if not result:
                return {}
            
            return {
                "total_artists_tracked": result.total_artists or 0,
                "high_momentum_artists": result.high_momentum or 0,
                "medium_momentum_artists": result.medium_momentum or 0,
                "urgent_targets": result.urgent_targets or 0,
                "average_momentum_score": round(result.avg_momentum_score or 0, 1),
                "average_breakout_probability": round(float(result.avg_breakout_prob or 0), 3)
            }
            
        except Exception as e:
            logger.error(f"Error getting summary statistics: {e}")
            return {}
    
    def generate_artist_deep_dive(self, artist_id: int) -> Dict:
        """Generate comprehensive intelligence report for a specific artist"""
        try:
            # Get basic artist info
            artist = self.db.query(Artist).filter(Artist.id == artist_id).first()
            if not artist:
                return {"error": "Artist not found"}
            
            # Get momentum analysis
            momentum_data = self.momentum_analyzer.generate_momentum_insights(artist_id)
            
            # Get authenticity analysis
            authenticity_data = self.authenticity_detector.analyze_artist_authenticity(artist_id)
            
            # Get recent metrics for platform breakdown
            platform_metrics = self._get_platform_breakdown(artist_id)
            
            # Get independence status assessment
            independence_data = self._assess_independence_status(artist_id)
            
            report = {
                "artist": {
                    "id": artist.id,
                    "name": artist.name,
                    "location": artist.location,
                    "genres": artist.genres or [],
                    "independence_status": artist.independence_status,
                    "discovery_date": artist.discovery_date.isoformat() if artist.discovery_date else None,
                    "spotify_id": artist.spotify_id,
                    "youtube_id": artist.youtube_id
                },
                "momentum_analysis": momentum_data,
                "authenticity_analysis": authenticity_data,
                "platform_breakdown": platform_metrics,
                "independence_assessment": independence_data,
                "commercial_intelligence": self._assess_commercial_potential(artist_id, momentum_data),
                "recommended_action": self._generate_action_recommendation(momentum_data, authenticity_data, independence_data),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Store the deep dive report
            self._store_intelligence_report("deep_dive", artist_id, report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating deep dive for artist {artist_id}: {e}")
            return {"error": f"Failed to generate deep dive report: {str(e)}"}
    
    def _identify_top_growth_platform(self, velocity_data: Dict) -> str:
        """Identify which platform is driving the most growth"""
        platform_scores = velocity_data.get("platform_scores", {})
        if not platform_scores:
            return "Unknown"
        
        top_platform = max(platform_scores.keys(), key=lambda k: platform_scores[k].get("score", 0))
        return top_platform.replace("_", " ").title()
    
    def _get_total_tracked_count(self) -> int:
        """Get total number of artists being tracked"""
        try:
            return self.db.query(Artist).count()
        except Exception:
            return 0
    
    def _get_platform_breakdown(self, artist_id: int) -> Dict:
        """Get recent performance across all platforms"""
        try:
            query = text("""
                SELECT 
                    platform,
                    metric_type,
                    value,
                    time
                FROM artist_metrics 
                WHERE artist_id = :artist_id 
                  AND time >= NOW() - INTERVAL '7 days'
                ORDER BY platform, metric_type, time DESC
            """)
            
            results = self.db.execute(query, {"artist_id": artist_id}).fetchall()
            
            platform_data = {}
            for row in results:
                platform = row.platform
                if platform not in platform_data:
                    platform_data[platform] = {}
                
                # Get most recent value for each metric type
                if row.metric_type not in platform_data[platform]:
                    platform_data[platform][row.metric_type] = {
                        "current_value": row.value,
                        "last_updated": row.time.isoformat()
                    }
            
            return platform_data
            
        except Exception as e:
            logger.error(f"Error getting platform breakdown: {e}")
            return {}
    
    def _assess_independence_status(self, artist_id: int) -> Dict:
        """Assess artist's current independence and signability"""
        try:
            artist = self.db.query(Artist).filter(Artist.id == artist_id).first()
            
            # This is a simplified assessment - would be enhanced with more data sources
            status_assessment = {
                "current_status": artist.independence_status if artist else "unknown",
                "signability": "unknown",
                "estimated_team_presence": "minimal",
                "deal_window": "unknown"
            }
            
            if artist and artist.independence_status == "unsigned":
                status_assessment.update({
                    "signability": "high",
                    "estimated_team_presence": "minimal",
                    "deal_window": "wide_open"
                })
            elif artist and artist.independence_status == "indie_dist":
                status_assessment.update({
                    "signability": "medium",
                    "estimated_team_presence": "basic",
                    "deal_window": "competitive"
                })
            
            return status_assessment
            
        except Exception as e:
            logger.error(f"Error assessing independence status: {e}")
            return {}
    
    def _assess_commercial_potential(self, artist_id: int, momentum_data: Dict) -> Dict:
        """Assess commercial revenue potential"""
        try:
            velocity_score = momentum_data.get("velocity_score", 0)
            breakout_prob = momentum_data.get("breakout_probability", 0)
            
            # Simple revenue projection model
            if velocity_score >= 80 and breakout_prob >= 0.7:
                revenue_tier = "high"
                year_1_projection = "$200K-500K"
            elif velocity_score >= 60 and breakout_prob >= 0.4:
                revenue_tier = "medium"
                year_1_projection = "$100K-300K"
            else:
                revenue_tier = "low"
                year_1_projection = "$50K-150K"
            
            return {
                "revenue_tier": revenue_tier,
                "year_1_projection": year_1_projection,
                "primary_revenue_streams": ["streaming", "live_performance", "merchandising"],
                "sync_potential": "medium",  # Would be enhanced with actual analysis
                "brand_partnership_potential": "medium"
            }
            
        except Exception as e:
            logger.error(f"Error assessing commercial potential: {e}")
            return {}
    
    def _generate_action_recommendation(self, momentum_data: Dict, authenticity_data: Dict, independence_data: Dict) -> Dict:
        """Generate specific action recommendation"""
        try:
            velocity_score = momentum_data.get("velocity_score", 0)
            authenticity_score = authenticity_data.get("authenticity_score", 50)
            urgency = momentum_data.get("urgency_level", "low")
            
            if authenticity_score < 40:
                return {
                    "action": "AVOID",
                    "reason": "Authenticity concerns detected",
                    "timeline": "Do not pursue"
                }
            
            if velocity_score >= 80 and urgency == "high":
                return {
                    "action": "IMMEDIATE_CONTACT",
                    "reason": "High momentum with breakout potential",
                    "timeline": "Contact within 24-48 hours",
                    "method": "Direct artist outreach"
                }
            elif velocity_score >= 60:
                return {
                    "action": "PRIORITY_CONTACT",
                    "reason": "Strong momentum detected",
                    "timeline": "Contact within 1 week",
                    "method": "Artist or management contact"
                }
            elif velocity_score >= 40:
                return {
                    "action": "MONITOR_CLOSELY",
                    "reason": "Moderate momentum, watch for acceleration",
                    "timeline": "Monitor for 2-4 weeks"
                }
            else:
                return {
                    "action": "WATCHLIST",
                    "reason": "Low momentum, periodic monitoring",
                    "timeline": "Monthly check-ins"
                }
                
        except Exception as e:
            logger.error(f"Error generating action recommendation: {e}")
            return {"action": "UNKNOWN", "reason": "Analysis error"}
    
    def _store_intelligence_report(self, report_type: str, artist_id: Optional[int], content: Dict):
        """Store intelligence report in database"""
        try:
            report = IntelligenceReport(
                artist_id=artist_id,
                report_type=report_type,
                content=content
            )
            self.db.add(report)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error storing intelligence report: {e}")
            self.db.rollback()