#!/usr/bin/env python3
"""
Twitter API v2 Integration for Real-Time A&R Intelligence
Production-ready system for viral artist discovery and breakthrough monitoring
"""

import asyncio
import httpx
import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterARAPI:
    """
    Twitter API v2 integration for A&R intelligence
    Real-time monitoring of viral moments and artist breakthroughs
    """
    
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        
        # A&R-specific search queries for real-time monitoring
        self.ar_queries = {
            "viral_breakthrough": [
                '("my song went viral" OR "going viral" OR "blew up overnight") -is:retweet',
                '("TikTok viral" OR "viral on TikTok" OR "TikTok blew up") -is:retweet',
                '("unsigned artist" OR "independent artist" OR "no label") ("viral" OR "trending") -is:retweet',
                '("bedroom producer" OR "home studio" OR "self produced") ("viral" OR "breakthrough") -is:retweet'
            ],
            
            "engagement_velocity": [
                '("500 comments" OR "comments going crazy" OR "notifications insane") -is:retweet',
                '("DMs flooded" OR "phone blowing up" OR "can\'t keep up") -is:retweet',
                '("followers jumped" OR "gained 10k" OR "overnight growth") -is:retweet'
            ],
            
            "ken_carson_opportunities": [
                '("rage rap" OR "experimental trap" OR "opium sound") ("unsigned" OR "independent") -is:retweet',
                '("Ken Carson type" OR "opium inspired") ("original" OR "my own") -is:retweet',
                '("rage style" OR "experimental hip hop") ("no label" OR "unsigned") -is:retweet'
            ],
            
            "industry_signals": [
                '("A&R reached out" OR "label interest" OR "meeting tomorrow") -is:retweet',
                '("just got signed" OR "record deal" OR "contract") -is:retweet',
                '("management" OR "booking agent" OR "lawyer") ("signed" OR "talking") -is:retweet'
            ],
            
            "geographic_scenes": [
                '("#ATLmusic" OR "#ATLunderground" OR "Atlanta scene") ("unsigned" OR "independent") -is:retweet',
                '("#NYCindiemusic" OR "#BKscene" OR "NYC underground") ("new artist" OR "breakthrough") -is:retweet',
                '("#LAmusic" OR "#bedroompopLA" OR "LA scene") ("independent" OR "unsigned") -is:retweet',
                '("#UKdrill" OR "#Londonmusic" OR "UK scene") ("unsigned" OR "independent") -is:retweet'
            ]
        }
    
    async def search_tweets_realtime(self, query: str, max_results: int = 10) -> Dict:
        """
        Search tweets using Twitter API v2 with real-time results
        Optimized for A&R discovery and viral moment detection
        """
        
        # Twitter API v2 search endpoint
        search_url = f"{self.base_url}/tweets/search/recent"
        
        # Parameters for A&R-optimized search
        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": "author_id,created_at,public_metrics,context_annotations,referenced_tweets",
            "user.fields": "username,name,public_metrics,verified,description,location",
            "expansions": "author_id,referenced_tweets.id"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(search_url, headers=self.headers, params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    logger.warning("Rate limit hit. Waiting...")
                    await asyncio.sleep(15 * 60)  # Wait 15 minutes
                    return {"data": [], "error": "Rate limited"}
                else:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    return {"data": [], "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return {"data": [], "error": str(e)}
    
    async def monitor_viral_moments(self) -> List[Dict]:
        """
        Real-time monitoring of viral breakthrough moments
        Returns prioritized list of A&R opportunities
        """
        
        viral_discoveries = []
        
        print("🔍 TWITTER API v2 - REAL-TIME A&R MONITORING")
        print("=" * 50)
        print(f"⚡ API Status: Connected | Time: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Monitor each query category
        for category, queries in self.ar_queries.items():
            print(f"📊 {category.upper().replace('_', ' ')} MONITORING:")
            
            for query in queries:
                print(f"   🔎 Searching: {query[:60]}...")
                
                # Search Twitter API
                results = await self.search_tweets_realtime(query, max_results=10)
                
                if "error" in results:
                    print(f"      ❌ Error: {results['error']}")
                    continue
                
                # Process discoveries
                tweets = results.get("data", [])
                users = {user["id"]: user for user in results.get("includes", {}).get("users", [])}
                
                discoveries = await self.analyze_tweets_for_ar_intelligence(tweets, users, category)
                viral_discoveries.extend(discoveries)
                
                # Rate limiting - Twitter API v2 allows 300 requests per 15 minutes
                await asyncio.sleep(2)  # 2 second delay between requests
        
        return viral_discoveries
    
    async def analyze_tweets_for_ar_intelligence(self, tweets: List[Dict], users: Dict, category: str) -> List[Dict]:
        """
        Analyze tweets for A&R intelligence signals
        Score and prioritize based on viral potential and independence status
        """
        
        discoveries = []
        
        for tweet in tweets:
            user_id = tweet["author_id"]
            user = users.get(user_id, {})
            
            # Extract A&R intelligence signals
            ar_signals = await self.extract_ar_signals(tweet, user, category)
            
            if ar_signals["confidence"] > 60:  # Only high-confidence discoveries
                discovery = {
                    "timestamp": datetime.now().isoformat(),
                    "category": category,
                    "artist_handle": f"@{user.get('username', 'unknown')}",
                    "artist_name": user.get("name", "Unknown"),
                    "tweet_text": tweet["text"],
                    "tweet_url": f"https://twitter.com/{user.get('username', 'x')}/status/{tweet['id']}",
                    "followers": user.get("public_metrics", {}).get("followers_count", 0),
                    "tweet_metrics": tweet.get("public_metrics", {}),
                    "signals": ar_signals,
                    "urgency": self.calculate_urgency(ar_signals, category),
                    "next_action": self.recommend_action(ar_signals, category)
                }
                
                discoveries.append(discovery)
                
                # Log discovery
                urgency_emoji = "🚨" if discovery["urgency"] == "IMMEDIATE" else "⚡" if discovery["urgency"] == "HIGH" else "📊"
                print(f"      {urgency_emoji} DISCOVERY: {discovery['artist_name']} ({discovery['artist_handle']})")
                print(f"         Confidence: {ar_signals['confidence']}% | Urgency: {discovery['urgency']}")
        
        return discoveries
    
    async def extract_ar_signals(self, tweet: Dict, user: Dict, category: str) -> Dict:
        """
        Extract A&R intelligence signals from tweet and user data
        """
        
        text = tweet["text"].lower()
        user_desc = user.get("description", "").lower()
        followers = user.get("public_metrics", {}).get("followers_count", 0)
        
        signals = {
            "viral_indicators": [],
            "independence_indicators": [],
            "engagement_signals": [],
            "genre_signals": [],
            "confidence": 0
        }
        
        # Viral moment detection
        viral_keywords = ["viral", "blew up", "overnight", "can't believe", "insane", "crazy"]
        for keyword in viral_keywords:
            if keyword in text:
                signals["viral_indicators"].append(keyword)
        
        # Independence status signals
        independence_keywords = ["unsigned", "independent", "no label", "bedroom", "home studio", "self produced"]
        for keyword in independence_keywords:
            if keyword in text or keyword in user_desc:
                signals["independence_indicators"].append(keyword)
        
        # Engagement velocity signals (your key insight!)
        engagement_keywords = ["500 comments", "comments going crazy", "notifications", "DMs flooded", "followers jumped"]
        for keyword in engagement_keywords:
            if keyword in text:
                signals["engagement_signals"].append(keyword)
        
        # Genre-specific signals (post-Ken Carson)
        genre_keywords = ["rage rap", "experimental trap", "opium", "bedroom pop", "hyperpop"]
        for keyword in genre_keywords:
            if keyword in text or keyword in user_desc:
                signals["genre_signals"].append(keyword)
        
        # Calculate confidence score
        confidence = 0
        confidence += len(signals["viral_indicators"]) * 20
        confidence += len(signals["independence_indicators"]) * 25
        confidence += len(signals["engagement_signals"]) * 30  # Your engagement velocity insight!
        confidence += len(signals["genre_signals"]) * 15
        
        # Follower count scoring (your A&R sweet spot: 10K-50K)
        if 10000 <= followers <= 50000:
            confidence += 20  # Perfect A&R range
        elif 5000 <= followers <= 10000:
            confidence += 15  # Early stage potential
        elif followers > 100000:
            confidence -= 10  # Likely already discovered
        
        signals["confidence"] = min(confidence, 100)
        
        return signals
    
    def calculate_urgency(self, signals: Dict, category: str) -> str:
        """
        Calculate urgency level for A&R action
        """
        
        confidence = signals["confidence"]
        viral_count = len(signals["viral_indicators"])
        engagement_count = len(signals["engagement_signals"])
        
        # Immediate action required
        if confidence > 85 and viral_count > 0 and engagement_count > 0:
            return "IMMEDIATE"
        
        # High priority
        elif confidence > 70 and (viral_count > 0 or engagement_count > 0):
            return "HIGH"
        
        # Medium priority monitoring
        elif confidence > 60:
            return "MEDIUM"
        
        else:
            return "LOW"
    
    def recommend_action(self, signals: Dict, category: str) -> str:
        """
        Recommend specific A&R action based on signals
        """
        
        confidence = signals["confidence"]
        urgency = self.calculate_urgency(signals, category)
        
        if urgency == "IMMEDIATE":
            return "Contact within 6 hours - Viral window closing"
        elif urgency == "HIGH":
            return "Schedule discovery call within 24-48 hours"
        elif urgency == "MEDIUM":
            return "Add to monitoring list - Track for 1 week"
        else:
            return "Monitor passively - Low priority"

class TwitterARMonitoringService:
    """
    Production monitoring service for Twitter A&R intelligence
    Continuous monitoring with real-time alerts and data persistence
    """
    
    def __init__(self, bearer_token: str, heatseeker_api_url: str = "http://localhost:8000"):
        self.twitter_api = TwitterARAPI(bearer_token)
        self.heatseeker_url = heatseeker_api_url
        self.monitoring_active = False
        
    async def start_monitoring(self, interval_minutes: int = 15):
        """
        Start continuous monitoring service
        15-minute intervals recommended for Twitter API v2 rate limits
        """
        
        self.monitoring_active = True
        
        print("🚀 TWITTER A&R MONITORING SERVICE STARTED")
        print("=" * 45)
        print(f"⚡ Monitoring interval: {interval_minutes} minutes")
        print(f"🎯 Heatseeker integration: {self.heatseeker_url}")
        print(f"📡 API status: Connected to Twitter API v2")
        print()
        
        while self.monitoring_active:
            try:
                # Monitor viral moments
                discoveries = await self.twitter_api.monitor_viral_moments()
                
                # Process discoveries
                if discoveries:
                    await self.process_discoveries(discoveries)
                
                # Wait for next monitoring cycle
                print(f"\n⏰ Next monitoring cycle in {interval_minutes} minutes...")
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                self.monitoring_active = False
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def process_discoveries(self, discoveries: List[Dict]):
        """
        Process discoveries and integrate with Heatseeker system
        """
        
        print(f"\n📊 PROCESSING {len(discoveries)} DISCOVERIES")
        print("=" * 40)
        
        for discovery in discoveries:
            # Extract artist name for Heatseeker verification
            artist_name = discovery["artist_name"]
            
            # Cross-reference with Heatseeker independence verification
            try:
                async with httpx.AsyncClient() as client:
                    verification = await client.get(f"{self.heatseeker_url}/verify/{artist_name}")
                    
                    if verification.status_code == 200:
                        verification_data = verification.json()
                        discovery["heatseeker_verification"] = verification_data
            except:
                discovery["heatseeker_verification"] = {"error": "Verification unavailable"}
            
            # Log discovery with action recommendation
            self.log_discovery(discovery)
    
    def log_discovery(self, discovery: Dict):
        """
        Log discovery with formatted output for A&R team
        """
        
        urgency_emoji = "🚨" if discovery["urgency"] == "IMMEDIATE" else "⚡" if discovery["urgency"] == "HIGH" else "📊"
        
        print(f"\n{urgency_emoji} {discovery['urgency']} PRIORITY")
        print(f"Artist: {discovery['artist_name']} ({discovery['artist_handle']})")
        print(f"Category: {discovery['category']}")
        print(f"Tweet: \"{discovery['tweet_text'][:100]}...\"")
        print(f"Followers: {discovery['followers']:,}")
        print(f"Confidence: {discovery['signals']['confidence']}%")
        print(f"Action: {discovery['next_action']}")
        print(f"URL: {discovery['tweet_url']}")
        
        # Heatseeker verification
        if "heatseeker_verification" in discovery:
            verification = discovery["heatseeker_verification"]
            if "independence_status" in verification:
                print(f"Independence: {verification['independence_status']}")

async def main():
    """
    Twitter A&R Intelligence Setup and Demo
    """
    
    print("🐦 TWITTER API v2 A&R INTELLIGENCE SETUP")
    print("=" * 45)
    print()
    
    # Check for Twitter API Bearer Token
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    
    if not bearer_token:
        print("⚠️  TWITTER API v2 SETUP REQUIRED")
        print()
        print("📋 SETUP STEPS:")
        print("1. Apply for Twitter API v2 access:")
        print("   → https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api")
        print()
        print("2. Create a Twitter Developer Project:")
        print("   → https://developer.twitter.com/en/portal/dashboard")
        print("   → Select 'Research' use case for academic/commercial research")
        print("   → Mention: Music industry A&R intelligence and viral artist discovery")
        print()
        print("3. Generate Bearer Token:")
        print("   → Go to your project settings")
        print("   → Generate Bearer Token for API v2 access")
        print("   → Copy the token (starts with 'AAAAAAAAAAAAAAAAA')")
        print()
        print("4. Set Environment Variable:")
        print("   export TWITTER_BEARER_TOKEN='your_bearer_token_here'")
        print()
        print("5. Run the monitoring service:")
        print("   python twitter_ar_monitoring.py")
        print()
        print("💡 TWITTER API v2 FEATURES FOR A&R:")
        print("   • Real-time search (last 7 days)")
        print("   • 300 requests per 15 minutes")
        print("   • Tweet metadata and user metrics")
        print("   • Geographic and language filtering")
        print("   • Engagement metrics for viral detection")
        print()
        print("🎯 A&R USE CASE JUSTIFICATION:")
        print("   'Music industry A&R intelligence for emerging artist discovery")
        print("   and viral content monitoring for commercial talent acquisition.'")
        return
    
    # Initialize monitoring service
    monitoring_service = TwitterARMonitoringService(bearer_token)
    
    print("✅ Twitter API Bearer Token found")
    print("🚀 Starting A&R monitoring service...")
    print()
    
    # Start monitoring (15-minute intervals)
    await monitoring_service.start_monitoring(interval_minutes=15)

if __name__ == "__main__":
    asyncio.run(main())