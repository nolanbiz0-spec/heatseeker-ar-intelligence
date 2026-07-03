#!/usr/bin/env python3
"""
Live Twitter A&R Intelligence Monitoring - Background Service
Real-time viral artist discovery running 24/7
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
import signal
import sys

# Load credentials
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAADZf8QEAAAAA7nwFfKvf1w1GLVkrcrojIe%2Bb9SA%3DieoEPjowCLGeNHM3hLEt58i8r3x6WcVMfyH1qm1KvNFe7Dsxbv'

class TwitterARMonitor:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        self.running = False
        
        # A&R-optimized queries for real-time discovery
        self.queries = [
            '("my song went viral" OR "going viral" OR "blew up overnight") -is:retweet',
            '("TikTok viral" OR "viral on TikTok") ("unsigned" OR "independent") -is:retweet',
            '("500 comments" OR "comments going crazy") ("artist" OR "song") -is:retweet',
            '("A&R reached out" OR "label interest") -is:retweet',
            '("rage rap" OR "experimental trap") ("unsigned" OR "no label") -is:retweet',
            '("#ATLmusic" OR "#ATLunderground") ("unsigned" OR "independent") -is:retweet'
        ]
    
    async def search_twitter(self, query):
        """Search Twitter API v2 for A&R intelligence"""
        url = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            "query": query,
            "max_results": 10,
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
                    print(f"⚠️  Rate limit hit. Waiting 15 minutes...")
                    await asyncio.sleep(15 * 60)
                    return {"data": []}
                else:
                    print(f"❌ API error: {response.status_code}")
                    return {"data": []}
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {"data": []}
    
    async def analyze_discovery(self, tweet, user):
        """Analyze tweet for A&R opportunity signals"""
        text = tweet["text"].lower()
        user_desc = user.get("description", "").lower()
        followers = user.get("public_metrics", {}).get("followers_count", 0)
        
        # A&R scoring
        score = 0
        signals = []
        
        # Viral indicators
        if any(word in text for word in ["viral", "blew up", "overnight", "crazy"]):
            score += 30
            signals.append("viral_moment")
        
        # Independence signals  
        if any(word in text + user_desc for word in ["unsigned", "independent", "no label"]):
            score += 25
            signals.append("unsigned_status")
        
        # Engagement velocity (your key insight!)
        if any(phrase in text for phrase in ["500 comments", "comments going crazy", "notifications"]):
            score += 35
            signals.append("engagement_velocity")
        
        # Your A&R sweet spot: 10K-50K followers
        if 10000 <= followers <= 50000:
            score += 20
            signals.append("optimal_range")
        
        return {
            "score": score,
            "signals": signals,
            "followers": followers,
            "priority": "🚨 IMMEDIATE" if score > 70 else "⚡ HIGH" if score > 50 else "📊 MEDIUM"
        }
    
    async def monitor_cycle(self):
        """Single monitoring cycle - checks all queries"""
        print(f"\n🔍 TWITTER A&R SCAN - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 45)
        
        discoveries = []
        
        for i, query in enumerate(self.queries):
            print(f"   {i+1}/6 Scanning: {query[:40]}...")
            
            results = await self.search_twitter(query)
            tweets = results.get("data", [])
            users = {user["id"]: user for user in results.get("includes", {}).get("users", [])}
            
            for tweet in tweets[:3]:  # Top 3 per query
                user = users.get(tweet["author_id"], {})
                analysis = await self.analyze_discovery(tweet, user)
                
                if analysis["score"] > 40:  # Only significant discoveries
                    discovery = {
                        "artist": user.get("name", "Unknown"),
                        "handle": f"@{user.get('username', 'unknown')}",
                        "tweet": tweet["text"][:100] + "...",
                        "url": f"https://twitter.com/{user.get('username', 'x')}/status/{tweet['id']}",
                        **analysis
                    }
                    discoveries.append(discovery)
            
            await asyncio.sleep(2)  # Rate limiting
        
        # Report discoveries
        if discoveries:
            print(f"\n🎯 FOUND {len(discoveries)} A&R OPPORTUNITIES:")
            for d in sorted(discoveries, key=lambda x: x["score"], reverse=True)[:5]:
                print(f"\n{d['priority']} {d['artist']} ({d['handle']})")
                print(f"   Score: {d['score']}/100 | Followers: {d['followers']:,}")
                print(f"   Signals: {', '.join(d['signals'])}")
                print(f"   Tweet: \"{d['tweet']}\"")
                print(f"   URL: {d['url']}")
        else:
            print("   📊 No high-priority discoveries this cycle")
        
        print(f"\n⏰ Next scan in 15 minutes...")
    
    async def start_monitoring(self):
        """Start continuous 24/7 monitoring"""
        self.running = True
        
        print("🚀 TWITTER A&R INTELLIGENCE - LIVE MONITORING")
        print("=" * 50)
        print("🎯 Searching for viral breakthrough moments...")
        print("🎵 Targeting unsigned artists in optimal range (10K-50K)")
        print("⚡ 15-minute monitoring cycles")
        print("🚨 Real-time alerts for IMMEDIATE opportunities")
        print("\n💡 Press Ctrl+C to stop monitoring")
        print()
        
        try:
            while self.running:
                await self.monitor_cycle()
                
                # Wait 15 minutes between cycles
                for i in range(15 * 60):
                    if not self.running:
                        break
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 MONITORING STOPPED")
            print("📊 Twitter A&R Intelligence service ended")
            self.running = False
    
    def stop_monitoring(self):
        """Stop the monitoring service"""
        self.running = False

# Signal handler for clean shutdown
monitor = TwitterARMonitor()

def signal_handler(sig, frame):
    print("\n🛑 Shutting down Twitter A&R monitoring...")
    monitor.stop_monitoring()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

async def main():
    """Main entry point"""
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())