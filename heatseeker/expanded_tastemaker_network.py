#!/usr/bin/env python3
"""
Expanded Tastemaker Network Integration
Adding high-value discovered accounts to monitoring system
"""

import asyncio
import httpx
from datetime import datetime

# Twitter API credentials
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAADZf8QEAAAAA7nwFfKvf1w1GLVkrcrojIe%2Bb9SA%3DieoEPjowCLGeNHM3hLEt58i8r3x6WcVMfyH1qm1KvNFe7Dsxbv'

class ExpandedTastemakerNetwork:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # TIER 1: Original proven tastemakers (highest weight)
        self.tier1_tastemakers = {
            "yeenballin": {"weight": 2.5, "focus": "Breaking artists & scene events", "tier": 1},
            "3trilll": {"weight": 2.0, "focus": "Artist discoveries & discussions", "tier": 1}, 
            "beforeikrash": {"weight": 2.0, "focus": "Viral moments & current events", "tier": 1},
            "kashermike": {"weight": 2.0, "focus": "Music industry insights & discoveries", "tier": 1}
        }
        
        # TIER 2: High-potential discovered tastemakers (medium weight)
        self.tier2_tastemakers = {
            "kevvwill": {"weight": 1.8, "focus": "Pop culture & music scene connections", "tier": 2},
            "madeinny": {"weight": 1.6, "focus": "NYC official music scene intelligence", "tier": 2},
            "bobbymahers": {"weight": 1.5, "focus": "Music industry insights & AI discourse", "tier": 2},
            "bitgogc": {"weight": 1.4, "focus": "Global emerging artist media coverage", "tier": 2},
            "lovell_d4d": {"weight": 1.3, "focus": "Artist development & Lagos scene", "tier": 2}
        }
        
        # Combined monitoring queries for all tiers
        self.expanded_monitoring_queries = {
            "tier1_discovery": [
                'from:yeenballin OR from:3trilll OR from:beforeikrash OR from:kashermike ("new artist" OR "unsigned" OR "fire") -is:retweet',
                'from:yeenballin OR from:3trilll OR from:beforeikrash OR from:kashermike ("viral" OR "A&R" OR "label") -is:retweet',
                'from:yeenballin OR from:3trilll OR from:beforeikrash OR from:kashermike ("about to blow" OR "next big") -is:retweet'
            ],
            "tier2_discovery": [
                'from:kevvwill OR from:madeinny OR from:bobbymahers OR from:bitgogc OR from:lovell_d4d ("artist" OR "music") -is:retweet',
                'from:kevvwill OR from:madeinny OR from:bobbymahers OR from:bitgogc OR from:lovell_d4d ("emerging" OR "underground") -is:retweet',
                'from:kevvwill OR from:madeinny OR from:bobbymahers OR from:bitgogc OR from:lovell_d4d ("scene" OR "discovery") -is:retweet'
            ],
            "cross_tier_validation": [
                # Look for artists mentioned by multiple tiers (high confidence signals)
                '(from:yeenballin OR from:3trilll OR from:beforeikrash OR from:kashermike OR from:kevvwill OR from:madeinny) ("artist" OR "rapper" OR "singer") -is:retweet'
            ]
        }
    
    async def search_twitter(self, query, max_results=20):
        """Twitter API search with enhanced data collection"""
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
    
    async def analyze_tastemaker_discovery(self, tweet, user, tastemaker_tier):
        """Enhanced analysis incorporating tier weighting"""
        text = tweet["text"].lower()
        username = user.get("username", "").lower()
        
        # Get tastemaker data
        all_tastemakers = {**self.tier1_tastemakers, **self.tier2_tastemakers}
        tastemaker_data = all_tastemakers.get(username, {"weight": 1.0, "tier": 3})
        
        score = 0
        signals = []
        
        # Base tastemaker credibility score
        base_score = 40 * tastemaker_data["weight"]  # Higher weight = more credible
        score += base_score
        signals.append(f"tier{tastemaker_data['tier']}_tastemaker")
        
        # Artist discovery language
        if any(phrase in text for phrase in ["new artist", "discovered", "unsigned", "independent"]):
            score += 35 * tastemaker_data["weight"]
            signals.append("artist_discovery")
        
        # Quality endorsement
        if any(word in text for word in ["fire", "incredible", "amazing", "talent", "genius"]):
            score += 30 * tastemaker_data["weight"]
            signals.append("quality_endorsement")
        
        # Breakthrough prediction
        if any(phrase in text for phrase in ["blow up", "next big", "about to", "gonna be huge"]):
            score += 40 * tastemaker_data["weight"]  # Most valuable signal
            signals.append("breakthrough_prediction")
        
        # Industry intelligence
        if any(word in text for word in ["a&r", "label", "signed", "deal", "industry"]):
            score += 25 * tastemaker_data["weight"]
            signals.append("industry_intel")
        
        # Viral moment detection
        if any(word in text for word in ["viral", "trending", "tiktok", "blew up"]):
            score += 30 * tastemaker_data["weight"]
            signals.append("viral_moment")
        
        return {
            "score": score,
            "signals": signals,
            "tastemaker": username,
            "tier": tastemaker_data["tier"],
            "weight": tastemaker_data["weight"],
            "focus": tastemaker_data["focus"]
        }
    
    async def expanded_monitoring_cycle(self):
        """Complete monitoring cycle across expanded tastemaker network"""
        print(f"\n🎯 EXPANDED TASTEMAKER NETWORK SCAN - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        print("👥 TIER 1: @yeenballin, @3trilll, @beforeikrash, @kashermike (2.0-2.5x weight)")
        print("👥 TIER 2: @kevvwill, @madeinny, @bobbymahers, @bitgogc, @lovell_d4d (1.3-1.8x weight)")
        print()
        
        all_discoveries = []
        tier_stats = {"tier1": 0, "tier2": 0, "cross_tier": 0}
        
        for category, queries in self.expanded_monitoring_queries.items():
            print(f"📊 {category.replace('_', ' ').title()}:")
            
            for i, query in enumerate(queries):
                print(f"   {i+1}/{len(queries)} {query[:55]}...")
                
                results = await self.search_twitter(query)
                tweets = results.get("data", [])
                users = {user["id"]: user for user in results.get("includes", {}).get("users", [])}
                
                for tweet in tweets:
                    user = users.get(tweet["author_id"], {})
                    username = user.get("username", "").lower()
                    
                    # Only process if from monitored tastemakers
                    all_tastemakers = {**self.tier1_tastemakers, **self.tier2_tastemakers}
                    if username in all_tastemakers:
                        
                        analysis = await self.analyze_tastemaker_discovery(tweet, user, category)
                        
                        if analysis["score"] > 50:  # Quality threshold
                            discovery = {
                                "artist_mention": self.extract_artist_mentions(tweet["text"]),
                                "tastemaker": f"@{username}",
                                "text": tweet["text"][:120] + "...",
                                "url": f"https://twitter.com/{username}/status/{tweet['id']}",
                                "engagement": tweet.get("public_metrics", {}).get("like_count", 0) + 
                                           tweet.get("public_metrics", {}).get("retweet_count", 0),
                                **analysis
                            }
                            all_discoveries.append(discovery)
                            
                            # Track tier stats
                            tier_stats[f"tier{analysis['tier']}"] += 1
                
                await asyncio.sleep(1.5)
        
        # Cross-tier validation analysis
        await self.analyze_cross_tier_validation(all_discoveries)
        
        # Report discoveries
        await self.report_expanded_discoveries(all_discoveries, tier_stats)
        
        return all_discoveries
    
    def extract_artist_mentions(self, text):
        """Extract potential artist names from tastemaker posts"""
        import re
        
        # Look for artist name patterns
        patterns = [
            r'@(\w+)',  # @mentions
            r'"([^"]{3,25})"',  # Quoted names
            r'artist (\w+)',  # "artist X"
            r'rapper (\w+)',   # "rapper X"
        ]
        
        mentions = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            mentions.extend(matches)
        
        return [m for m in mentions if len(m) > 2][:3]  # Top 3 mentions
    
    async def analyze_cross_tier_validation(self, discoveries):
        """Identify artists mentioned by multiple tastemaker tiers (high confidence)"""
        from collections import defaultdict
        
        artist_mentions = defaultdict(list)
        
        for discovery in discoveries:
            for artist in discovery["artist_mention"]:
                artist_mentions[artist].append(discovery)
        
        # Find cross-tier validated artists
        validated_artists = []
        for artist, mentions in artist_mentions.items():
            tiers = set(m["tier"] for m in mentions)
            if len(tiers) > 1:  # Mentioned by multiple tiers
                validated_artists.append({
                    "artist": artist,
                    "mentions": len(mentions),
                    "tiers": sorted(tiers),
                    "total_score": sum(m["score"] for m in mentions),
                    "tastemakers": [m["tastemaker"] for m in mentions]
                })
        
        return sorted(validated_artists, key=lambda x: x["total_score"], reverse=True)
    
    async def report_expanded_discoveries(self, discoveries, tier_stats):
        """Generate comprehensive tastemaker network report"""
        if not discoveries:
            print("   📊 No significant discoveries this cycle")
            return
        
        # Sort by score
        top_discoveries = sorted(discoveries, key=lambda x: x["score"], reverse=True)[:8]
        
        print(f"\n🔥 TOP TASTEMAKER DISCOVERIES ({len(discoveries)} total):")
        print("=" * 45)
        
        for i, d in enumerate(top_discoveries):
            priority = "🚨 URGENT" if d["score"] > 100 else "⚡ HIGH" if d["score"] > 75 else "📊 MEDIUM"
            
            print(f"\n{i+1}. {priority} - {d['tastemaker']} (Tier {d['tier']}, {d['weight']}x weight)")
            print(f"   Score: {d['score']:.1f}/150 | Engagement: {d['engagement']}")
            print(f"   Focus: {d['focus']}")
            print(f"   Signals: {', '.join(d['signals'])}")
            print(f"   Artists: {d['artist_mention']}")
            print(f"   Tweet: \"{d['text']}\"")
            print(f"   URL: {d['url']}")
        
        # Network performance stats
        print(f"\n📊 NETWORK PERFORMANCE:")
        print("-" * 25)
        print(f"   Tier 1 discoveries: {tier_stats['tier1']}")
        print(f"   Tier 2 discoveries: {tier_stats['tier2']}")
        print(f"   Total discoveries: {len(discoveries)}")
        
        urgent = len([d for d in top_discoveries if d["score"] > 100])
        high = len([d for d in top_discoveries if 75 <= d["score"] <= 100])
        
        print(f"\n🎯 PRIORITY BREAKDOWN:")
        print(f"   🚨 URGENT (>100): {urgent}")
        print(f"   ⚡ HIGH (75-100): {high}")
    
    async def continuous_expanded_monitoring(self):
        """Run continuous expanded tastemaker monitoring"""
        print("🚀 EXPANDED TASTEMAKER NETWORK - CONTINUOUS MONITORING")
        print("=" * 60)
        print("🎯 9-account tastemaker network for maximum scene coverage")
        print("⚡ Tier-weighted scoring for credibility-based discovery")
        print("🔍 12-minute monitoring cycles for rapid detection")
        print("\n💡 Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                await self.expanded_monitoring_cycle()
                
                print(f"\n⏰ Next expanded network scan in 12 minutes...")
                
                # Wait 12 minutes between cycles
                for i in range(12 * 60):
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 EXPANDED TASTEMAKER MONITORING STOPPED")
            print("📊 9-account network monitoring ended")

async def main():
    """Start expanded tastemaker network monitoring"""
    network = ExpandedTastemakerNetwork()
    await network.continuous_expanded_monitoring()

if __name__ == "__main__":
    asyncio.run(main())