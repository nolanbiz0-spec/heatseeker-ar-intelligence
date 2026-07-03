# 🔥 Enhanced A&R Intelligence System v3.0 - Engagement Velocity Engine

## ENGAGEMENT VELOCITY TRACKING SYSTEM

### Core A&R Intelligence Metrics:
1. **Follower Count:** 10K-50K (optimal targeting window)
2. **Engagement Rate:** 25-40% (likes to followers ratio)
3. **Comment Velocity:** 500+ comments in first hour = TIER 1 TARGET
4. **Independence Status:** Multi-source verification (Spotify + MusicBrainz + SpotScraper)
5. **Geographic Concentration:** Target market presence validation

---

## ENGAGEMENT VELOCITY ENGINE ARCHITECTURE

### Real-Time Instagram Monitoring System

```python
import asyncio
import httpx
from datetime import datetime, timedelta
import json

class EngagementVelocityTracker:
    """
    Track INSTAGRAM-SPECIFIC comment velocity for A&R intelligence
    
    CRITICAL SPECIFICATION:
    - INSTAGRAM ONLY - not cross-platform aggregation
    - 500+ comments within first hour AFTER they post on Instagram
    - Real-time monitoring of individual Instagram posts
    - Measures community response speed on single platform
    """
    
    def __init__(self, instagram_api_key):
        self.instagram_api = instagram_api_key
        self.velocity_thresholds = {
            "TIER_1": 500,  # Comments in first hour - URGENT TARGET
            "TIER_2": 200,  # High priority 
            "TIER_3": 100,  # Monitor closely
            "TIER_4": 50    # Standard tracking
        }
    
    async def track_post_velocity(self, artist_instagram_handle, post_id):
        """
        Monitor comment accumulation in first hour after post
        Returns velocity score and A&R tier classification
        """
        
        post_timestamp = await self.get_post_timestamp(post_id)
        
        # Track comments every 15 minutes for first hour
        velocity_data = []
        
        for checkpoint in [15, 30, 45, 60]:  # Minutes after posting
            await asyncio.sleep(900)  # Wait 15 minutes
            
            comment_count = await self.get_comment_count(post_id)
            velocity_data.append({
                "minutes_elapsed": checkpoint,
                "total_comments": comment_count,
                "velocity_per_hour": (comment_count / checkpoint) * 60
            })
        
        # Calculate final first-hour velocity
        first_hour_comments = velocity_data[-1]["total_comments"]
        
        # Determine A&R tier
        tier = self.classify_ar_tier(first_hour_comments)
        
        return {
            "artist": artist_instagram_handle,
            "post_id": post_id,
            "first_hour_comments": first_hour_comments,
            "ar_tier": tier,
            "velocity_data": velocity_data,
            "commercial_potential": self.assess_commercial_potential(first_hour_comments),
            "recommended_action": self.get_ar_recommendation(tier)
        }
    
    def classify_ar_tier(self, comment_count):
        """Classify A&R priority based on comment velocity"""
        
        if comment_count >= self.velocity_thresholds["TIER_1"]:
            return "TIER_1_URGENT"
        elif comment_count >= self.velocity_thresholds["TIER_2"]:
            return "TIER_2_HIGH_PRIORITY"
        elif comment_count >= self.velocity_thresholds["TIER_3"]:
            return "TIER_3_MONITOR"
        else:
            return "TIER_4_STANDARD"
    
    def assess_commercial_potential(self, velocity):
        """Assess commercial viability from engagement velocity"""
        
        if velocity >= 500:
            return {
                "score": 95,
                "indicators": [
                    "Superfan concentration - immediate response to content",
                    "High concert ticket conversion potential", 
                    "Strong merchandise sales likelihood",
                    "Viral content amplification capability",
                    "Active community ready for album releases"
                ]
            }
        elif velocity >= 200:
            return {
                "score": 80,
                "indicators": [
                    "Strong engaged fanbase",
                    "Good touring potential in key markets",
                    "Solid streaming conversion rates",
                    "Community building in progress"
                ]
            }
        else:
            return {
                "score": 60,
                "indicators": [
                    "Growing but early-stage engagement", 
                    "Monitor for velocity increases",
                    "Potential for development"
                ]
            }
    
    def get_ar_recommendation(self, tier):
        """Generate A&R action recommendations based on tier"""
        
        recommendations = {
            "TIER_1_URGENT": {
                "timeline": "Contact within 48-72 hours",
                "actions": [
                    "Immediate management/booking contact research",
                    "Attend next live show in major market",
                    "Competitive intelligence - check other label interest", 
                    "Prepare preliminary offer structure",
                    "Fast-track A&R presentation to leadership"
                ],
                "rationale": "500+ comments/hour indicates superfan base ready for major label push"
            },
            
            "TIER_2_HIGH_PRIORITY": {
                "timeline": "Contact within 1-2 weeks", 
                "actions": [
                    "Deep-dive streaming analytics verification",
                    "Research management representation status",
                    "Monitor next 2-3 posts for velocity consistency",
                    "Attend upcoming shows for live assessment",
                    "Prepare A&R brief for monthly review"
                ],
                "rationale": "200-499 comments/hour shows strong engagement, monitor for Tier 1 growth"
            },
            
            "TIER_3_MONITOR": {
                "timeline": "Monthly check-ins for 3-6 months",
                "actions": [
                    "Track velocity trends across multiple posts",
                    "Monitor follower growth consistency", 
                    "Watch for touring expansion signals",
                    "Quarterly A&R review inclusion"
                ],
                "rationale": "100-200 comments shows potential, needs development time"
            },
            
            "TIER_4_STANDARD": {
                "timeline": "Quarterly monitoring",
                "actions": [
                    "Include in broader indie scene tracking",
                    "Watch for breakthrough moments",
                    "Annual A&R pipeline review"
                ],
                "rationale": "Early stage - standard indie development timeline"
            }
        }
        
        return recommendations.get(tier, recommendations["TIER_4_STANDARD"])

class ARIntelligenceSystem:
    """
    Enhanced A&R Intelligence combining follower metrics + engagement velocity
    """
    
    def __init__(self):
        self.velocity_tracker = EngagementVelocityTracker(instagram_api_key="TBD")
        self.independence_verifier = IndependenceVerificationEngine()
    
    async def comprehensive_ar_assessment(self, artist_name, instagram_handle):
        """
        Complete A&R intelligence assessment combining all metrics
        """
        
        print(f"🎯 COMPREHENSIVE A&R ASSESSMENT: {artist_name}")
        print("=" * 60)
        
        # 1. Independence verification (existing system)
        independence = await self.independence_verifier.verify_independence(artist_name)
        
        # 2. Follower metrics (existing system) 
        follower_metrics = await self.get_follower_metrics(instagram_handle)
        
        # 3. Engagement velocity (NEW)
        recent_posts = await self.get_recent_posts(instagram_handle, limit=3)
        velocity_scores = []
        
        for post in recent_posts:
            velocity = await self.velocity_tracker.track_post_velocity(instagram_handle, post['id'])
            velocity_scores.append(velocity)
        
        # 4. Calculate composite A&R score
        composite_score = self.calculate_composite_ar_score(
            independence, follower_metrics, velocity_scores
        )
        
        # 5. Generate final recommendation
        return {
            "artist_name": artist_name,
            "independence_status": independence,
            "follower_metrics": follower_metrics,
            "engagement_velocity": velocity_scores,
            "composite_ar_score": composite_score,
            "final_recommendation": self.generate_final_recommendation(composite_score),
            "competitive_timeline": self.assess_competitive_timeline(composite_score)
        }
    
    def calculate_composite_ar_score(self, independence, followers, velocity):
        """
        Weighted A&R scoring:
        - Independence: 30% (must be unsigned)
        - Follower count: 25% (10K-50K sweet spot)
        - Engagement rate: 25% (25-40% optimal)
        - Velocity: 20% (500+ comments = bonus)
        """
        
        score = 0
        
        # Independence (30 points max)
        if independence['status'] == 'unsigned':
            score += 30
        elif independence['status'] == 'indie_label':
            score += 20
        else:
            score += 0  # Signed to major = not targetable
        
        # Follower count (25 points max)
        follower_count = followers.get('count', 0)
        if 10000 <= follower_count <= 50000:
            score += 25  # Sweet spot
        elif 5000 <= follower_count <= 75000:
            score += 20  # Good range
        elif 1000 <= follower_count <= 100000:
            score += 15  # Acceptable
        else:
            score += 5   # Too small or too big
        
        # Engagement rate (25 points max)
        engagement_rate = followers.get('engagement_rate', 0)
        if 25 <= engagement_rate <= 40:
            score += 25  # Optimal
        elif 20 <= engagement_rate <= 45:
            score += 20  # Good
        elif 15 <= engagement_rate <= 50:
            score += 15  # Acceptable
        else:
            score += 10  # Suboptimal
        
        # Comment velocity (20 points max)
        avg_velocity = sum(v['first_hour_comments'] for v in velocity) / len(velocity)
        if avg_velocity >= 500:
            score += 20  # Tier 1 - superfan base
        elif avg_velocity >= 200:
            score += 15  # Tier 2 - strong engagement
        elif avg_velocity >= 100:
            score += 10  # Tier 3 - developing
        else:
            score += 5   # Early stage
        
        return score
    
    def generate_final_recommendation(self, composite_score):
        """Generate final A&R recommendation based on composite score"""
        
        if composite_score >= 85:
            return {
                "priority": "URGENT_TIER_1",
                "timeline": "Contact within 24-48 hours",
                "rationale": "Perfect A&R metrics - unsigned artist with superfan engagement",
                "action": "Immediate deal pursuit - competitive situation likely"
            }
        elif composite_score >= 70:
            return {
                "priority": "HIGH_PRIORITY_TIER_2", 
                "timeline": "Contact within 1-2 weeks",
                "rationale": "Strong A&R candidate with good metrics across all categories",
                "action": "Fast-track research and outreach"
            }
        elif composite_score >= 55:
            return {
                "priority": "MONITOR_TIER_3",
                "timeline": "Monthly monitoring for 3-6 months", 
                "rationale": "Developing artist with some strong metrics",
                "action": "Track growth trajectory and engagement trends"
            }
        else:
            return {
                "priority": "STANDARD_TRACKING",
                "timeline": "Quarterly review",
                "rationale": "Early stage or suboptimal metrics",
                "action": "Include in broader indie scene monitoring"
            }

# Usage example:
async def main():
    ar_system = ARIntelligenceSystem()
    
    # Assess Lunar Vacation with new velocity tracking
    assessment = await ar_system.comprehensive_ar_assessment(
        "Lunar Vacation", 
        "@lunarvacation"
    )
    
    print(json.dumps(assessment, indent=2))

# Run assessment
# asyncio.run(main())
```

---

## ENHANCED HEATSEEKER DASHBOARD FEATURES

### Real-Time Engagement Velocity Tracking
- **Live comment monitoring** for tracked artists
- **Velocity alerts** when artists hit 500+ comments/hour
- **Trend analysis** across multiple posts
- **Competitive benchmarking** against similar artists

### A&R Intelligence Dashboard
- **Composite scoring** combining all metrics
- **Priority queues** based on velocity + independence
- **Alert system** for Tier 1 urgent targets
- **Historical velocity tracking** for momentum analysis

### Enhanced API Endpoints
```
GET /velocity/{artist_instagram}     - Current velocity metrics
GET /ar-assessment/{artist_name}     - Comprehensive A&R scoring  
GET /tier-1-alerts                   - Artists hitting 500+ velocity
GET /competitive-timeline/{artist}   - Deal urgency assessment
```

---

## IMPLEMENTATION ROADMAP

### Phase 1: Core Velocity Engine (Week 1)
- Instagram API integration for comment tracking
- Velocity calculation algorithms
- Basic tier classification system

### Phase 2: Enhanced Dashboard (Week 2)  
- Real-time velocity monitoring interface
- Alert system for 500+ comment velocity
- Historical trend visualization

### Phase 3: Composite Scoring (Week 3)
- Weighted A&R scoring algorithm
- Final recommendation engine
- Competitive timeline assessment

### Phase 4: Production Deployment (Week 4)
- Railway deployment with Instagram API
- Team dashboard for A&R decision making
- Automated velocity alerts and briefings

---

**🚀 This enhanced system transforms A&R intelligence from static metrics to real-time engagement velocity tracking - identifying superfan concentrations that indicate commercial breakthrough potential!**