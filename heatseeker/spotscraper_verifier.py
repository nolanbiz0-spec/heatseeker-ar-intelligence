#!/usr/bin/env python3
"""
🎯 SpotScraper Integration for Enhanced A&R Intelligence
Professional Spotify data access with comprehensive label verification
"""

import os
import httpx
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

class SpotScraperVerifier:
    """
    Enhanced A&R intelligence using SpotScraper API
    
    SpotScraper provides:
    - Comprehensive artist metadata
    - Detailed copyright/label information
    - Enhanced rate limits for commercial use
    - Professional data access beyond basic Spotify API
    """
    
    def __init__(self):
        self.api_key = os.getenv("SPOTSCRAPER_API_KEY", "CPXMzrLRevbDbyAlLaIYXCSDfuVfXoGpBmjPhI3Rmc")
        self.base_url = "https://api.spotscraper.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def verify_artist_independence(self, artist_name: str) -> Dict[str, Any]:
        """
        Comprehensive independence verification using SpotScraper
        
        Provides enhanced copyright analysis and label relationship detection
        """
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            
            # Search for artist with enhanced metadata
            search_result = await self._search_artist_enhanced(client, artist_name)
            
            if not search_result["found"]:
                return self._create_unknown_result(artist_name, search_result["reason"])
            
            artist_data = search_result["artist"]
            
            # Get detailed discography with copyright info
            discography = await self._get_enhanced_discography(client, artist_data["id"])
            
            # Analyze latest releases for current signing status
            independence_analysis = self._analyze_independence_status(
                artist_name, discography
            )
            
            return independence_analysis
    
    async def _search_artist_enhanced(self, client: httpx.AsyncClient, artist_name: str) -> Dict[str, Any]:
        """Search for artist using SpotScraper enhanced search"""
        
        try:
            search_url = f"{self.base_url}/search"
            params = {
                "q": artist_name,
                "type": "artist",
                "limit": 10,
                "include_metadata": True
            }
            
            response = await client.get(search_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                artists = data.get("artists", {}).get("items", [])
                
                if artists:
                    # Select best match (exact name match preferred)
                    best_match = self._select_best_artist_match(artists, artist_name)
                    
                    return {
                        "found": True,
                        "artist": best_match,
                        "total_matches": len(artists)
                    }
                else:
                    return {
                        "found": False,
                        "reason": f"No artists found for '{artist_name}'"
                    }
            else:
                return {
                    "found": False,
                    "reason": f"Search API error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "found": False,
                "reason": f"Search failed: {str(e)}"
            }
    
    async def _get_enhanced_discography(self, client: httpx.AsyncClient, artist_id: str) -> List[Dict]:
        """Get comprehensive discography with copyright metadata"""
        
        try:
            discography_url = f"{self.base_url}/artists/{artist_id}/albums"
            params = {
                "include_groups": "album,single",
                "limit": 50,
                "include_copyrights": True,
                "include_labels": True,
                "market": "US"
            }
            
            response = await client.get(discography_url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("items", [])
            else:
                print(f"Discography fetch failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Discography error: {e}")
            return []
    
    def _select_best_artist_match(self, artists: List[Dict], target_name: str) -> Dict:
        """Select the most relevant artist from search results"""
        
        target_lower = target_name.lower().strip()
        
        # First priority: Exact name match
        for artist in artists:
            if artist.get("name", "").lower().strip() == target_lower:
                return artist
        
        # Second priority: Name contains target (for partial matches)
        for artist in artists:
            if target_lower in artist.get("name", "").lower():
                return artist
        
        # Fallback: Most popular (highest follower count)
        return max(artists, key=lambda x: x.get("followers", {}).get("total", 0))
    
    def _analyze_independence_status(self, artist_name: str, discography: List[Dict]) -> Dict[str, Any]:
        """
        Analyze independence status based on enhanced discography data
        
        Uses SpotScraper's enhanced copyright and label metadata
        """
        
        if not discography:
            return self._create_unknown_result(artist_name, "No discography data available")
        
        # Sort releases by date (newest first)
        sorted_releases = sorted(
            discography,
            key=lambda x: x.get("release_date", "0000-00-00"),
            reverse=True
        )
        
        # Analyze latest releases (last 18 months)
        current_date = datetime.now()
        recent_releases = []
        
        for release in sorted_releases:
            release_date_str = release.get("release_date", "")
            if release_date_str and len(release_date_str) >= 4:
                try:
                    release_year = int(release_date_str[:4])
                    current_year = current_date.year
                    
                    # Consider releases from last 2 years as "recent"
                    if current_year - release_year <= 2:
                        recent_releases.append(release)
                        
                except ValueError:
                    continue
        
        if not recent_releases:
            recent_releases = sorted_releases[:3]  # Fallback to 3 most recent
        
        # Analyze copyright and label information
        copyright_analysis = self._analyze_copyright_patterns(recent_releases)
        label_analysis = self._analyze_label_relationships(recent_releases)
        
        # Determine final independence status
        return self._determine_final_status(
            artist_name, copyright_analysis, label_analysis, recent_releases
        )
    
    def _analyze_copyright_patterns(self, releases: List[Dict]) -> Dict[str, Any]:
        """Analyze copyright patterns across recent releases"""
        
        major_labels = {
            "universal", "umg", "interscope", "capitol", "republic", "def jam", "geffen",
            "sony", "columbia", "rca", "epic", "arista", "legacy",
            "warner", "atlantic", "elektra", "rhino", "parlophone", "reprise"
        }
        
        indie_labels = {
            "sub pop", "matador", "4ad", "domino", "merge", "saddle creek", 
            "epitaph", "fat wreck", "dischord", "touch and go", "kranky"
        }
        
        copyright_signals = {
            "major_label_count": 0,
            "indie_label_count": 0,
            "independent_count": 0,
            "detected_labels": [],
            "evidence": []
        }
        
        for release in releases:
            # Check copyright information
            copyrights = release.get("copyrights", [])
            
            for copyright_info in copyrights:
                copyright_text = copyright_info.get("text", "").lower()
                
                # Check for major labels
                major_detected = False
                for major in major_labels:
                    if major in copyright_text:
                        copyright_signals["major_label_count"] += 1
                        copyright_signals["detected_labels"].append(copyright_info.get("text"))
                        copyright_signals["evidence"].append(f"Major label: {copyright_info.get('text')}")
                        major_detected = True
                        break
                
                # Check for indie labels (only if no major detected)
                if not major_detected:
                    indie_detected = False
                    for indie in indie_labels:
                        if indie in copyright_text:
                            copyright_signals["indie_label_count"] += 1
                            copyright_signals["evidence"].append(f"Indie label: {copyright_info.get('text')}")
                            indie_detected = True
                            break
                    
                    # If no known label, consider independent
                    if not indie_detected and copyright_text:
                        copyright_signals["independent_count"] += 1
                        copyright_signals["evidence"].append(f"Independent: {copyright_info.get('text')}")
        
        return copyright_signals
    
    def _analyze_label_relationships(self, releases: List[Dict]) -> Dict[str, Any]:
        """Analyze label relationship metadata from SpotScraper"""
        
        label_relationships = {
            "current_labels": [],
            "distribution_partners": [],
            "label_changes": [],
            "independence_indicators": []
        }
        
        for release in releases:
            # Check label metadata (SpotScraper enhanced data)
            label_info = release.get("label_info", {})
            
            if label_info:
                label_name = label_info.get("name", "")
                label_type = label_info.get("type", "")  # major, indie, distribution, self
                
                if label_type == "major":
                    label_relationships["current_labels"].append(label_name)
                elif label_type == "distribution":
                    label_relationships["distribution_partners"].append(label_name)
                elif label_type == "self" or label_type == "independent":
                    label_relationships["independence_indicators"].append(label_name)
        
        return label_relationships
    
    def _determine_final_status(
        self, 
        artist_name: str,
        copyright_analysis: Dict[str, Any],
        label_analysis: Dict[str, Any],
        recent_releases: List[Dict]
    ) -> Dict[str, Any]:
        """Determine final independence status with confidence scoring"""
        
        # Scoring logic based on copyright and label analysis
        major_signals = copyright_analysis["major_label_count"]
        indie_signals = copyright_analysis["indie_label_count"] 
        independent_signals = copyright_analysis["independent_count"]
        
        current_labels = label_analysis["current_labels"]
        independence_indicators = label_analysis["independence_indicators"]
        
        # Determine status
        if major_signals > 0 or current_labels:
            independence_status = "signed_major"
            confidence = 0.90 + (0.05 if len(current_labels) > 0 else 0)
            actionable = False
            primary_label = current_labels[0] if current_labels else copyright_analysis["detected_labels"][0]
            red_flag = "🚨 SIGNED TO MAJOR LABEL - NOT AVAILABLE FOR A&R"
            
        elif indie_signals > independent_signals:
            independence_status = "signed_indie" 
            confidence = 0.75
            actionable = False  # Complex negotiation required
            primary_label = "Independent Label"
            red_flag = "⚠️ Signed to indie label - complex A&R situation"
            
        elif independence_indicators or independent_signals > 0:
            independence_status = "unsigned"
            confidence = 0.80 + (0.1 if len(independence_indicators) > 0 else 0)
            actionable = True
            primary_label = None
            red_flag = None
            
        else:
            independence_status = "unknown"
            confidence = 0.40
            actionable = False
            primary_label = None
            red_flag = "❓ Independence status requires verification"
        
        # Build comprehensive result
        return {
            "artist_name": artist_name,
            "independence_status": independence_status,
            "confidence_score": confidence,
            "label_relationship": primary_label,
            "evidence": copyright_analysis["evidence"][:5],
            "red_flags": [red_flag] if red_flag else [],
            "a_and_r_actionable": actionable,
            "verification_timestamp": datetime.now().isoformat(),
            "spotscraper_analysis": {
                "recent_releases_analyzed": len(recent_releases),
                "major_label_signals": major_signals,
                "indie_label_signals": indie_signals,
                "independence_signals": independent_signals,
                "current_labels": current_labels,
                "independence_indicators": independence_indicators
            }
        }
    
    def _create_unknown_result(self, artist_name: str, reason: str) -> Dict[str, Any]:
        """Create result for unknown/error cases"""
        
        return {
            "artist_name": artist_name,
            "independence_status": "unknown",
            "confidence_score": 0.30,
            "label_relationship": None,
            "evidence": [reason],
            "red_flags": ["❓ Independence status requires verification"],
            "a_and_r_actionable": False,
            "verification_timestamp": datetime.now().isoformat(),
            "spotscraper_analysis": {
                "error": reason
            }
        }

# Test SpotScraper integration
async def test_spotscraper_integration():
    """Test the SpotScraper integration with known artists"""
    
    verifier = SpotScraperVerifier()
    
    print("🎯 SPOTSCRAPER A&R INTELLIGENCE TEST")
    print("=" * 60)
    print(f"API Key: {verifier.api_key[:10]}...")
    print(f"Base URL: {verifier.base_url}")
    
    test_artists = ["Wisp", "Steve Lacy", "Clairo", "Boy Pablo"]
    
    for artist in test_artists:
        print(f"\n🔍 Testing: {artist}")
        
        result = await verifier.verify_artist_independence(artist)
        
        print(f"   Status: {result['independence_status']}")
        print(f"   Confidence: {result['confidence_score']:.0%}")
        
        if result.get('label_relationship'):
            print(f"   Label: {result['label_relationship']}")
        
        print(f"   A&R Available: {'✅' if result['a_and_r_actionable'] else '❌'}")
        
        spotscraper_data = result.get('spotscraper_analysis', {})
        if spotscraper_data.get('recent_releases_analyzed'):
            print(f"   Releases analyzed: {spotscraper_data['recent_releases_analyzed']}")
            print(f"   Major signals: {spotscraper_data.get('major_label_signals', 0)}")
        
        print(f"   Evidence: {result['evidence'][:2]}")
        
        await asyncio.sleep(1)  # Rate limiting

if __name__ == "__main__":
    asyncio.run(test_spotscraper_integration())