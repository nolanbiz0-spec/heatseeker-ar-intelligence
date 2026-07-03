#!/usr/bin/env python3
"""
Scene Discovery & Youth Sentiment Analysis for A&R Intelligence
Find who the kids are talking about + discover new tastemaker accounts to monitor
"""

import asyncio
import httpx
import json
from datetime import datetime
import re
from collections import Counter

# Twitter API credentials
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAADZf8QEAAAAA7nwFfKvf1w1GLVkrcrojIe%2Bb9SA%3DieoEPjowCLGeNHM3hLEt58i8r3x6WcVMfyH1qm1KvNFe7Dsxbv'

class SceneIntelligence:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Current tastemaker network
        self.known_tastemakers = ["yeenballin", "3trilll", "beforeikrash", "kashermike"]
        
        # Youth sentiment discovery queries
        self.youth_sentiment_queries = [
            # What kids are saying about artists
            '("he fire" OR "she fire" OR "they fire") ("artist" OR "rapper" OR "singer") -is:retweet',
            '("this artist" OR "this rapper") ("underrated" OR "slept on" OR "needs more recognition") -is:retweet',
            '("discovered" OR "found") ("new artist" OR "underground artist") -is:retweet',
            
            # Youth discovery patterns
            '("my new favorite" OR "obsessed with") ("artist" OR "song") -is:retweet',
            '("everyone needs to listen" OR "y\'all sleeping on") -is:retweet',
            '("about to blow up" OR "next up" OR "gonna be huge") -is:retweet',
            
            # Gen Z music opinions
            '("this generation" OR "our generation") ("music" OR "artists") -is:retweet',
            '("tiktok made me" OR "found on tiktok") ("discover" OR "listen") -is:retweet',
            '("playlist" OR "spotify wrapped") ("underground" OR "indie" OR "unsigned") -is:retweet'
        ]
        
        # Scene account discovery queries
        self.tastemaker_discovery_queries = [
            # Find accounts that discuss music frequently
            '("music blog" OR "music curator" OR "playlist curator") -is:retweet',
            '("underground music" OR "indie music" OR "music discovery") -is:retweet',
            '("new music friday" OR "music recommendations") -is:retweet',
            
            # Find influencers in music scenes
            '("music scene" OR "local scene") ("atlanta" OR "chicago" OR "nyc" OR "la") -is:retweet',
            '("a&r" OR "talent scout" OR "music industry") -is:retweet',
            '("breaking artist" OR "emerging artist") -is:retweet'
        ]
    
    async def search_twitter(self, query, max_results=25):
        """Enhanced Twitter search with user data"""
        url = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": "author_id,created_at,public_metrics,context_annotations",
            "user.fields": "username,name,public_metrics,description,verified",
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
    
    def extract_artist_mentions(self, text):
        """Extract potential artist names from tweets"""
        # Common patterns for artist mentions
        patterns = [
            r'@(\w+)',  # @mentions
            r'"([^"]{2,25})"',  # Quoted names
            r'listen to ([A-Za-z\s]{2,25})',  # "listen to X"
            r'([A-Za-z\s]{2,25}) is fire',  # "X is fire"
            r'([A-Za-z\s]{2,25}) about to blow',  # "X about to blow"
        ]
        
        mentions = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            mentions.extend([m.strip() for m in matches if len(m.strip()) > 2])
        
        return mentions
    
    async def analyze_youth_sentiment(self):
        """Analyze what young people are saying about artists"""
        print("\n🔍 YOUTH SENTIMENT ANALYSIS - WHO THE KIDS ARE TALKING ABOUT")
        print("=" * 65)
        
        artist_mentions = Counter()
        sentiment_data = []
        
        for i, query in enumerate(self.youth_sentiment_queries):
            print(f"   {i+1}/9 Scanning youth sentiment: {query[:50]}...")
            
            results = await self.search_twitter(query)
            tweets = results.get("data", [])
            users = {user["id"]: user for user in results.get("includes", {}).get("users", [])}
            
            for tweet in tweets:
                user = users.get(tweet["author_id"], {})
                text = tweet["text"]
                
                # Extract artist mentions
                mentions = self.extract_artist_mentions(text)
                for mention in mentions:
                    artist_mentions[mention] += 1
                
                # Analyze sentiment context
                sentiment_signals = []
                if any(word in text.lower() for word in ["fire", "amazing", "incredible", "love"]):
                    sentiment_signals.append("positive")
                if any(word in text.lower() for word in ["underrated", "slept on", "needs recognition"]):
                    sentiment_signals.append("discovery_opportunity")
                if any(word in text.lower() for word in ["about to blow", "next up", "gonna be huge"]):
                    sentiment_signals.append("breakthrough_prediction")
                
                if sentiment_signals:
                    sentiment_data.append({
                        "text": text[:120] + "...",
                        "user": user.get("name", "Unknown"),
                        "handle": f"@{user.get('username', 'unknown')}",
                        "followers": user.get("public_metrics", {}).get("followers_count", 0),
                        "engagement": tweet.get("public_metrics", {}).get("like_count", 0),
                        "signals": sentiment_signals,
                        "mentions": mentions
                    })
            
            await asyncio.sleep(2)
        
        return artist_mentions, sentiment_data
    
    async def discover_new_tastemakers(self):
        """Find new accounts to add to tastemaker monitoring"""
        print("\n🔍 DISCOVERING NEW SCENE TASTEMAKER ACCOUNTS")
        print("=" * 50)
        
        potential_tastemakers = []
        
        for i, query in enumerate(self.tastemaker_discovery_queries):
            print(f"   {i+1}/6 Searching for scene accounts: {query[:45]}...")
            
            results = await self.search_twitter(query)
            tweets = results.get("data", [])
            users = {user["id"]: user for user in results.get("includes", {}).get("users", [])}
            
            for tweet in tweets:
                user = users.get(tweet["author_id"], {})
                username = user.get("username", "").lower()
                
                # Skip if already monitoring
                if username in self.known_tastemakers:
                    continue
                
                # Score potential tastemaker
                score = 0
                signals = []
                
                followers = user.get("public_metrics", {}).get("followers_count", 0)
                description = user.get("description", "").lower()
                text = tweet["text"].lower()
                
                # Follower sweet spot (not too big, not too small)
                if 1000 <= followers <= 100000:
                    score += 20
                    signals.append("good_reach")
                
                # Music industry keywords in bio
                if any(word in description for word in ["music", "a&r", "playlist", "curator", "blog", "dj"]):
                    score += 30
                    signals.append("music_focus")
                
                # Discovery/scene language
                if any(phrase in text + description for phrase in ["underground", "emerging", "new artist", "scene"]):
                    score += 25
                    signals.append("discovery_focused")
                
                # Engagement quality
                engagement = tweet.get("public_metrics", {}).get("like_count", 0) + tweet.get("public_metrics", {}).get("retweet_count", 0)
                if engagement > 10:
                    score += 15
                    signals.append("good_engagement")
                
                # Geographic scene indicators
                if any(city in text + description for city in ["atlanta", "chicago", "nyc", "la", "miami", "houston"]):
                    score += 10
                    signals.append("scene_connected")
                
                if score > 40:  # Quality threshold
                    potential_tastemakers.append({
                        "username": username,
                        "handle": f"@{username}",
                        "name": user.get("name", "Unknown"),
                        "followers": followers,
                        "description": user.get("description", "")[:100] + "...",
                        "score": score,
                        "signals": signals,
                        "sample_tweet": tweet["text"][:100] + "..."
                    })
            
            await asyncio.sleep(2)
        
        return sorted(potential_tastemakers, key=lambda x: x["score"], reverse=True)
    
    async def generate_scene_intelligence_report(self):
        """Generate comprehensive scene intelligence for A&R decisions"""
        print("🎯 GENERATING SCENE INTELLIGENCE REPORT")
        print("=" * 45)
        print("📊 Analyzing youth sentiment + discovering new tastemaker accounts...")
        print()
        
        # Get youth sentiment data
        artist_mentions, sentiment_data = await self.analyze_youth_sentiment()
        
        # Discover new tastemakers
        potential_tastemakers = await self.discover_new_tastemakers()
        
        # Generate report
        print("\n" + "="*70)
        print("🔥 SCENE INTELLIGENCE REPORT - YOUTH SENTIMENT & TASTEMAKER DISCOVERY")
        print("="*70)
        
        # Top artist mentions from youth
        print(f"\n🎵 TOP ARTISTS THE KIDS ARE TALKING ABOUT:")
        print("-" * 40)
        for artist, count in artist_mentions.most_common(10):
            if len(artist) > 2 and artist.lower() not in ["music", "song", "artist", "rapper"]:
                print(f"   {count}x mentions: {artist}")
        
        # High-signal youth sentiment
        print(f"\n💬 HIGH-SIGNAL YOUTH SENTIMENT (Top 8):")
        print("-" * 35)
        top_sentiment = sorted(sentiment_data, key=lambda x: x["engagement"], reverse=True)[:8]
        for i, s in enumerate(top_sentiment):
            print(f"\n{i+1}. {s['user']} ({s['handle']}) | {s['followers']:,} followers")
            print(f"   Signals: {', '.join(s['signals'])}")
            print(f"   Mentions: {s['mentions']}")
            print(f"   Tweet: \"{s['text']}\"")
        
        # New tastemaker recommendations
        print(f"\n👥 NEW TASTEMAKER ACCOUNTS TO MONITOR (Top 10):")
        print("-" * 45)
        for i, tm in enumerate(potential_tastemakers[:10]):
            print(f"\n{i+1}. {tm['handle']} - {tm['name']}")
            print(f"   Score: {tm['score']}/100 | Followers: {tm['followers']:,}")
            print(f"   Signals: {', '.join(tm['signals'])}")
            print(f"   Bio: \"{tm['description']}\"")
            print(f"   Sample: \"{tm['sample_tweet']}\"")
        
        # A&R Recommendations
        print(f"\n🎯 A&R INTELLIGENCE RECOMMENDATIONS:")
        print("-" * 35)
        
        breakthrough_predictions = [s for s in sentiment_data if "breakthrough_prediction" in s["signals"]]
        discovery_opportunities = [s for s in sentiment_data if "discovery_opportunity" in s["signals"]]
        
        print(f"🚨 {len(breakthrough_predictions)} breakthrough predictions from youth")
        print(f"💎 {len(discovery_opportunities)} underrated/slept-on artist signals")
        print(f"👥 {len(potential_tastemakers)} new tastemaker accounts identified")
        print(f"📈 Monitor top mentioned artists for signing opportunities")
        
        return {
            "artist_mentions": artist_mentions,
            "sentiment_data": sentiment_data,
            "potential_tastemakers": potential_tastemakers[:15],  # Top 15
            "breakthrough_signals": len(breakthrough_predictions),
            "discovery_opportunities": len(discovery_opportunities)
        }

async def main():
    """Generate scene intelligence report"""
    intelligence = SceneIntelligence()
    report = await intelligence.generate_scene_intelligence_report()
    
    print(f"\n✅ SCENE INTELLIGENCE COMPLETE!")
    print(f"📊 {len(report['potential_tastemakers'])} new tastemaker candidates identified")
    print(f"🎵 {len(report['artist_mentions'])} artist mentions analyzed")
    print(f"💬 {len(report['sentiment_data'])} youth sentiment signals captured")

if __name__ == "__main__":
    asyncio.run(main())