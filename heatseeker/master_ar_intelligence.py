#!/usr/bin/env python3
"""
MASTER A&R INTELLIGENCE CONSOLIDATION DASHBOARD
Real-time monitoring of what the kids think + scene intelligence
Centralized system to know who to sign and who not to sign
"""

import asyncio
import httpx
from datetime import datetime
import signal
import sys

# Twitter API credentials
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAADZf8QEAAAAA7nwFfKvf1w1GLVkrcrojIe%2Bb9SA%3DieoEPjowCLGeNHM3hLEt58i8r3x6WcVMfyH1qm1KvNFe7Dsxbv'

class MasterARIntelligence:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        self.running = False
        
        print("🚀 MASTER A&R INTELLIGENCE CONSOLIDATION SYSTEM")
        print("=" * 60)
        print("🎯 MISSION: Know what the kids think to determine who to sign")
        print("📊 Youth sentiment determines artist career success")
        print("👥 Scene tastemaker intelligence for early discovery")
        print("⚡ Real-time monitoring for competitive advantage")
        print()
    
    async def consolidation_cycle(self):
        """Master consolidation cycle - all intelligence sources"""
        print(f"\n🔥 MASTER A&R INTELLIGENCE SCAN - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 70)
        print("📊 Consolidating: Youth Sentiment + Tastemaker Intelligence + Viral Detection")
        print()
        
        # Import and run all monitoring systems
        from heatseeker.youth_sentiment_dashboard import YouthSentimentDashboard
        from heatseeker.expanded_tastemaker_network import ExpandedTastemakerNetwork
        
        # 1. Youth Sentiment Analysis (Most Important)
        print("🧒 ANALYZING YOUTH SENTIMENT (Primary Signal)")
        print("-" * 45)
        youth_dashboard = YouthSentimentDashboard()
        youth_signals = await youth_dashboard.monitor_youth_sentiment()
        
        # 2. Expanded Tastemaker Network Analysis
        print("\n👥 ANALYZING TASTEMAKER NETWORK (Secondary Signal)")
        print("-" * 50)
        tastemaker_network = ExpandedTastemakerNetwork()
        tastemaker_discoveries = await tastemaker_network.expanded_monitoring_cycle()
        
        # 3. Cross-Reference Analysis
        await self.cross_reference_analysis(youth_signals, tastemaker_discoveries)
        
        return {
            "youth_signals": len(youth_signals),
            "tastemaker_discoveries": len(tastemaker_discoveries),
            "timestamp": datetime.now().isoformat()
        }
    
    async def cross_reference_analysis(self, youth_signals, tastemaker_discoveries):
        """Cross-reference youth sentiment with tastemaker intelligence"""
        print(f"\n🔗 CROSS-REFERENCE ANALYSIS")
        print("=" * 35)
        
        # Analyze overlapping signals
        youth_positive = [s for s in youth_signals if s["sentiment_score"] > 0]
        youth_negative = [s for s in youth_signals if s["sentiment_score"] < 0]
        breakthrough_predictions = [s for s in youth_signals if any("breakthrough" in sig for sig in s["signals"])]
        
        tastemaker_urgent = [d for d in tastemaker_discoveries if d["score"] > 100]
        tastemaker_high = [d for d in tastemaker_discoveries if 75 <= d["score"] <= 100]
        
        # Generate final recommendations
        print(f"🎯 FINAL A&R RECOMMENDATIONS:")
        print("-" * 30)
        print(f"🚨 IMMEDIATE ACTION REQUIRED:")
        print(f"   • {len(youth_positive)} artists with positive youth sentiment")
        print(f"   • {len(tastemaker_urgent)} urgent tastemaker discoveries") 
        print(f"   • {len(breakthrough_predictions)} youth breakthrough predictions")
        
        print(f"\n⚡ HIGH PRIORITY MONITORING:")
        print(f"   • {len(tastemaker_high)} high-value tastemaker signals")
        print(f"   • Cross-reference for overlapping mentions")
        
        print(f"\n⚠️  AVOID/RED FLAGS:")
        print(f"   • {len(youth_negative)} artists with negative youth sentiment")
        print(f"   • Youth opinion = career trajectory predictor")
        
        print(f"\n📊 INTELLIGENCE SUMMARY:")
        print(f"   • Total youth voices captured: {len(youth_signals)}")
        print(f"   • Total tastemaker signals: {len(tastemaker_discoveries)}")
        print(f"   • Combined intelligence sources: Youth + 9 Tastemaker accounts")
        
        # Success metrics
        success_score = (len(youth_positive) * 2) + len(tastemaker_urgent) + len(breakthrough_predictions)
        print(f"\n🏆 SESSION SUCCESS SCORE: {success_score}")
        
        if success_score > 50:
            print("   🔥 EXCELLENT - High discovery activity detected!")
        elif success_score > 25:
            print("   ⚡ GOOD - Solid intelligence gathered")
        else:
            print("   📊 BASELINE - Continue monitoring")
    
    async def continuous_consolidation(self):
        """Run continuous master consolidation monitoring"""
        self.running = True
        
        print("\n💡 CONSOLIDATION SCHEDULE:")
        print("   🧒 Youth Sentiment: Every 25 minutes (primary)")
        print("   👥 Tastemaker Network: Every 25 minutes (secondary)")
        print("   🔗 Cross-Reference: After each cycle")
        print("   📊 Full Consolidation: Every 25 minutes")
        print()
        print("💡 Press Ctrl+C to stop monitoring")
        
        try:
            while self.running:
                results = await self.consolidation_cycle()
                
                print(f"\n⏰ NEXT MASTER CONSOLIDATION SCAN IN 25 MINUTES")
                print(f"📊 Last scan: {results['youth_signals']} youth + {results['tastemaker_discoveries']} tastemaker signals")
                print("🎯 Continuous intelligence gathering for competitive A&R advantage")
                
                # Wait 25 minutes between full consolidation cycles
                for i in range(25 * 60):
                    if not self.running:
                        break
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n\n🛑 MASTER A&R INTELLIGENCE STOPPED")
            print("📊 Consolidation dashboard ended")
            self.running = False
    
    def stop_monitoring(self):
        """Stop monitoring service"""
        self.running = False

# Signal handler for clean shutdown
master_intelligence = MasterARIntelligence()

def signal_handler(sig, frame):
    print("\n🛑 Shutting down Master A&R Intelligence...")
    master_intelligence.stop_monitoring()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

async def main():
    """Start master A&R intelligence consolidation"""
    await master_intelligence.continuous_consolidation()

if __name__ == "__main__":
    asyncio.run(main())