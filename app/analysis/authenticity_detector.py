import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.models import Artist, ArtistMetric, AuthenticitySignal
import logging

logger = logging.getLogger(__name__)

class AuthenticityDetector:
    def __init__(self, db: Session):
        self.db = db
        
        # Known suspicious regions for bot farms
        self.suspicious_regions = ["VN", "BD", "PK", "ID", "IN"]  # Vietnam, Bangladesh, Pakistan, Indonesia, India
        
        # Thresholds for various authenticity checks
        self.thresholds = {
            "geographic_clustering": 40,  # % threshold for suspicious regions
            "growth_spike": 300,  # % growth in single day that's suspicious
            "platform_divergence": 0.3,  # Correlation threshold below which platforms are divergent
            "engagement_ratio": 0.05,  # Minimum engagement rate expected
        }
    
    def analyze_artist_authenticity(self, artist_id: int) -> Dict:
        """
        Comprehensive authenticity analysis for an artist
        Returns overall authenticity score and detailed red flags
        """
        try:
            red_flags = {
                "geographic_clustering": self._check_geographic_clustering(artist_id),
                "velocity_anomalies": self._check_velocity_anomalies(artist_id),
                "platform_inconsistencies": self._check_platform_consistency(artist_id),
                "engagement_ratios": self._check_engagement_ratios(artist_id),
                "growth_patterns": self._check_growth_patterns(artist_id)
            }
            
            # Calculate overall risk score (0-100, higher = more suspicious)
            risk_weights = {
                "geographic_clustering": 0.25,
                "velocity_anomalies": 0.25,
                "platform_inconsistencies": 0.20,
                "engagement_ratios": 0.15,
                "growth_patterns": 0.15
            }
            
            total_risk = 0
            for flag_type, weight in risk_weights.items():
                flag_data = red_flags.get(flag_type, {})
                flag_severity = flag_data.get("severity", 0)
                total_risk += flag_severity * weight
            
            # Convert risk score to authenticity score (inverse)
            authenticity_score = max(0, 100 - total_risk)
            
            # Determine risk level
            if total_risk >= 70:
                risk_level = "high"
            elif total_risk >= 40:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Store authenticity signal in database
            self._store_authenticity_signal(
                artist_id, 
                "overall_authenticity", 
                authenticity_score, 
                0.85,  # confidence
                {"red_flags": red_flags, "risk_level": risk_level}
            )
            
            return {
                "authenticity_score": round(authenticity_score, 2),
                "risk_level": risk_level,
                "total_risk_score": round(total_risk, 2),
                "red_flags": red_flags,
                "summary": self._generate_authenticity_summary(authenticity_score, red_flags)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing authenticity for artist {artist_id}: {e}")
            return {
                "authenticity_score": 50,
                "risk_level": "unknown",
                "red_flags": {},
                "summary": "Error during analysis"
            }
    
    def _check_geographic_clustering(self, artist_id: int) -> Dict:
        """Check for suspicious geographic concentration of activity"""
        try:
            # Note: This would require geographic data from streaming platforms
            # For now, return a placeholder that can be enhanced when geo data is available
            
            # Simulate geographic analysis based on growth patterns
            query = text("""
                SELECT 
                    platform,
                    metric_type,
                    time,
                    value
                FROM artist_metrics 
                WHERE artist_id = :artist_id 
                  AND time >= NOW() - INTERVAL '30 days'
                ORDER BY time DESC
                LIMIT 100
            """)
            
            results = self.db.execute(query, {"artist_id": artist_id}).fetchall()
            
            if not results:
                return {"severity": 0, "details": "No data available for geographic analysis"}
            
            # Look for patterns that suggest bot activity (placeholder logic)
            suspicious_patterns = 0
            
            # Check for sudden spikes without corresponding organic indicators
            values_by_platform = {}
            for row in results:
                platform = row.platform
                if platform not in values_by_platform:
                    values_by_platform[platform] = []
                values_by_platform[platform].append(row.value)
            
            for platform, values in values_by_platform.items():
                if len(values) > 1:
                    # Check for sudden large increases
                    max_increase = max(
                        (values[i] - values[i+1]) / max(values[i+1], 1) * 100 
                        for i in range(len(values) - 1)
                    )
                    
                    if max_increase > self.thresholds["growth_spike"]:
                        suspicious_patterns += 1
            
            severity = min(100, suspicious_patterns * 30)
            
            return {
                "severity": severity,
                "details": f"Detected {suspicious_patterns} suspicious growth patterns",
                "confidence": 0.6  # Lower confidence without actual geo data
            }
            
        except Exception as e:
            logger.error(f"Error checking geographic clustering for artist {artist_id}: {e}")
            return {"severity": 0, "details": "Error in geographic analysis"}
    
    def _check_velocity_anomalies(self, artist_id: int) -> Dict:
        """Check for unnatural velocity spikes that suggest manipulation"""
        try:
            query = text("""
                SELECT 
                    platform,
                    metric_type,
                    time,
                    value,
                    LAG(value) OVER (PARTITION BY platform, metric_type ORDER BY time) as prev_value,
                    LAG(time) OVER (PARTITION BY platform, metric_type ORDER BY time) as prev_time
                FROM artist_metrics 
                WHERE artist_id = :artist_id 
                  AND time >= NOW() - INTERVAL '60 days'
                ORDER BY platform, metric_type, time
            """)
            
            results = self.db.execute(query, {"artist_id": artist_id}).fetchall()
            
            if not results:
                return {"severity": 0, "details": "No data available for velocity analysis"}
            
            anomaly_count = 0
            total_comparisons = 0
            suspicious_spikes = []
            
            for row in results:
                if row.prev_value is not None and row.prev_value > 0:
                    total_comparisons += 1
                    
                    # Calculate growth rate
                    growth_rate = ((row.value - row.prev_value) / row.prev_value) * 100
                    
                    # Check for suspicious spikes
                    if growth_rate > self.thresholds["growth_spike"]:
                        anomaly_count += 1
                        suspicious_spikes.append({
                            "platform": row.platform,
                            "metric": row.metric_type,
                            "growth_rate": round(growth_rate, 2),
                            "date": row.time.strftime("%Y-%m-%d")
                        })
            
            if total_comparisons == 0:
                return {"severity": 0, "details": "Insufficient data for velocity analysis"}
            
            anomaly_rate = (anomaly_count / total_comparisons) * 100
            severity = min(100, anomaly_rate * 2)  # Scale to 0-100
            
            return {
                "severity": severity,
                "details": f"Found {anomaly_count} suspicious velocity spikes out of {total_comparisons} data points",
                "suspicious_spikes": suspicious_spikes,
                "anomaly_rate": round(anomaly_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error checking velocity anomalies for artist {artist_id}: {e}")
            return {"severity": 0, "details": "Error in velocity analysis"}
    
    def _check_platform_consistency(self, artist_id: int) -> Dict:
        """Check if growth patterns are consistent across platforms"""
        try:
            query = text("""
                SELECT 
                    platform,
                    metric_type,
                    DATE(time) as date,
                    AVG(value) as daily_avg
                FROM artist_metrics 
                WHERE artist_id = :artist_id 
                  AND time >= NOW() - INTERVAL '30 days'
                  AND metric_type IN ('followers', 'subscribers', 'popularity')
                GROUP BY platform, metric_type, DATE(time)
                HAVING COUNT(*) > 0
                ORDER BY platform, metric_type, date
            """)
            
            results = self.db.execute(query, {"artist_id": artist_id}).fetchall()
            
            if len(results) < 6:  # Need at least 3 platforms with 2 data points each
                return {"severity": 0, "details": "Insufficient cross-platform data"}
            
            # Group by platform for correlation analysis
            platform_data = {}
            for row in results:
                platform_key = f"{row.platform}_{row.metric_type}"
                if platform_key not in platform_data:
                    platform_data[platform_key] = []
                platform_data[platform_key].append({"date": row.date, "value": row.daily_avg})
            
            # Calculate correlations between platforms
            correlations = []
            platforms = list(platform_data.keys())
            
            for i in range(len(platforms)):
                for j in range(i + 1, len(platforms)):
                    platform1_data = platform_data[platforms[i]]
                    platform2_data = platform_data[platforms[j]]
                    
                    # Align dates and calculate correlation
                    correlation = self._calculate_platform_correlation(platform1_data, platform2_data)
                    if correlation is not None:
                        correlations.append(correlation)
            
            if not correlations:
                return {"severity": 0, "details": "Could not calculate platform correlations"}
            
            avg_correlation = np.mean(correlations)
            
            # Low correlation suggests inconsistent (potentially manipulated) growth
            if avg_correlation < self.thresholds["platform_divergence"]:
                severity = (self.thresholds["platform_divergence"] - avg_correlation) * 200
            else:
                severity = 0
            
            severity = min(100, severity)
            
            return {
                "severity": severity,
                "details": f"Average cross-platform correlation: {avg_correlation:.3f}",
                "correlations": correlations,
                "platform_count": len(platforms)
            }
            
        except Exception as e:
            logger.error(f"Error checking platform consistency for artist {artist_id}: {e}")
            return {"severity": 0, "details": "Error in platform consistency analysis"}
    
    def _calculate_platform_correlation(self, data1: List[Dict], data2: List[Dict]) -> Optional[float]:
        """Calculate correlation between two platform datasets"""
        try:
            # Create aligned datasets by date
            dates1 = {item["date"]: item["value"] for item in data1}
            dates2 = {item["date"]: item["value"] for item in data2}
            
            common_dates = set(dates1.keys()) & set(dates2.keys())
            
            if len(common_dates) < 3:  # Need at least 3 data points
                return None
            
            values1 = [dates1[date] for date in sorted(common_dates)]
            values2 = [dates2[date] for date in sorted(common_dates)]
            
            # Calculate Pearson correlation
            correlation_matrix = np.corrcoef(values1, values2)
            return correlation_matrix[0, 1] if not np.isnan(correlation_matrix[0, 1]) else None
            
        except Exception:
            return None
    
    def _check_engagement_ratios(self, artist_id: int) -> Dict:
        """Check for healthy engagement ratios (would need engagement data)"""
        try:
            # Placeholder for engagement ratio analysis
            # In a real implementation, this would analyze:
            # - Save rate vs play rate on Spotify
            # - Like/comment rate vs views on YouTube
            # - Organic shares vs follows on social platforms
            
            # For now, return low severity as we don't have engagement data
            return {
                "severity": 10,  # Low severity placeholder
                "details": "Limited engagement data available for analysis",
                "note": "Full engagement analysis requires additional API access"
            }
            
        except Exception as e:
            logger.error(f"Error checking engagement ratios for artist {artist_id}: {e}")
            return {"severity": 0, "details": "Error in engagement analysis"}
    
    def _check_growth_patterns(self, artist_id: int) -> Dict:
        """Check for natural vs artificial growth patterns"""
        try:
            query = text("""
                SELECT 
                    platform,
                    metric_type,
                    time,
                    value
                FROM artist_metrics 
                WHERE artist_id = :artist_id 
                  AND time >= NOW() - INTERVAL '90 days'
                ORDER BY platform, metric_type, time
            """)
            
            results = self.db.execute(query, {"artist_id": artist_id}).fetchall()
            
            if not results:
                return {"severity": 0, "details": "No data for growth pattern analysis"}
            
            # Group by platform and metric
            growth_patterns = {}
            for row in results:
                key = f"{row.platform}_{row.metric_type}"
                if key not in growth_patterns:
                    growth_patterns[key] = []
                growth_patterns[key].append({"time": row.time, "value": row.value})
            
            suspicious_patterns = 0
            total_patterns = len(growth_patterns)
            
            for key, data_points in growth_patterns.items():
                if len(data_points) < 5:  # Need sufficient data
                    continue
                
                # Sort by time
                data_points.sort(key=lambda x: x["time"])
                values = [point["value"] for point in data_points]
                
                # Check for artificial patterns
                if self._has_artificial_pattern(values):
                    suspicious_patterns += 1
            
            if total_patterns == 0:
                return {"severity": 0, "details": "Insufficient data for pattern analysis"}
            
            pattern_suspicion_rate = (suspicious_patterns / total_patterns) * 100
            severity = min(100, pattern_suspicion_rate * 1.5)
            
            return {
                "severity": severity,
                "details": f"{suspicious_patterns} out of {total_patterns} growth patterns appear artificial",
                "pattern_analysis": f"{pattern_suspicion_rate:.1f}% of patterns flagged as suspicious"
            }
            
        except Exception as e:
            logger.error(f"Error checking growth patterns for artist {artist_id}: {e}")
            return {"severity": 0, "details": "Error in growth pattern analysis"}
    
    def _has_artificial_pattern(self, values: List[int]) -> bool:
        """Detect artificial growth patterns in a series of values"""
        try:
            if len(values) < 5:
                return False
            
            # Check for perfectly linear growth (unlikely to be natural)
            differences = [values[i+1] - values[i] for i in range(len(values) - 1)]
            
            # If differences are too uniform, it's suspicious
            if len(set(differences)) <= 2 and len(differences) > 5:
                return True
            
            # Check for sudden plateau after growth (bot campaign ended)
            recent_values = values[-5:]
            if len(set(recent_values)) == 1 and values[-6] < recent_values[0]:
                return True
            
            # Check for exponential growth followed by sudden stop
            if len(values) >= 10:
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                first_growth = (first_half[-1] - first_half[0]) / len(first_half)
                second_growth = (second_half[-1] - second_half[0]) / len(second_half) if len(second_half) > 1 else 0
                
                # If growth rate drops to near zero suddenly, it's suspicious
                if first_growth > 100 and second_growth < 10:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _store_authenticity_signal(self, artist_id: int, signal_type: str, value: float, confidence: float, details: Dict):
        """Store authenticity signal in database"""
        try:
            signal = AuthenticitySignal(
                artist_id=artist_id,
                signal_type=signal_type,
                value=value,
                confidence=confidence,
                details=details
            )
            self.db.add(signal)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error storing authenticity signal: {e}")
            self.db.rollback()
    
    def _generate_authenticity_summary(self, score: float, red_flags: Dict) -> str:
        """Generate human-readable summary of authenticity analysis"""
        if score >= 85:
            summary = "High authenticity - Growth patterns appear organic and genuine"
        elif score >= 70:
            summary = "Good authenticity - Minor concerns but overall legitimate growth"
        elif score >= 50:
            summary = "Moderate concerns - Some red flags detected, investigate further"
        elif score >= 30:
            summary = "Significant concerns - Multiple red flags suggest potential manipulation"
        else:
            summary = "High risk - Strong indicators of artificial growth and manipulation"
        
        # Add specific concerns
        major_concerns = []
        for flag_type, flag_data in red_flags.items():
            if flag_data.get("severity", 0) >= 60:
                major_concerns.append(flag_type.replace("_", " "))
        
        if major_concerns:
            summary += f". Primary concerns: {', '.join(major_concerns)}"
        
        return summary