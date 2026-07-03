#!/usr/bin/env python3
"""
Youth Twitter Sentiment Consolidation Dashboard
Real-time monitoring of what the kids think - critical for A&R decisions
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re

# Twitter API credentials  
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAADZf8QEAAAAA7nwFfKvf1w1GLVkrcrojIe%2Bb9SA%3DieoEPjowCLGeNHM3hLEt58i8r3x6WcVMfyH1qm1KvNFe7Dsxbv'

class YouthSentimentDashboard:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Current tastemaker network (proven sources)
        self.core_tastemakers = ["yeenballin", "3trilll", "beforeikrash", "kashermike"]
        
        # New high-potential tastemakers from scene discovery
        self.emerging_tastemakers = [
            "kevvwill",      # 100/100 score - Pop culture & scene connected
            "madeinny",      # 85/100 - NYC music scene official
            "bobbymahers",   # 85/100 - Music industry insights  
            "bitgogc",       # 85/100 - Global music media platform
            "lovell_d4d"     # 70/100 - Artist development & Lagos scene
        ]
        
        # Youth sentiment monitoring queries - what kids really think
        self.youth_monitoring_queries = {
            "artist_hype": [
                '("this artist" OR "this rapper" OR "this singer") ("fire" OR "hard" OR "amazing") -is:retweet',
                '("discovered" OR "found out about") (artist OR rapper OR singer) -is:retweet',
                '("my new favorite" OR "obsessed with") (artist OR song OR album) -is:retweet'
            ],
            "breakthrough_signals": [
                '("about to blow up" OR "next big thing" OR "gonna be huge") -is:retweet',
                '("before they famous" OR "before they blow") -is:retweet', 
                '("underground" OR "underrated") ("needs recognition" OR "slept on") -is:retweet'
            ],
            "negative_sentiment": [
                '("overrated" OR "overhyped" OR "not that good") (artist OR rapper OR singer) -is:retweet',
                '("used to be good" OR "fell off" OR "not the same") -is:retweet',
                '("industry plant" OR "fake" OR "manufactured") -is:retweet'
            ],
            "platform_momentum": [
                '("tiktok famous" OR "viral on tiktok") (artist OR song) -is:retweet',
                '("spotify algorithm" OR "for you page") (discovered OR found) -is:retweet',
                '("instagram reels" OR "youtube shorts") (music OR artist) -is:retweet'
            ],
            "scene_discussions": [
                '("atlanta scene" OR "chicago scene" OR "nyc scene" OR "la scene") -is:retweet',
                '("local artist" OR "hometown hero" OR "our city") -is:retweet',
                '("underground scene" OR "indie scene") -is:retweet'
            ]
        }
        
        # Youth demographic filters (age-specific language patterns)
        self.youth_indicators = [
            "no cap", "lowkey", "highkey", "periodt", "slaps", "hits different",
            "fr fr", "deadass", "bet", "finna", "boutta", "sus", "cap",
            "respectfully", "not me", "the way", "pov:", "main character",
            "living rent free", "sending me", "down bad", "its giving"
        ]
    
    async def search_twitter_advanced(self, query, max_results=30):
        """Advanced Twitter search with enhanced filtering"""
        url = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": "author_id,created_at,public_metrics,context_annotations,lang",
            "user.fields": "username,name,public_metrics,description,verified,created_at",
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
    
    def is_youth_voice(self, text, user_data):
        """Identify if this is likely a young person's voice"""
        text_lower = text.lower()
        bio_lower = user_data.get("description", "").lower()
        
        youth_score = 0
        
        # Language patterns
        youth_words = sum(1 for indicator in self.youth_indicators if indicator in text_lower)
        youth_score += youth_words * 10
        
        # Account age (newer accounts more likely to be young users)
        created_at = user_data.get("created_at")
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                years_old = (datetime.now().timestamp() - created_date.timestamp()) / (365.25 * 24 * 3600)
                if years_old < 3:  # Account less than 3 years old
                    youth_score += 15
            except:
                pass
        
        # Follower patterns (not too established)
        followers = user_data.get("public_metrics", {}).get("followers_count", 0)
        if 50 <= followers <= 5000:  # Sweet spot for authentic young voices
            youth_score += 20
        
        # Bio indicators
        if any(word in bio_lower for word in ["student", "college", "uni", "school", "teen", "young"]):
            youth_score += 25
        
        # Music enthusiasm indicators
        if any(word in bio_lower for word in ["music", "stan", "fan", "lover", "addict"]):
            youth_score += 15
        
        return youth_score > 30
    
    def extract_artist_sentiment(self, text):
        """Extract artist names and associated sentiment"""
        text_lower = text.lower()
        
        # Positive sentiment indicators
        positive_words = ["fire", "hard", "amazing", "incredible", "love", "obsessed", 
                         "slaps", "hits different", "talent", "underrated", "genius"]
        
        # Negative sentiment indicators  
        negative_words = ["overrated", "trash", "mid", "fell off", "not good", "overhyped",
                         "fake", "industry plant", "boring", "generic", "cringe"]
        
        # Breakthrough prediction indicators
        breakthrough_words = ["blow up", "next big", "gonna be huge", "about to", "before they famous"]
        
        sentiment_score = 0
        signals = []
        
        for word in positive_words:
            if word in text_lower:
                sentiment_score += 1
                signals.append(f"positive_{word.replace(' ', '_')}")
        
        for word in negative_words:
            if word in text_lower:
                sentiment_score -= 1
                signals.append(f"negative_{word.replace(' ', '_')}")
        
        for phrase in breakthrough_words:
            if phrase in text_lower:
                sentiment_score += 2  # Breakthrough predictions are valuable
                signals.append(f"breakthrough_{phrase.replace(' ', '_')}")
        
        return sentiment_score, signals
    
    async def monitor_youth_sentiment(self):
        """Complete youth sentiment monitoring cycle"""
        print(f"\n🧒 YOUTH SENTIMENT MONITORING - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 55)
        print("🎯 What the kids think determines an artist's career trajectory")
        print()
        
        all_youth_signals = []
        artist_sentiment_tracker = defaultdict(list)
        category_results = {}
        
        for category, queries in self.youth_monitoring_queries.items():
            print(f"📊 {category.replace('_', ' ').title()}:")
            category_signals = []
            
            for i, query in enumerate(queries):
                print(f"   {i+1}/{len(queries)} {query[:50]}...")
                
                results = await self.search_twitter_advanced(query)
                tweets = results.get("data", [])
                users = {user["id"]: user for user in results.get("includes", {}).get("users", [])}
                
                for tweet in tweets:
                    user = users.get(tweet["author_id"], {})
                    text = tweet["text"]
                    
                    # Filter for authentic youth voices
                    if self.is_youth_voice(text, user):
                        sentiment_score, sentiment_signals = self.extract_artist_sentiment(text)
                        
                        youth_signal = {
                            "category": category,
                            "text": text[:150] + "...",
                            "user": user.get("name", "Unknown"),
                            "handle": f"@{user.get('username', 'unknown')}",
                            "followers": user.get("public_metrics", {}).get("followers_count", 0),
                            "engagement": tweet.get("public_metrics", {}).get("like_count", 0),
                            "sentiment_score": sentiment_score,
                            "signals": sentiment_signals,
                            "youth_authenticity": "high",
                            "timestamp": tweet.get("created_at", ""),
                            "url": f"https://twitter.com/{user.get('username', 'x')}/status/{tweet['id']}"
                        }
                        
                        category_signals.append(youth_signal)
                        all_youth_signals.append(youth_signal)
                
                await asyncio.sleep(2)  # Rate limiting
            
            category_results[category] = category_signals
            print(f"      ✅ {len(category_signals)} authentic youth voices captured")
        
        # Analysis and reporting
        await self.generate_youth_sentiment_report(all_youth_signals, category_results)
        
        return all_youth_signals
    
    async def generate_youth_sentiment_report(self, all_signals, category_results):
        """Generate actionable youth sentiment intelligence report"""
        print(f"\n" + "="*70)
        print("🔥 YOUTH SENTIMENT INTELLIGENCE - A&R DECISION SUPPORT")
        print("="*70)
        
        # Top positive sentiment (potential signings)
        positive_signals = [s for s in all_signals if s["sentiment_score"] > 0]
        positive_signals.sort(key=lambda x: x["sentiment_score"] + (x["engagement"]/10), reverse=True)
        
        print(f"\n🚨 HIGH-POSITIVE YOUTH SENTIMENT (Signing Opportunities):")
        print("-" * 50)
        for i, signal in enumerate(positive_signals[:5]):
            print(f"\n{i+1}. {signal['user']} ({signal['handle']}) | {signal['followers']:,} followers")
            print(f"   Sentiment: +{signal['sentiment_score']} | Engagement: {signal['engagement']}")
            print(f"   Signals: {', '.join(signal['signals'])}")
            print(f"   Tweet: \"{signal['text']}\"")
            print(f"   URL: {signal['url']}")
        
        # Breakthrough predictions (early discovery)
        breakthrough_signals = [s for s in all_signals if any("breakthrough" in sig for sig in s["signals"])]
        breakthrough_signals.sort(key=lambda x: x["engagement"], reverse=True)
        
        print(f"\n⚡ BREAKTHROUGH PREDICTIONS FROM YOUTH ({len(breakthrough_signals)} total):")
        print("-" * 45)
        for i, signal in enumerate(breakthrough_signals[:3]):
            print(f"\n{i+1}. {signal['user']} predicting breakthrough")
            print(f"   \"{signal['text']}\"")
            print(f"   Engagement: {signal['engagement']} | URL: {signal['url']}")
        
        # Negative sentiment warnings (avoid signings)
        negative_signals = [s for s in all_signals if s["sentiment_score"] < 0]
        negative_signals.sort(key=lambda x: abs(x["sentiment_score"]), reverse=True)
        
        print(f"\n⚠️  NEGATIVE YOUTH SENTIMENT WARNINGS ({len(negative_signals)} total):")
        print("-" * 40)
        for i, signal in enumerate(negative_signals[:3]):
            print(f"\n{i+1}. {signal['user']} - Negative sentiment detected")
            print(f"   Sentiment: {signal['sentiment_score']} | Signals: {', '.join(signal['signals'])}")
            print(f"   \"{signal['text']}\"")
        
        # Platform momentum analysis
        platform_signals = category_results.get("platform_momentum", [])
        print(f"\n📱 PLATFORM MOMENTUM INSIGHTS ({len(platform_signals)} signals):")
        print("-" * 35)
        for signal in platform_signals[:3]:
            print(f"   • {signal['text'][:100]}...")
        
        # Scene intelligence
        scene_signals = category_results.get("scene_discussions", [])
        print(f"\n🏙️  SCENE DISCUSSIONS ({len(scene_signals)} signals):")
        print("-" * 25)
        for signal in scene_signals[:3]:
            print(f"   • {signal['text'][:100]}...")
        
        # A&R Action Items
        print(f"\n🎯 A&R ACTION ITEMS:")
        print("-" * 20)
        print(f"🚨 IMMEDIATE: Investigate {len(positive_signals)} artists with positive youth sentiment")
        print(f"⚡ EARLY DISCOVERY: Monitor {len(breakthrough_signals)} breakthrough predictions")  
        print(f"⚠️  AVOID: {len(negative_signals)} artists with negative youth sentiment")
        print(f"📊 TOTAL YOUTH VOICES: {len(all_signals)} authentic signals captured")
        
        return {
            "positive_opportunities": len(positive_signals),
            "breakthrough_predictions": len(breakthrough_signals),
            "negative_warnings": len(negative_signals),
            "total_youth_voices": len(all_signals)
        }
    
    async def continuous_youth_monitoring(self):
        """Run continuous youth sentiment monitoring"""
        print("🚀 YOUTH SENTIMENT DASHBOARD - CONTINUOUS MONITORING")
        print("=" * 55)
        print("🧒 Real-time tracking of what young people think about artists")
        print("🎯 Youth opinion determines signing success - monitoring critical sentiment")
        print("⚡ 20-minute monitoring cycles for rapid sentiment detection")
        print("\n💡 Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                await self.monitor_youth_sentiment()
                
                print(f"\n⏰ Next youth sentiment scan in 20 minutes...")
                print("📊 Tracking authentic youth voices for A&R intelligence")
                
                # Wait 20 minutes between cycles
                for i in range(20 * 60):
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 YOUTH SENTIMENT MONITORING STOPPED")
            print("📊 Youth sentiment dashboard ended")

async def main():
    """Start youth sentiment monitoring dashboard"""
    dashboard = YouthSentimentDashboard()
    await dashboard.continuous_youth_monitoring()

if __name__ == "__main__":
    asyncio.run(main())