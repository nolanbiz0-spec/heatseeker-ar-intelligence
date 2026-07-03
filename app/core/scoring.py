from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from ..config import settings


class OpportunityScorer:
    """Score commercial opportunities and deal urgency for artists"""
    
    async def calculate_independence_score(
        self,
        label_status: Optional[str],
        distributor: Optional[str],
        deal_indicators: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Score independence level and deal accessibility"""
        
        deal_indicators = deal_indicators or {}
        
        # Independence levels (1.0 = fully independent, 0.0 = major label)
        if not label_status or label_status.lower() in ["independent", "indie", "self-released"]:
            independence_level = 1.0
        elif label_status.lower() in ["universal", "sony", "warner", "umg", "smg", "wmg"]:
            independence_level = 0.0
        else:
            independence_level = 0.5  # Indie label or unclear
        
        # Distributor analysis
        major_distributors = ["distrokid", "cd baby", "tunecore", "amuse", "ditto"]
        indie_distributors = ["believe", "stem", "empire", "ingrooves"]
        
        distributor_score = 1.0  # Default independent
        if distributor:
            dist_lower = distributor.lower()
            if any(major in dist_lower for major in ["universal", "sony", "warner"]):
                distributor_score = 0.0
            elif any(indie in dist_lower for indie in indie_distributors):
                distributor_score = 0.7
            elif any(diy in dist_lower for diy in major_distributors):
                distributor_score = 1.0
        
        # Deal timing indicators
        urgency_factors = []
        
        # Recent rapid growth = higher urgency
        if deal_indicators.get("velocity_30d", 0) > 100:
            urgency_factors.append(("rapid_growth", 0.8))
        
        # Viral content or breakthrough moment
        if deal_indicators.get("viral_content", False):
            urgency_factors.append(("viral_moment", 0.9))
        
        # Cross-platform momentum
        if deal_indicators.get("cross_platform_score", 0) > 0.8:
            urgency_factors.append(("cross_platform", 0.7))
        
        # Competition indicators
        if deal_indicators.get("industry_attention", False):
            urgency_factors.append(("industry_buzz", 0.6))
        
        # Calculate urgency multiplier
        urgency_multiplier = 1.0
        if urgency_factors:
            urgency_multiplier = max([factor[1] for factor in urgency_factors])
        
        # Final independence score
        base_score = (independence_level + distributor_score) / 2
        
        return {
            "independence_level": independence_level,
            "distributor_freedom": distributor_score,
            "base_score": base_score,
            "urgency_multiplier": urgency_multiplier,
            "final_score": base_score * urgency_multiplier,
            "deal_accessible": base_score > 0.5,
            "urgency_factors": [factor[0] for factor in urgency_factors]
        }
    
    async def calculate_commercial_potential(
        self,
        momentum_score: float,
        authenticity_score: float,
        audience_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Score commercial potential based on audience and growth"""
        
        # Audience size scoring (logarithmic scale)
        total_audience = 0
        for platform in ["spotify_monthly_listeners", "youtube_subscribers", "lastfm_listeners"]:
            total_audience += audience_metrics.get(platform, 0)
        
        import math
        if total_audience > 0:
            # Scale: 1K = 0.1, 10K = 0.3, 100K = 0.5, 1M = 0.7, 10M = 0.9
            audience_score = min(0.9, math.log10(total_audience + 1) / 7)
        else:
            audience_score = 0.0
        
        # Genre/market analysis
        genres = audience_metrics.get("genres", [])
        market_multiplier = 1.0
        
        # High-commercial genres
        commercial_genres = ["pop", "hip hop", "rap", "r&b", "country", "rock"]
        if any(genre.lower() in " ".join(genres).lower() for genre in commercial_genres):
            market_multiplier = 1.2
        
        # Niche but valuable genres
        niche_genres = ["indie", "alternative", "electronic", "folk"]
        if any(genre.lower() in " ".join(genres).lower() for genre in niche_genres):
            market_multiplier = 1.0
        
        # Experimental/difficult genres
        else:
            market_multiplier = 0.8
        
        # Demographic analysis
        age_breakdown = audience_metrics.get("age_demographics", {})
        demo_multiplier = 1.0
        
        # Target demo: 18-34 (key streaming demographic)
        if age_breakdown:
            target_demo_percentage = (
                age_breakdown.get("18-24", 0) + 
                age_breakdown.get("25-34", 0)
            )
            if target_demo_percentage > 60:
                demo_multiplier = 1.3
            elif target_demo_percentage > 40:
                demo_multiplier = 1.1
        
        # Calculate base commercial score
        base_commercial = (
            audience_score * 0.4 +      # 40% audience size
            momentum_score * 0.003 +    # 30% momentum (scale from 0-100 to 0-0.3)
            authenticity_score * 0.3    # 30% authenticity
        ) * market_multiplier * demo_multiplier
        
        return {
            "audience_score": audience_score,
            "momentum_contribution": momentum_score * 0.003,
            "authenticity_contribution": authenticity_score * 0.3,
            "market_multiplier": market_multiplier,
            "demographic_multiplier": demo_multiplier,
            "base_score": base_commercial,
            "scaled_score": min(1.0, base_commercial),
            "tier": self._get_commercial_tier(base_commercial)
        }
    
    def _get_commercial_tier(self, score: float) -> str:
        """Classify commercial potential into tiers"""
        if score >= 0.8:
            return "platinum_potential"
        elif score >= 0.6:
            return "gold_potential"
        elif score >= 0.4:
            return "strong_commercial"
        elif score >= 0.2:
            return "moderate_commercial"
        else:
            return "niche_appeal"
    
    async def calculate_deal_urgency(
        self,
        velocity_scores: Dict[str, float],
        industry_signals: Dict[str, Any],
        competition_level: float = 0.5
    ) -> Dict[str, Any]:
        """Calculate how urgently a deal should be pursued"""
        
        urgency_factors = []
        
        # Velocity-based urgency
        velocity_7d = velocity_scores.get("velocity_7d", 0)
        velocity_30d = velocity_scores.get("velocity_30d", 0)
        
        if velocity_7d > 200:  # 200% weekly growth = extremely hot
            urgency_factors.append(("explosive_growth", 0.95))
        elif velocity_7d > 100:
            urgency_factors.append(("rapid_growth", 0.8))
        elif velocity_30d > 50:
            urgency_factors.append(("strong_growth", 0.6))
        
        # Industry attention signals
        if industry_signals.get("playlist_adds", 0) > 5:
            urgency_factors.append(("playlist_momentum", 0.7))
        
        if industry_signals.get("press_mentions", 0) > 3:
            urgency_factors.append(("media_attention", 0.6))
        
        if industry_signals.get("label_inquiries", False):
            urgency_factors.append(("competitor_interest", 0.9))
        
        if industry_signals.get("booking_increase", False):
            urgency_factors.append(("live_demand", 0.5))
        
        # Seasonal/timing factors
        current_month = datetime.utcnow().month
        if current_month in [1, 9]:  # January/September = label budget reset
            urgency_factors.append(("budget_timing", 0.3))
        
        # Competition level
        competition_multiplier = 1.0 + competition_level
        
        # Calculate overall urgency
        if urgency_factors:
            base_urgency = max([factor[1] for factor in urgency_factors])
            combined_urgency = min(1.0, base_urgency * competition_multiplier)
        else:
            combined_urgency = 0.2  # Default low urgency
        
        # Urgency timeline
        if combined_urgency >= 0.9:
            timeline = "immediate"  # Days
        elif combined_urgency >= 0.7:
            timeline = "urgent"     # 1-2 weeks
        elif combined_urgency >= 0.5:
            timeline = "priority"   # 1 month
        elif combined_urgency >= 0.3:
            timeline = "monitor"    # 3 months
        else:
            timeline = "watch"      # 6+ months
        
        return {
            "urgency_score": combined_urgency,
            "timeline": timeline,
            "factors": [factor[0] for factor in urgency_factors],
            "competition_multiplier": competition_multiplier,
            "recommendation": self._get_urgency_recommendation(combined_urgency, timeline)
        }
    
    def _get_urgency_recommendation(self, urgency_score: float, timeline: str) -> str:
        """Generate actionable recommendation based on urgency"""
        if timeline == "immediate":
            return "Contact management immediately. Artist is breaking out now."
        elif timeline == "urgent":
            return "Schedule meeting within 2 weeks. Strong momentum building."
        elif timeline == "priority":
            return "Add to priority watchlist. Reach out within 30 days."
        elif timeline == "monitor":
            return "Monitor closely. Reassess in 3 months."
        else:
            return "Add to general watchlist. Check quarterly."
    
    async def calculate_final_opportunity_score(
        self,
        independence_analysis: Dict[str, Any],
        commercial_analysis: Dict[str, Any],
        urgency_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate final composite opportunity score"""
        
        # Weight the components
        independence_weight = 0.4  # 40% - Can we actually sign them?
        commercial_weight = 0.4    # 40% - Is it worth it commercially?
        urgency_weight = 0.2       # 20% - How fast do we need to move?
        
        final_score = (
            independence_analysis["final_score"] * independence_weight +
            commercial_analysis["scaled_score"] * commercial_weight +
            urgency_analysis["urgency_score"] * urgency_weight
        )
        
        # Overall recommendation
        if final_score >= 0.8 and urgency_analysis["urgency_score"] > 0.7:
            recommendation = "IMMEDIATE PRIORITY - Contact now"
        elif final_score >= 0.7:
            recommendation = "HIGH PRIORITY - Schedule meeting"
        elif final_score >= 0.5:
            recommendation = "STRONG INTEREST - Add to active watchlist"
        elif final_score >= 0.3:
            recommendation = "MONITOR - Check monthly progress"
        else:
            recommendation = "PASS - Not current priority"
        
        return {
            "final_score": round(final_score, 3),
            "recommendation": recommendation,
            "breakdown": {
                "independence": independence_analysis,
                "commercial": commercial_analysis,
                "urgency": urgency_analysis
            },
            "deal_tier": self._get_deal_tier(final_score),
            "next_steps": self._get_next_steps(final_score, urgency_analysis["timeline"])
        }
    
    def _get_deal_tier(self, score: float) -> str:
        """Classify deal opportunity tier"""
        if score >= 0.8:
            return "A-tier"
        elif score >= 0.6:
            return "B-tier"
        elif score >= 0.4:
            return "C-tier"
        else:
            return "D-tier"
    
    def _get_next_steps(self, score: float, timeline: str) -> List[str]:
        """Generate specific next steps"""
        steps = []
        
        if score >= 0.7:
            steps.append("Research management/legal representation")
            steps.append("Analyze streaming revenue potential")
            
        if timeline in ["immediate", "urgent"]:
            steps.append("Contact management within 48 hours")
            steps.append("Prepare preliminary offer framework")
        elif timeline == "priority":
            steps.append("Schedule intro call within 2 weeks")
            steps.append("Request additional streaming data")
        
        if score >= 0.5:
            steps.append("Check competitive landscape")
            steps.append("Assess touring/live potential")
        
        return steps


# Global instance
opportunity_scorer = OpportunityScorer()