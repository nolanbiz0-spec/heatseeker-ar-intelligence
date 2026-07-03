#!/usr/bin/env python3
"""
Real-time artist independence verification system
CRITICAL: This is what Heatseeker NEEDS to be production-ready
"""

import asyncio
import httpx
from datetime import datetime, timedelta
import re

class IndependenceVerifier:
    """Verify if artists are actually unsigned vs signed to major/indie labels"""
    
    def __init__(self, musicbrainz_email: str):
        self.musicbrainz_email = musicbrainz_email
        self.session = None
        
    async def verify_artist_independence(self, artist_name: str) -> dict:
        """
        Multi-source verification of artist signing status
        Returns: {status, confidence, last_verified, evidence, warnings}
        """
        
        results = {
            "artist_name": artist_name,
            "independence_status": "unknown",
            "confidence": 0.0,
            "last_verified": datetime.now().isoformat(),
            "evidence": [],
            "red_flags": [],
            "verification_sources": []
        }
        
        # 1. MusicBrainz Label Relationships
        mb_result = await self._check_musicbrainz_labels(artist_name)
        if mb_result:
            results["evidence"].extend(mb_result["evidence"])
            results["verification_sources"].append("musicbrainz")
            
        # 2. Spotify Release Metadata  
        spotify_result = await self._check_spotify_labels(artist_name)
        if spotify_result:
            results["evidence"].extend(spotify_result["evidence"])
            results["verification_sources"].append("spotify")
            
        # 3. Recent Press/News Monitoring
        press_result = await self._check_recent_press(artist_name)
        if press_result:
            results["evidence"].extend(press_result["evidence"])
            results["verification_sources"].append("press_monitoring")
            
        # 4. Distribution Pattern Analysis
        distro_result = await self._analyze_distribution(artist_name)
        if distro_result:
            results["evidence"].extend(distro_result["evidence"])
            results["verification_sources"].append("distribution_analysis")
            
        # Calculate final status and confidence
        results = self._calculate_independence_score(results)
        
        return results
    
    async def _check_musicbrainz_labels(self, artist_name: str) -> dict:
        """Check MusicBrainz for label relationships"""
        
        try:
            # Search for artist
            search_url = f"https://musicbrainz.org/ws/2/artist"
            params = {
                "query": f"artist:{artist_name}",
                "fmt": "json",
                "limit": 5
            }
            
            headers = {"User-Agent": f"HeatsekerAR/1.0 ({self.musicbrainz_email})"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(search_url, params=params, headers=headers)
                
                if response.status_code != 200:
                    return None
                    
                data = response.json()
                
                if not data.get("artists"):
                    return {"evidence": [f"No MusicBrainz entry found for {artist_name}"]}
                
                evidence = []
                
                for artist in data["artists"]:
                    if artist.get("score", 0) > 85:  # High confidence match
                        
                        # Get detailed artist info with label relationships
                        artist_id = artist["id"] 
                        detail_url = f"https://musicbrainz.org/ws/2/artist/{artist_id}"
                        detail_params = {"inc": "release-groups+labels", "fmt": "json"}
                        
                        detail_response = await client.get(detail_url, params=detail_params, headers=headers)
                        
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            
                            # Analyze release groups for label patterns
                            if "release-groups" in detail_data:
                                labels_found = self._extract_labels_from_releases(detail_data["release-groups"])
                                
                                for label in labels_found:
                                    if self._is_major_label(label):
                                        evidence.append(f"MAJOR LABEL DETECTED: {label}")
                                    elif self._is_indie_label(label):
                                        evidence.append(f"Indie label: {label}")
                                    else:
                                        evidence.append(f"Unknown label: {label}")
                
                return {"evidence": evidence}
                
        except Exception as e:
            return {"evidence": [f"MusicBrainz check failed: {str(e)}"]}
    
    async def _check_spotify_labels(self, artist_name: str) -> dict:
        """Check Spotify for label/publisher information on recent releases"""
        
        # This would need Spotify API integration
        # Check artist's recent albums/singles for label metadata
        # Look for patterns: major label vs indie vs self-released
        
        return {"evidence": ["Spotify label check not implemented yet"]}
    
    async def _check_recent_press(self, artist_name: str) -> dict:
        """Monitor recent press for signing announcements"""
        
        try:
            # Search for recent signing announcements
            search_terms = [
                f'"{artist_name}" signed',
                f'"{artist_name}" record deal', 
                f'"{artist_name}" label',
                f'"{artist_name}" announces signing'
            ]
            
            evidence = []
            
            # This would integrate with Google News API or similar
            # For now, return placeholder
            evidence.append("Press monitoring not fully implemented")
            
            return {"evidence": evidence}
            
        except Exception as e:
            return {"evidence": [f"Press check failed: {str(e)}"]}
    
    async def _analyze_distribution(self, artist_name: str) -> dict:
        """Analyze distribution patterns to infer label status"""
        
        # Major labels typically use specific distributors
        # Indies use different patterns
        # Self-released artists use DistroKid, CD Baby, etc.
        
        return {"evidence": ["Distribution analysis not implemented yet"]}
    
    def _extract_labels_from_releases(self, release_groups: list) -> list:
        """Extract label names from MusicBrainz release groups"""
        labels = set()
        
        for rg in release_groups:
            # This would parse the release group data for label info
            # Implementation depends on MB data structure
            pass
            
        return list(labels)
    
    def _is_major_label(self, label_name: str) -> bool:
        """Check if label is a major (Universal, Sony, Warner)"""
        
        major_labels = {
            # Universal Music Group
            "universal", "interscope", "def jam", "island", "republic", "capitol", 
            "geffen", "atlantic", "elektra", "warner",
            
            # Sony Music Entertainment  
            "columbia", "rca", "epic", "sony music", "arista", "j records",
            
            # Warner Music Group
            "warner bros", "warner music", "atlantic", "elektra", "roadrunner",
            
            # Other majors/major imprints
            "emi", "virgin", "capitol", "hollywood records"
        }
        
        label_lower = label_name.lower()
        return any(major in label_lower for major in major_labels)
    
    def _is_indie_label(self, label_name: str) -> bool:
        """Check if label is a known indie (not major, but established)"""
        
        indie_labels = {
            "sub pop", "matador", "merge", "domino", "4ad", "xl recordings",
            "rough trade", "factory", "creation", "mute", "warp", "ninja tune",
            "epitaph", "fat wreck chords", "dischord", "sst", "touch and go"
        }
        
        label_lower = label_name.lower()
        return any(indie in label_lower for indie in indie_labels)
    
    def _calculate_independence_score(self, results: dict) -> dict:
        """Calculate final independence status and confidence"""
        
        evidence = results["evidence"]
        
        # Count different types of evidence
        major_label_count = len([e for e in evidence if "MAJOR LABEL DETECTED" in e])
        indie_label_count = len([e for e in evidence if "Indie label:" in e])
        
        if major_label_count > 0:
            results["independence_status"] = "signed_major"
            results["confidence"] = 0.9
            results["red_flags"].append("SIGNED TO MAJOR LABEL - NOT AVAILABLE FOR A&R")
            
        elif indie_label_count > 0:
            results["independence_status"] = "signed_indie" 
            results["confidence"] = 0.7
            results["red_flags"].append("Signed to indie label - may have limited availability")
            
        else:
            # No clear label evidence found
            if len(results["verification_sources"]) >= 2:
                results["independence_status"] = "likely_unsigned"
                results["confidence"] = 0.6
            else:
                results["independence_status"] = "unknown"
                results["confidence"] = 0.3
                results["red_flags"].append("Insufficient data for verification")
        
        return results

# Example usage
async def main():
    verifier = IndependenceVerifier(musicbrainz_email="nolanbiz0@gmail.com")
    
    # Test with known artists
    test_artists = ["Wisp", "Steve Lacy", "PinkPantheress"]
    
    for artist in test_artists:
        result = await verifier.verify_artist_independence(artist)
        
        print(f"\n🎵 ARTIST: {artist}")
        print(f"Status: {result['independence_status']}")
        print(f"Confidence: {result['confidence']:.2f}")
        
        if result['red_flags']:
            print("🚨 RED FLAGS:")
            for flag in result['red_flags']:
                print(f"   • {flag}")
        
        print("Evidence:")
        for evidence in result['evidence']:
            print(f"   • {evidence}")

if __name__ == "__main__":
    asyncio.run(main())