#!/usr/bin/env python3
"""
🎯 Signing Status Fluidity Demo
Demonstrates how artist independence status changes over time
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any

class SigningStatusFluidityDemo:
    """
    Demonstrates artist signing status fluidity with real examples
    
    Key insight: LATEST RELEASE = CURRENT STATUS (not historical deals)
    """
    
    def __init__(self):
        # Real-world examples of signing status changes
        self.status_change_examples = {
            "wisp": {
                "current_status": {
                    "independence_status": "signed_major",
                    "label": "Interscope Records",
                    "evidence": ["℗ 2025 Music Soup/Interscope Records"],
                    "latest_releases": [
                        {"name": "If Not Winter", "date": "2025-08-01", "label": "Interscope"},
                        {"name": "Yellow", "date": "2025-09-10", "label": "Interscope"},
                        {"name": "I remember how your hands felt", "date": "2024-10-31", "label": "Interscope"}
                    ]
                },
                "historical_status": {
                    "independence_status": "unsigned",  # Assumed based on early career
                    "evidence": ["Early releases likely independent"],
                    "note": "Signed to Interscope sometime before 2023"
                },
                "status_change": "INDEPENDENT → MAJOR LABEL (Pre-2023)",
                "a_and_r_impact": "❌ No longer available - major label deal"
            },
            
            "frank_ocean": {
                "current_status": {
                    "independence_status": "unsigned", 
                    "label": "Independent/Own label",
                    "evidence": ["Blonde (2016) released independently", "No major label on recent releases"],
                    "latest_releases": [
                        {"name": "Blonde", "date": "2016-08-20", "label": "Independent"},
                        {"name": "Endless", "date": "2016-08-19", "label": "Independent"}
                    ]
                },
                "historical_status": {
                    "independence_status": "signed_major",
                    "label": "Def Jam Recordings",
                    "evidence": ["Channel Orange (2012) - Def Jam", "Nostalgia, Ultra mixtape era"]
                },
                "status_change": "MAJOR LABEL → INDEPENDENT (2016)",
                "a_and_r_impact": "✅ Theoretically available but unlikely to sign (established independent)"
            },
            
            "chance_the_rapper": {
                "current_status": {
                    "independence_status": "unsigned",
                    "label": "Independent", 
                    "evidence": ["Consistently rejected major label offers", "Self-funded tours and releases"],
                    "latest_releases": [
                        {"name": "The Big Day", "date": "2019-07-26", "label": "Independent"},
                        {"name": "Coloring Book", "date": "2016-05-13", "label": "Independent"}
                    ]
                },
                "historical_status": {
                    "independence_status": "unsigned",
                    "evidence": ["Always been independent", "Turned down multiple major deals"]
                },
                "status_change": "CONSISTENTLY INDEPENDENT",
                "a_and_r_impact": "❌ Not available - committed to independence"
            },
            
            "tyler_the_creator": {
                "current_status": {
                    "independence_status": "independent_label_owner",
                    "label": "Odd Future Records (own label)",
                    "evidence": ["Owns Odd Future Records", "Distribution deals but maintains ownership"],
                    "latest_releases": [
                        {"name": "Call Me If You Get Lost", "date": "2021-06-25", "label": "Odd Future/Columbia"},
                        {"name": "Igor", "date": "2019-05-17", "label": "Odd Future/Columbia"}
                    ]
                },
                "historical_status": {
                    "independence_status": "signed_indie",
                    "label": "XL Recordings",
                    "evidence": ["Early albums on XL Recordings"]
                },
                "status_change": "INDIE LABEL → OWN LABEL/DISTRIBUTION (2011+)",
                "a_and_r_impact": "⚠️ Complex - has own label but distribution partnerships"
            }
        }
    
    def demonstrate_status_fluidity(self) -> Dict[str, Any]:
        """
        Demonstrate how signing status fluidity affects A&R intelligence
        
        Shows why LATEST RELEASE analysis is critical for accurate targeting
        """
        
        print("🎯 SIGNING STATUS FLUIDITY IN A&R INTELLIGENCE")
        print("=" * 80)
        print("Key insight: Artist independence status changes over time")
        print("LATEST RELEASE = CURRENT STATUS (not historical deals)\n")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_examples": len(self.status_change_examples),
            "status_change_patterns": {},
            "a_and_r_implications": {}
        }
        
        for artist_name, data in self.status_change_examples.items():
            print(f"📊 {artist_name.upper()}")
            print("-" * 40)
            
            current = data["current_status"]
            historical = data["historical_status"] 
            
            print(f"Historical Status: {historical['independence_status']}")
            if historical.get('label'):
                print(f"Historical Label: {historical['label']}")
            
            print(f"Current Status: {current['independence_status']}")  
            if current.get('label'):
                print(f"Current Label: {current['label']}")
            
            print(f"Status Change: {data['status_change']}")
            print(f"A&R Impact: {data['a_and_r_impact']}")
            
            # Show latest release evidence
            print(f"Latest Release Evidence:")
            for release in current['latest_releases'][:2]:
                print(f"  • {release['name']} ({release['date']}) - {release['label']}")
            
            print()
            
            # Store pattern data
            results["status_change_patterns"][artist_name] = {
                "historical_status": historical["independence_status"],
                "current_status": current["independence_status"],
                "change_type": data["status_change"]
            }
            
            results["a_and_r_implications"][artist_name] = {
                "actionable": "✅" in data["a_and_r_impact"],
                "complexity": "⚠️" in data["a_and_r_impact"],
                "unavailable": "❌" in data["a_and_r_impact"]
            }
        
        # Summary insights
        print("🎯 KEY A&R INTELLIGENCE INSIGHTS:")
        print("=" * 50)
        
        actionable_count = sum(1 for x in results["a_and_r_implications"].values() if x["actionable"])
        unavailable_count = sum(1 for x in results["a_and_r_implications"].values() if x["unavailable"])
        complex_count = sum(1 for x in results["a_and_r_implications"].values() if x["complexity"])
        
        print(f"✅ Currently actionable targets: {actionable_count}/{len(self.status_change_examples)}")
        print(f"❌ Unavailable (signed/committed): {unavailable_count}/{len(self.status_change_examples)}")
        print(f"⚠️ Complex situations: {complex_count}/{len(self.status_change_examples)}")
        
        print(f"\n📈 STATUS CHANGE PATTERNS DETECTED:")
        
        change_patterns = {}
        for artist_data in results["status_change_patterns"].values():
            change_key = f"{artist_data['historical_status']} → {artist_data['current_status']}"
            change_patterns[change_key] = change_patterns.get(change_key, 0) + 1
        
        for pattern, count in change_patterns.items():
            print(f"  • {pattern}: {count} artist(s)")
        
        print(f"\n🚨 CRITICAL A&R SYSTEM REQUIREMENTS:")
        print(f"1. ✅ LATEST RELEASE analysis (not historical)")
        print(f"2. ✅ Regular status re-verification (quarterly)")  
        print(f"3. ✅ Status change detection and alerts")
        print(f"4. ✅ Multi-source copyright verification")
        print(f"5. ✅ Deal timeline and availability scoring")
        
        results["summary"] = {
            "actionable_percentage": (actionable_count / len(self.status_change_examples)) * 100,
            "unavailable_percentage": (unavailable_count / len(self.status_change_examples)) * 100,
            "verification_critical": True,
            "latest_release_priority": True
        }
        
        return results
    
    def get_verification_recommendations(self) -> List[str]:
        """
        Get specific recommendations for implementing status fluidity verification
        """
        
        return [
            "🔍 LATEST RELEASE PRIORITY: Always check most recent releases (last 12 months)",
            "📊 COPYRIGHT ANALYSIS: Parse ℗ (phonogram) and © (copyright) lines from metadata",
            "🔄 STATUS CHANGE DETECTION: Compare current vs historical label relationships", 
            "⏰ REGULAR RE-VERIFICATION: Quarterly checks for high-momentum artists",
            "🚨 ALERT SYSTEM: Flag status changes that affect A&R availability",
            "📈 CONFIDENCE SCORING: Weight recent releases higher than historical data",
            "🎯 DISTRIBUTION vs LABEL: Distinguish between distribution deals and full label contracts",
            "💼 DEAL EXPIRATION TRACKING: Monitor known deal lengths and expiration timelines"
        ]

# Run the demonstration
if __name__ == "__main__":
    demo = SigningStatusFluidityDemo()
    
    results = demo.demonstrate_status_fluidity()
    
    print(f"\n🎯 VERIFICATION RECOMMENDATIONS:")
    print("=" * 50)
    
    for recommendation in demo.get_verification_recommendations():
        print(f"  {recommendation}")
    
    print(f"\n📊 SYSTEM EFFECTIVENESS:")
    print(f"  Actionable targets: {results['summary']['actionable_percentage']:.1f}%")
    print(f"  Unavailable/complex: {results['summary']['unavailable_percentage']:.1f}%")
    print(f"  Latest release analysis: CRITICAL for accuracy")