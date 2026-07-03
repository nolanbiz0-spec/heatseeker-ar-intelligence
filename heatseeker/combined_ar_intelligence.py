#!/usr/bin/env python3
"""
Combined A&R Intelligence Dashboard
Real-time monitoring of both general viral discovery + tastemaker signals
"""

import asyncio
import httpx
from datetime import datetime
import signal
import sys

# Twitter API credentials
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAADZf8QEAAAAA7nwFfKvf1w1GLVkrcrojIe%2Bb9SA%3DieoEPjowCLGeNHM3hLEt58i8r3x6WcVMfyH1qm1KvNFe7Dsxbv'

class CombinedARIntelligence:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        self.running = False
        
        # Key music scene tastemakers with influence weights
        self.tastemakers = {
            "yeenballin": {"weight": 2.5, "focus": "Breaking artists & scene events"},
            "3trilll": {"weight": 2.0, "focus": "Artist discoveries & discussions"}, 
            "beforeikrash": {"weight": 2.0, "focus": "Viral moments & current events"},
            "kashermike": {"weight": 2.0, "focus": "Music industry insights & discoveries"}
        }
        
        # Combined monitoring queries
        self.queries = {
            "viral_discovery": [
                '("my song went viral" OR "going viral" OR "blew up overnight") -is:retweet',
                '("TikTok viral" OR "viral on TikTok") ("unsigned" OR "independent") -is:retweet'
            ],
            "tastemaker_signals": [
                'from:yeenballin OR from:3trilll OR from:beforeikrash OR from:kashermike ("new artist" OR "unsigned" OR "fire") -is:retweet',
                'from:yeenballin OR from:3trilll OR from:beforeikrash OR from:kashermike ("viral" OR "A&R" OR "label") -is:retweet'
            ],
            "engagement_velocity": [
                '("500 comments" OR "comments going crazy") ("artist" OR "song") -is:retweet',
                '("DMs flooded" OR "phone blowing up") -is:retweet'
            ],
            "competitive_intel": [
                '("A&R reached out" OR "label interest" OR "meeting tomorrow") -is:retweet',
                '("just got signed" OR "record deal") -is:retweet'
            ],
            "post_ken_carson": [
                '("rage rap" OR "experimental trap") ("unsigned" OR "no label") -is:retweet',
                '("Ken Carson type" OR "opium inspired") ("original" OR "my own") -is:retweet'
            ]
        }
    
    async def search_twitter(self, query):
        """Search Twitter API v2 with error handling"""
        url = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            "query": query,
            "max_results": 15,
            "tweet.fields": "author_id,created_at,public_metrics",
            "user.fields": "username,name,public_metrics,description",
            "expansions": "author_id"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    await asyncio.sleep(60)
                    return {"data": []}
                else:
                    return {"data": []}
        except Exception:
            return {"data": []}
    
    async def analyze_discovery(self, tweet, user, category):
        """Analyze tweet for A&R opportunity with category-specific scoring"""
        text = tweet["text"].lower()
        username = user.get("username", "").lower()
        user_desc = user.get("description", "").lower()
        followers = user.get("public_metrics", {}).get("followers_count", 0)
        
        score = 0
        signals = []
        
        # Base category scoring
        category_weights = {
            "viral_discovery": 1.0,
            "tastemaker_signals": 2.0,  # Higher weight for tastemaker posts
            "engagement_velocity": 1.5,
            "competitive_intel": 1.2,
            "post_ken_carson": 1.3
        }
        
        weight = category_weights.get(category, 1.0)
        
        # Tastemaker bonus
        if username in self.tastemakers:
            tastemaker_weight = self.tastemakers[username]["weight"]
            score += 30 * tastemaker_weight
            signals.append(f"tastemaker_{username}")
        
        # Viral indicators
        if any(word in text for word in ["viral", "blew up", "overnight", "crazy"]):
            score += 35 * weight
            signals.append("viral_moment")
        
        # Independence signals
        if any(word in text + user_desc for word in ["unsigned", "independent", "no label"]):
            score += 30 * weight
            signals.append("unsigned_status")
        
        # Engagement velocity (your key insight!)
        if any(phrase in text for phrase in ["500 comments", "comments going crazy", "notifications", "dms flooded"]):
            score += 40 * weight
            signals.append("engagement_velocity")
        
        # Quality endorsement
        if any(word in text for word in ["fire", "heat", "hard", "amazing"]):
            score += 20 * weight
            signals.append("quality_endorsement")
        
        # Industry intelligence
        if any(phrase in text for phrase in ["a&r", "label interest", "signed", "deal"]):
            score += 35 * weight
            signals.append("industry_intel")
        
        # Your A&R sweet spot: 10K-50K followers
        if 10000 <= followers <= 50000:
            score += 25
            signals.append("optimal_range")
        elif followers < 10000 and any(sig in signals for sig in ["viral_moment", "engagement_velocity"]):
            score += 15  # Early discovery bonus
            signals.append("early_discovery")
        
        return {
            "score": score,
            "signals": signals,
            "category": category,
            "followers": followers,
            "priority": "🚨 URGENT" if score > 100 else "⚡ HIGH" if score > 70 else "📊 MEDIUM" if score > 40 else "📍 LOW"
        }
    
    async def monitoring_cycle(self):
        """Complete monitoring cycle across all categories"""
        print(f"\n🔍 COMBINED A&R INTELLIGENCE SCAN - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        all_discoveries = []
        
        for category, queries in self.queries.items():
            print(f"   📊 {category.replace('_', ' ').title()}:")
            
            for i, query in enumerate(queries):
                print(f"      {i+1}/{len(queries)} {query[:60]}...")
                
                results = await self.search_twitter(query)
                tweets = results.get("data", [])
                users = {user["id"]: user for user in results.get("includes", {}).get("users", [])}
                
                for tweet in tweets[:5]:  # Top 5 per query
                    user = users.get(tweet["author_id"], {})
                    analysis = await self.analyze_discovery(tweet, user, category)
                    
                    if analysis["score"] > 30:  # Quality threshold
                        discovery = {
                            "artist": user.get("name", "Unknown"),
                            "handle": f"@{user.get('username', 'unknown')}",
                            "tweet": tweet["text"][:100] + "...",
                            "url": f"https://twitter.com/{user.get('username', 'x')}/status/{tweet['id']}",
                            "engagement": tweet.get("public_metrics", {}).get("like_count", 0) + 
                                        tweet.get("public_metrics", {}).get("retweet_count", 0),
                            **analysis
                        }
                        all_discoveries.append(discovery)
                
                await asyncio.sleep(1.5)  # Rate limiting
        
        # Report top discoveries
        if all_discoveries:
            # Sort by score and priority
            top_discoveries = sorted(all_discoveries, key=lambda x: x["score"], reverse=True)[:10]
            
            print(f"\n🎯 TOP {len(top_discoveries)} A&R OPPORTUNITIES:")
            print("=" * 50)
            
            for i, d in enumerate(top_discoveries):
                print(f"\n{i+1}. {d['priority']} {d['artist']} ({d['handle']})")
                print(f"    Score: {d['score']:.1f}/150 | Category: {d['category'].replace('_', ' ').title()}")
                print(f"    Followers: {d['followers']:,} | Engagement: {d['engagement']}")
                print(f"    Signals: {', '.join(d['signals'])}")
                print(f"    Tweet: \"{d['tweet']}\"")
                print(f"    URL: {d['url']}")
                
            # Summary stats
            urgent = len([d for d in top_discoveries if d["priority"] == "🚨 URGENT"])
            high = len([d for d in top_discoveries if d["priority"] == "⚡ HIGH"])
            
            print(f"\n📊 PRIORITY BREAKDOWN:")
            print(f"   🚨 URGENT: {urgent} (Contact within 6 hours)")
            print(f"   ⚡ HIGH: {high} (Contact within 24 hours)")
            
        else:
            print("   📊 No high-priority discoveries this cycle")
        
        print(f"\n⏰ Next comprehensive scan in 15 minutes...")
        return all_discoveries
    
    async def start_monitoring(self):
        """Start combined A&R intelligence monitoring"""
        self.running = True
        
        print("🚀 COMBINED A&R INTELLIGENCE - LIVE MONITORING")
        print("=" * 60)
        print("🎯 General viral discovery + tastemaker intelligence")
        print("👥 Tastemakers: @yeenballin (2.5x), @3trilll (2.0x), @beforeikrash (2.0x), @kashermike (2.0x)")
        print("📊 Categories: Viral Discovery, Tastemaker Signals, Engagement Velocity,")
        print("              Competitive Intel, Post-Ken Carson Opportunities")
        print("⚡ 15-minute comprehensive monitoring cycles")
        print("\n💡 Press Ctrl+C to stop monitoring")
        
        try:
            while self.running:
                await self.monitoring_cycle()
                
                # Wait 15 minutes between cycles
                for i in range(15 * 60):
                    if not self.running:
                        break
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 MONITORING STOPPED")
            print("📊 Combined A&R Intelligence service ended")
            self.running = False
    
    def stop_monitoring(self):
        """Stop monitoring service"""
        self.running = False

# Signal handler for clean shutdown
monitor = CombinedARIntelligence()

def signal_handler(sig, frame):
    print("\n🛑 Shutting down Combined A&R Intelligence...")
    monitor.stop_monitoring()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

async def main():
    """Main entry point"""
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())