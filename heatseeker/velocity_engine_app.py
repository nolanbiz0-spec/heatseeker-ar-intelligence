from fastapi import FastAPI, HTTPException
import httpx
import asyncio
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional

app = FastAPI(title="Heatseeker A&R Intelligence v3.0 - Engagement Velocity Engine")

class EngagementVelocityEngine:
    """
    Core engagement velocity tracking for A&R intelligence
    Tracks Instagram comment velocity: 500+ comments/hour = TIER 1 targets
    """
    
    def __init__(self):
        self.velocity_thresholds = {
            "TIER_1_URGENT": 500,      # Comments in first hour - URGENT TARGET
            "TIER_2_HIGH_PRIORITY": 200,  # High priority 
            "TIER_3_MONITOR": 100,     # Monitor closely
            "TIER_4_STANDARD": 50      # Standard tracking
        }
        
        # Mock engagement data for demo (replace with real Instagram API)
        self.mock_engagement_data = {
            "lunar_vacation": {
                "followers": 22000,
                "recent_posts": [
                    {"id": "post_1", "comments_first_hour": 620, "likes": 8400, "timestamp": "2026-07-02"},
                    {"id": "post_2", "comments_first_hour": 580, "likes": 7800, "timestamp": "2026-06-28"},
                    {"id": "post_3", "comments_first_hour": 545, "likes": 7200, "timestamp": "2026-06-25"}
                ]
            },
            "pool_kids": {
                "followers": 8500,
                "recent_posts": [
                    {"id": "post_1", "comments_first_hour": 180, "likes": 3200, "timestamp": "2026-07-01"},
                    {"id": "post_2", "comments_first_hour": 165, "likes": 2900, "timestamp": "2026-06-27"}
                ]
            },
            "being_dead": {
                "followers": 12000,
                "recent_posts": [
                    {"id": "post_1", "comments_first_hour": 340, "likes": 4800, "timestamp": "2026-06-30"},
                    {"id": "post_2", "comments_first_hour": 280, "likes": 4200, "timestamp": "2026-06-26"}
                ]
            },
            "softcult": {
                "followers": 15000,
                "recent_posts": [
                    {"id": "post_1", "comments_first_hour": 420, "likes": 5600, "timestamp": "2026-06-29"},
                    {"id": "post_2", "comments_first_hour": 390, "likes": 5200, "timestamp": "2026-06-24"}
                ]
            }
        }
    
    async def get_engagement_velocity(self, artist_name: str) -> Dict:
        """Get comprehensive engagement velocity analysis for an artist"""
        
        # Normalize artist name for lookup
        normalized_name = artist_name.lower().replace(" ", "_")
        
        if normalized_name not in self.mock_engagement_data:
            return {
                "error": f"Artist '{artist_name}' not found in engagement tracking system",
                "available_artists": list(self.mock_engagement_data.keys())
            }
        
        data = self.mock_engagement_data[normalized_name]
        
        # Calculate velocity metrics
        recent_posts = data["recent_posts"]
        avg_velocity = sum(post["comments_first_hour"] for post in recent_posts) / len(recent_posts)
        avg_likes = sum(post["likes"] for post in recent_posts) / len(recent_posts)
        
        followers = data["followers"]
        engagement_rate = (avg_likes / followers) * 100
        
        # Classify A&R tier based on velocity
        tier = self.classify_ar_tier(avg_velocity)
        
        # Assess commercial potential
        commercial_potential = self.assess_commercial_potential(avg_velocity, engagement_rate)
        
        # Generate A&R recommendation
        recommendation = self.get_ar_recommendation(tier, avg_velocity)
        
        return {
            "artist_name": artist_name,
            "followers": followers,
            "avg_comments_first_hour": round(avg_velocity),
            "avg_likes_per_post": round(avg_likes),
            "engagement_rate": round(engagement_rate, 1),
            "ar_tier": tier,
            "commercial_potential_score": commercial_potential["score"],
            "commercial_indicators": commercial_potential["indicators"],
            "ar_recommendation": recommendation,
            "recent_post_analysis": recent_posts,
            "velocity_timestamp": datetime.now().isoformat()
        }
    
    def classify_ar_tier(self, avg_velocity: float) -> str:
        """Classify A&R priority based on comment velocity"""
        
        if avg_velocity >= self.velocity_thresholds["TIER_1_URGENT"]:
            return "TIER_1_URGENT"
        elif avg_velocity >= self.velocity_thresholds["TIER_2_HIGH_PRIORITY"]:
            return "TIER_2_HIGH_PRIORITY"
        elif avg_velocity >= self.velocity_thresholds["TIER_3_MONITOR"]:
            return "TIER_3_MONITOR"
        else:
            return "TIER_4_STANDARD"
    
    def assess_commercial_potential(self, velocity: float, engagement_rate: float) -> Dict:
        """Assess commercial viability from engagement velocity + rate"""
        
        if velocity >= 500 and engagement_rate >= 25:
            return {
                "score": 95,
                "indicators": [
                    "🔥 Superfan concentration - immediate response to content",
                    "🎫 High concert ticket conversion potential", 
                    "💿 Strong album pre-order likelihood",
                    "🚀 Viral content amplification capability",
                    "👥 Active community ready for major label push"
                ]
            }
        elif velocity >= 500 or engagement_rate >= 30:
            return {
                "score": 85,
                "indicators": [
                    "⚡ Strong velocity or engagement rate",
                    "🎵 Good streaming conversion potential",
                    "🎪 Solid touring prospects in key markets",
                    "📈 Growth trajectory trending upward"
                ]
            }
        elif velocity >= 200 and engagement_rate >= 20:
            return {
                "score": 75,
                "indicators": [
                    "📊 Strong engaged fanbase foundation",
                    "🎭 Good live show attendance potential",
                    "💽 Decent streaming conversion rates",
                    "🌱 Community building in progress"
                ]
            }
        else:
            return {
                "score": 60,
                "indicators": [
                    "🌿 Growing but early-stage engagement", 
                    "👀 Monitor for velocity increases",
                    "⭐ Potential for future development"
                ]
            }
    
    def get_ar_recommendation(self, tier: str, velocity: float) -> Dict:
        """Generate A&R action recommendations based on tier and velocity"""
        
        recommendations = {
            "TIER_1_URGENT": {
                "priority": "🚨 URGENT ACTION REQUIRED",
                "timeline": "Contact within 24-48 hours",
                "actions": [
                    "Immediate management/booking contact research",
                    "Attend next live show in major market", 
                    "Competitive intelligence - check other label interest",
                    "Prepare preliminary offer structure",
                    "Fast-track A&R presentation to leadership"
                ],
                "rationale": f"{velocity:.0f} comments/hour indicates superfan base ready for major label push",
                "urgency_score": 95
            },
            
            "TIER_2_HIGH_PRIORITY": {
                "priority": "⚡ HIGH PRIORITY TARGET",
                "timeline": "Contact within 1-2 weeks",
                "actions": [
                    "Deep-dive streaming analytics verification",
                    "Research management representation status",
                    "Monitor next 2-3 posts for velocity consistency",
                    "Attend upcoming shows for live assessment",
                    "Prepare A&R brief for weekly review"
                ],
                "rationale": f"{velocity:.0f} comments/hour shows strong engagement, monitor for Tier 1 growth",
                "urgency_score": 80
            },
            
            "TIER_3_MONITOR": {
                "priority": "📈 MONITOR CLOSELY", 
                "timeline": "Bi-weekly check-ins for 2-3 months",
                "actions": [
                    "Track velocity trends across multiple posts",
                    "Monitor follower growth consistency",
                    "Watch for touring expansion signals", 
                    "Monthly A&R review inclusion"
                ],
                "rationale": f"{velocity:.0f} comments shows potential, needs development time",
                "urgency_score": 65
            },
            
            "TIER_4_STANDARD": {
                "priority": "👀 STANDARD TRACKING",
                "timeline": "Monthly monitoring", 
                "actions": [
                    "Include in broader indie scene tracking",
                    "Watch for breakthrough velocity moments",
                    "Quarterly A&R pipeline review"
                ],
                "rationale": f"{velocity:.0f} comments indicates early stage development",
                "urgency_score": 45
            }
        }
        
        return recommendations.get(tier, recommendations["TIER_4_STANDARD"])

# Initialize velocity engine
velocity_engine = EngagementVelocityEngine()

@app.get("/")
async def root():
    return {
        "service": "Heatseeker A&R Intelligence v3.0", 
        "feature": "Engagement Velocity Engine",
        "description": "Real-time Instagram comment velocity tracking for A&R targeting",
        "tier_1_threshold": "500+ comments in first hour = URGENT TARGET"
    }

@app.get("/velocity/{artist_name}")
async def get_artist_velocity(artist_name: str):
    """Get engagement velocity analysis for specific artist"""
    
    try:
        velocity_data = await velocity_engine.get_engagement_velocity(artist_name)
        return velocity_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Velocity analysis error: {str(e)}")

@app.get("/tier-1-alerts")
async def get_tier_1_alerts():
    """Get all artists currently hitting Tier 1 velocity (500+ comments/hour)"""
    
    tier_1_artists = []
    
    for artist_key in velocity_engine.mock_engagement_data.keys():
        artist_name = artist_key.replace("_", " ").title()
        velocity_data = await velocity_engine.get_engagement_velocity(artist_name)
        
        if velocity_data.get("ar_tier") == "TIER_1_URGENT":
            tier_1_artists.append({
                "artist": artist_name,
                "avg_velocity": velocity_data["avg_comments_first_hour"],
                "followers": velocity_data["followers"],
                "engagement_rate": velocity_data["engagement_rate"],
                "urgency_score": velocity_data["ar_recommendation"]["urgency_score"],
                "timeline": velocity_data["ar_recommendation"]["timeline"]
            })
    
    return {
        "tier_1_urgent_targets": tier_1_artists,
        "count": len(tier_1_artists),
        "threshold": "500+ comments in first hour",
        "recommendation": "Immediate A&R contact required for all Tier 1 targets",
        "generated_at": datetime.now().isoformat()
    }

@app.get("/ar-dashboard")
async def get_ar_dashboard():
    """Complete A&R dashboard with all artists and velocity tiers"""
    
    dashboard_data = {
        "tier_1_urgent": [],
        "tier_2_high_priority": [],
        "tier_3_monitor": [],
        "tier_4_standard": []
    }
    
    for artist_key in velocity_engine.mock_engagement_data.keys():
        artist_name = artist_key.replace("_", " ").title()
        velocity_data = await velocity_engine.get_engagement_velocity(artist_name)
        
        tier = velocity_data.get("ar_tier", "").lower()
        
        artist_summary = {
            "artist": artist_name,
            "velocity": velocity_data["avg_comments_first_hour"],
            "followers": velocity_data["followers"], 
            "engagement_rate": velocity_data["engagement_rate"],
            "commercial_score": velocity_data["commercial_potential_score"],
            "timeline": velocity_data["ar_recommendation"]["timeline"]
        }
        
        if "tier_1" in tier:
            dashboard_data["tier_1_urgent"].append(artist_summary)
        elif "tier_2" in tier:
            dashboard_data["tier_2_high_priority"].append(artist_summary)
        elif "tier_3" in tier:
            dashboard_data["tier_3_monitor"].append(artist_summary)
        else:
            dashboard_data["tier_4_standard"].append(artist_summary)
    
    # Sort each tier by velocity
    for tier in dashboard_data.values():
        tier.sort(key=lambda x: x["velocity"], reverse=True)
    
    return {
        "ar_intelligence_dashboard": dashboard_data,
        "summary": {
            "tier_1_count": len(dashboard_data["tier_1_urgent"]),
            "tier_2_count": len(dashboard_data["tier_2_high_priority"]),
            "total_tracked": sum(len(tier) for tier in dashboard_data.values()),
            "tier_1_threshold": "500+ comments/hour",
            "generated_at": datetime.now().isoformat()
        }
    }

@app.get("/competitive-timeline/{artist_name}")
async def get_competitive_timeline(artist_name: str):
    """Assess competitive deal timeline based on engagement velocity"""
    
    velocity_data = await velocity_engine.get_engagement_velocity(artist_name)
    
    if "error" in velocity_data:
        raise HTTPException(status_code=404, detail=velocity_data["error"])
    
    avg_velocity = velocity_data["avg_comments_first_hour"]
    engagement_rate = velocity_data["engagement_rate"]
    followers = velocity_data["followers"]
    
    # Calculate competitive pressure timeline
    if avg_velocity >= 500 and followers >= 15000:
        timeline = {
            "competitive_pressure": "IMMEDIATE",
            "deal_window": "2-4 weeks maximum",
            "risk_factors": [
                "🚨 Superfan engagement = major label attention",
                "📊 Follower count visible to competitor A&Rs", 
                "⚡ High velocity likely triggering industry alerts",
                "🎯 Perfect A&R metrics = bidding war risk"
            ],
            "recommended_action": "Move immediately - competitive situation imminent"
        }
    elif avg_velocity >= 300 or followers >= 25000:
        timeline = {
            "competitive_pressure": "HIGH", 
            "deal_window": "4-8 weeks",
            "risk_factors": [
                "📈 Strong metrics approaching major label thresholds",
                "🎵 Growing industry awareness likely",
                "⏰ Window narrowing with each post/milestone"
            ],
            "recommended_action": "Fast-track outreach within 2-3 weeks"
        }
    elif avg_velocity >= 150 or followers >= 15000:
        timeline = {
            "competitive_pressure": "MODERATE",
            "deal_window": "2-4 months", 
            "risk_factors": [
                "📊 Visible growth trajectory",
                "👀 Indie A&R starting to track",
                "🎪 Touring expansion may trigger attention"
            ],
            "recommended_action": "Monitor closely, prepare for outreach"
        }
    else:
        timeline = {
            "competitive_pressure": "LOW",
            "deal_window": "6-12 months",
            "risk_factors": [
                "🌱 Early stage development",
                "⭐ Time for relationship building"
            ],
            "recommended_action": "Standard monitoring and development"
        }
    
    return {
        "artist": artist_name,
        "current_metrics": {
            "velocity": avg_velocity,
            "engagement_rate": engagement_rate,
            "followers": followers
        },
        "competitive_timeline": timeline,
        "analysis_timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)