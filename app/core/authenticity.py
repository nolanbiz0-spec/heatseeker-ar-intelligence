from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re
from ..config import settings


class AuthenticityScorer:
    """Detect fake engagement, bot farms, and inauthentic growth patterns"""
    
    @staticmethod
    async def calculate_engagement_ratio(
        followers: int,
        avg_engagement: int,
        recent_posts: int = 10
    ) -> float:
        """Calculate engagement ratio as percentage"""
        if followers <= 0 or recent_posts <= 0:
            return 0.0
        
        engagement_rate = (avg_engagement / followers) * 100
        return min(100.0, max(0.0, engagement_rate))
    
    async def analyze_follower_growth_pattern(
        self,
        growth_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze follower growth for suspicious patterns"""
        
        if len(growth_history) < 7:  # Need at least a week of data
            return {"suspicious": False, "confidence": 0.0, "patterns": []}
        
        suspicious_patterns = []
        daily_growth = []
        
        # Calculate daily growth rates
        for i in range(1, len(growth_history)):
            prev_followers = growth_history[i-1].get("followers", 0)
            curr_followers = growth_history[i].get("followers", 0)
            
            if prev_followers > 0:
                growth_rate = ((curr_followers - prev_followers) / prev_followers) * 100
                daily_growth.append(growth_rate)
        
        if not daily_growth:
            return {"suspicious": False, "confidence": 0.0, "patterns": []}
        
        # Check for bot farm patterns
        
        # 1. Sudden massive spikes (>50% growth in single day)
        spike_days = [growth for growth in daily_growth if growth > 50]
        if len(spike_days) > 0:
            suspicious_patterns.append({
                "type": "massive_spikes",
                "severity": len(spike_days) / len(daily_growth),
                "description": f"{len(spike_days)} days with >50% follower growth"
            })
        
        # 2. Perfectly linear growth (bot-like)
        import statistics
        growth_std = statistics.stdev(daily_growth) if len(daily_growth) > 1 else 0
        avg_growth = statistics.mean(daily_growth)
        
        if growth_std < 1.0 and avg_growth > 5.0:  # Very consistent high growth
            suspicious_patterns.append({
                "type": "linear_growth",
                "severity": 1.0 - (growth_std / 10.0),
                "description": "Unnaturally consistent follower growth"
            })
        
        # 3. Weekend/weekday pattern anomalies
        # (Real growth typically varies by day of week)
        
        # Calculate overall suspicion score
        if suspicious_patterns:
            avg_severity = sum(p["severity"] for p in suspicious_patterns) / len(suspicious_patterns)
            confidence = min(1.0, avg_severity)
        else:
            confidence = 0.0
        
        return {
            "suspicious": confidence > 0.6,
            "confidence": confidence,
            "patterns": suspicious_patterns
        }
    
    async def analyze_geographic_distribution(
        self,
        geographic_data: Dict[str, int],
        artist_origin_country: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze geographic listening patterns for authenticity"""
        
        if not geographic_data:
            return {"authentic": True, "score": 1.0, "flags": []}
        
        total_listeners = sum(geographic_data.values())
        if total_listeners == 0:
            return {"authentic": True, "score": 1.0, "flags": []}
        
        flags = []
        
        # Calculate country percentages
        country_percentages = {
            country: (listeners / total_listeners) * 100
            for country, listeners in geographic_data.items()
        }
        
        # Flag 1: Over-concentration in single country
        max_country = max(country_percentages, key=country_percentages.get)
        max_percentage = country_percentages[max_country]
        
        # Major music markets where high concentration is normal
        major_markets = ["US", "GB", "CA", "AU", "DE", "FR", "JP", "KR", "BR", "MX"]
        
        if max_percentage > 80 and max_country not in major_markets:
            flags.append({
                "type": "geographic_concentration",
                "severity": (max_percentage - 80) / 20,
                "description": f"{max_percentage:.1f}% listeners from {max_country}"
            })
        
        # Flag 2: Unusual country combinations (known bot farm locations)
        suspicious_countries = ["BD", "PK", "IN", "ID", "NG"]  # Common bot farm locations
        suspicious_percentage = sum(
            country_percentages.get(country, 0) 
            for country in suspicious_countries
        )
        
        if suspicious_percentage > 30:
            flags.append({
                "type": "suspicious_countries",
                "severity": suspicious_percentage / 100,
                "description": f"{suspicious_percentage:.1f}% from potential bot farm countries"
            })
        
        # Flag 3: Missing expected markets
        if artist_origin_country and artist_origin_country in major_markets:
            origin_percentage = country_percentages.get(artist_origin_country, 0)
            if origin_percentage < 10:  # Artist has <10% listeners from home country
                flags.append({
                    "type": "missing_home_market",
                    "severity": (10 - origin_percentage) / 10,
                    "description": f"Only {origin_percentage:.1f}% from artist's home country"
                })
        
        # Calculate authenticity score
        if flags:
            avg_severity = sum(flag["severity"] for flag in flags) / len(flags)
            authenticity_score = max(0.0, 1.0 - avg_severity)
        else:
            authenticity_score = 1.0
        
        return {
            "authentic": authenticity_score > settings.authenticity_threshold,
            "score": authenticity_score,
            "flags": flags
        }
    
    async def analyze_playlist_placements(
        self,
        playlist_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze playlist placements for pay-for-play patterns"""
        
        if not playlist_data:
            return {"organic": True, "score": 1.0, "flags": []}
        
        flags = []
        
        # Categorize playlists
        major_playlists = 0
        indie_playlists = 0
        suspicious_playlists = 0
        
        for playlist in playlist_data:
            follower_count = playlist.get("follower_count", 0)
            name = playlist.get("name", "").lower()
            
            # Major playlist indicators
            if follower_count > 1000000 or any(term in name for term in ["rap caviar", "today's top hits", "hot country", "rock this"]):
                major_playlists += 1
            
            # Suspicious playlist patterns
            elif follower_count > 50000 and any(pattern in name for pattern in [
                "playlist", "music", "new", "fresh", "hot", "best"
            ]):
                # Generic names with high followers often indicate pay-for-play
                suspicious_playlists += 1
            
            else:
                indie_playlists += 1
        
        total_playlists = len(playlist_data)
        
        # Flag high ratio of suspicious playlists
        if total_playlists > 0:
            suspicious_ratio = suspicious_playlists / total_playlists
            if suspicious_ratio > 0.5:
                flags.append({
                    "type": "suspicious_playlists",
                    "severity": suspicious_ratio,
                    "description": f"{suspicious_ratio*100:.1f}% of playlists appear to be pay-for-play"
                })
        
        # Calculate organic score
        organic_score = 1.0
        if flags:
            avg_severity = sum(flag["severity"] for flag in flags) / len(flags)
            organic_score = max(0.0, 1.0 - avg_severity)
        
        return {
            "organic": organic_score > 0.7,
            "score": organic_score,
            "flags": flags,
            "breakdown": {
                "major_playlists": major_playlists,
                "indie_playlists": indie_playlists,
                "suspicious_playlists": suspicious_playlists
            }
        }
    
    async def calculate_overall_authenticity_score(
        self,
        engagement_analysis: Dict[str, Any],
        geographic_analysis: Dict[str, Any],
        growth_analysis: Dict[str, Any],
        playlist_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate composite authenticity score"""
        
        scores = []
        weight_total = 0
        
        # Weight engagement ratio (30%)
        if engagement_analysis.get("ratio") is not None:
            engagement_score = min(1.0, engagement_analysis["ratio"] / 5.0)  # 5% = perfect score
            scores.append(engagement_score * 0.3)
            weight_total += 0.3
        
        # Weight geographic authenticity (25%)
        if geographic_analysis.get("score") is not None:
            scores.append(geographic_analysis["score"] * 0.25)
            weight_total += 0.25
        
        # Weight growth pattern authenticity (25%)
        if growth_analysis.get("confidence") is not None:
            growth_score = 1.0 - growth_analysis["confidence"]  # Invert confidence (high confidence = low authenticity)
            scores.append(growth_score * 0.25)
            weight_total += 0.25
        
        # Weight playlist authenticity (20%)
        if playlist_analysis.get("score") is not None:
            scores.append(playlist_analysis["score"] * 0.2)
            weight_total += 0.2
        
        # Calculate weighted average
        if weight_total > 0:
            overall_score = sum(scores) / weight_total
        else:
            overall_score = 0.5  # Neutral score if no data
        
        return {
            "score": round(overall_score, 3),
            "authentic": overall_score > settings.authenticity_threshold,
            "confidence": weight_total,  # How much data we had to work with
            "breakdown": {
                "engagement": engagement_analysis,
                "geographic": geographic_analysis,
                "growth": growth_analysis,
                "playlists": playlist_analysis
            }
        }


# Global instance
authenticity_scorer = AuthenticityScorer()