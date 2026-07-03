#!/usr/bin/env python3
"""
Tastemaker A&R Intelligence System
Monitor key music scene Twitter accounts for real-time artist discovery
"""

import asyncio
import httpx
import json
import os
from datetime import datetime

# Twitter API credentials
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAADZf8QEAAAAA7nwFfKvf1w1GLVkrcrojIe%2Bb9SA%3DieoEPjowCLGeNHM3hLEt58i8r3x6WcVMfyH1qm1KvNFe7Dsxbv'

class TastemakerMonitor:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Key music scene tastemakers
        self.tastemakers = {
            "yeenballin": {
                "handle": "@yeenballin",
                "focus": "Current music scene events & breaking artists",
                "weight": 2.5,  # High influence multiplier
                "url": "https://x.com/yeenballin"
            },
            "3trilll": {
                "handle": "@3trilll", 
                "focus": "Music scene discussions & artist discoveries",
                "weight": 2.0,
                "url": "https://x.com/3trilll"
            },
            "beforeikrash": {
                "handle": "@beforeikrash",
                "focus": "Music scene current events & viral moments", 
                "weight": 2.0,
                "url": "https://x.com/beforeikrash"
            }
        }
        
        # A&R-focused search queries for tastemaker posts
        self.tastemaker_queries = [
            # Direct mentions of discovery
            'from:yeenballin OR from:3trilll OR from:beforeikrash ("new artist" OR "unsigned" OR "independent") -is:retweet',
            'from:yeenballin OR from:3trilll OR from:beforeikrash ("viral" OR "blew up" OR "going crazy") -is:retweet',
            'from:yeenballin OR from:3trilll OR from:beforeikrash ("fire" OR "heat" OR "hard") (artist OR song) -is:retweet',
            
            # Industry intelligence  
            'from:yeenballin OR from:3trilll OR from:beforeikrash ("A&R" OR "label" OR "signed") -is:retweet',
            'from:yeenballin OR from:3trilll OR from:beforeikrash ("TikTok" OR "trending" OR "charts") -is:retweet',
            
            # Scene monitoring
            'from:yeenballin OR from:3trilll OR from:beforeikrash ("Atlanta" OR "NYC" OR "LA" OR "Chicago") (music OR scene) -is:retweet',
            'from:yeenballin OR from:3trilll OR from:beforeikrash ("rage rap" OR "drill" OR "bedroom pop" OR "experimental") -is:retweet'
        ]
    
    async def get_tastemaker_posts(self, query):
        """Fetch posts from tastemaker accounts"""
        url = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            "query": query,
            "max_results": 20,
            "tweet.fields": "author_id,created_at,public_metrics,context_annotations",
            "user.fields": "username,name,public_metrics,description",
            "expansions": "author_id"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    print(f"⚠️  Rate limit hit. Waiting...")
                    await asyncio.sleep(60)
                    return {"data": []}
                else:
                    return {"data": []}
        except Exception as e:
            return {"data": []}
    
    async def analyze_tastemaker_post(self, tweet, user):
        """Analyze tastemaker post for A&R intelligence"""
        text = tweet["text"].lower()
        username = user.get("username", "").lower()
        
        # Get tastemaker weight
        tastemaker_weight = self.tastemakers.get(username, {}).get("weight", 1.0)
        
        score = 0
        signals = []
        
        # Artist discovery signals
        if any(phrase in text for phrase in ["new artist", "unsigned", "independent", "no label"]):
            score += 40 * tastemaker_weight
            signals.append("artist_discovery")
        
        # Viral moment detection
        if any(phrase in text for phrase in ["viral", "blew up", "going crazy", "trending"]):
            score += 35 * tastemaker_weight  
            signals.append("viral_moment")
        
        # Quality endorsement
        if any(word in text for word in ["fire", "heat", "hard", "amazing", "incredible"]):
            score += 25 * tastemaker_weight
            signals.append("quality_endorsement")
        
        # Industry intelligence
        if any(phrase in text for phrase in ["a&r", "label interest", "signed", "deal"]):
            score += 30 * tastemaker_weight
            signals.append("industry_intel")
        
        # Platform mentions (TikTok, etc.)
        if any(platform in text for platform in ["tiktok", "youtube", "soundcloud", "spotify"]):
            score += 15 * tastemaker_weight
            signals.append("platform_momentum")
        
        # Genre/scene signals
        if any(genre in text for genre in ["rage rap", "drill", "bedroom pop", "experimental", "trap"]):
            score += 20 * tastemaker_weight
            signals.append("genre_trend")
        
        return {
            "score": score,
            "signals": signals,
            "tastemaker": username,
            "weight": tastemaker_weight,
            "priority": "🚨 URGENT" if score > 80 else "⚡ HIGH" if score > 50 else "📊 MEDIUM"
        }
    
    async def monitor_tastemakers(self):
        """Monitor all tastemaker accounts for A&R intelligence"""
        print(f"\n🎯 TASTEMAKER A&R INTELLIGENCE SCAN - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 55)
        print("👥 Monitoring: @yeenballin, @3trilll, @beforeikrash")
        print()
        
        discoveries = []
        
        for i, query in enumerate(self.tastemaker_queries):
            print(f"   {i+1}/7 Scanning: {query[:50]}...")
            
            results = await self.get_tastemaker_posts(query)
            tweets = results.get("data", [])
            users = {user["id"]: user for user in results.get("includes", {}).get("users", [])}
            
            for tweet in tweets:
                user = users.get(tweet["author_id"], {})
                analysis = await self.analyze_tastemaker_post(tweet, user)
                
                if analysis["score"] > 30:  # Lower threshold for tastemakers
                    discovery = {
                        "tastemaker": f"@{analysis['tastemaker']}",
                        "tweet": tweet["text"][:120] + "...",
                        "url": f"https://twitter.com/{user.get('username', 'x')}/status/{tweet['id']}",
                        "created_at": tweet["created_at"],
                        "engagement": tweet.get("public_metrics", {}).get("like_count", 0) + 
                                    tweet.get("public_metrics", {}).get("retweet_count", 0),
                        **analysis
                    }
                    discoveries.append(discovery)
            
            await asyncio.sleep(2)  # Rate limiting
        
        # Report discoveries
        if discoveries:
            print(f"\n🔍 FOUND {len(discoveries)} TASTEMAKER SIGNALS:")
            
            # Sort by score (weighted by tastemaker influence)
            for d in sorted(discoveries, key=lambda x: x["score"], reverse=True)[:8]:
                print(f"\n{d['priority']} {d['tastemaker']} (Weight: {d['weight']}x)")
                print(f"   Score: {d['score']:.1f}/100 | Engagement: {d['engagement']}")
                print(f"   Signals: {', '.join(d['signals'])}")
                print(f"   Tweet: \"{d['tweet']}\"")
                print(f"   URL: {d['url']}")
                
        else:
            print("   📊 No high-priority tastemaker signals this cycle")
        
        print(f"\n⏰ Next tastemaker scan in 10 minutes...")
        return discoveries
    
    async def start_monitoring(self):
        """Start continuous tastemaker monitoring"""
        print("🎯 TASTEMAKER A&R INTELLIGENCE - LIVE MONITORING")
        print("=" * 55)
        print("👥 Key Accounts:")
        for username, info in self.tastemakers.items():
            print(f"   • {info['handle']} - {info['focus']} (Weight: {info['weight']}x)")
        print()
        print("🔍 Monitoring for: artist discoveries, viral moments, industry intel")
        print("⚡ 10-minute monitoring cycles (faster for tastemakers)")
        print("🚨 Weighted scoring based on tastemaker influence")
        print("\n💡 Press Ctrl+C to stop monitoring")
        print()
        
        try:
            while True:
                await self.monitor_tastemakers()
                
                # Wait 10 minutes between cycles (faster than general monitoring)
                for i in range(10 * 60):
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 TASTEMAKER MONITORING STOPPED")
            print("📊 Tastemaker A&R Intelligence service ended")

async def main():
    """Main entry point for tastemaker monitoring"""
    monitor = TastemakerMonitor()
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())