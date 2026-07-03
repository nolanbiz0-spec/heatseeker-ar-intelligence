#!/usr/bin/env python3
"""
🎯 Latest Release Independence Verifier
Handles artist signing status fluidity - checks LATEST releases for current status
"""

import os
import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class LatestReleaseVerifier:
    """
    Verifies artist independence based on LATEST RELEASE analysis
    
    Key insight: Signing status is FLUID
    - Artists finish deals and go independent
    - Artists sign new deals after being independent
    - Historical label releases ≠ current signing status
    
    LATEST RELEASE = CURRENT STATUS
    """
    
    def __init__(self):
        self.spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.access_token = None
        self.token_expires = None
        
    async def get_spotify_token(self) -> Optional[str]:
        """Get Spotify access token for API calls"""
        
        if (self.access_token and self.token_expires and 
            datetime.now() < self.token_expires):
            return self.access_token
        
        if not self.spotify_client_id or not self.spotify_client_secret:
            return None
            
        async with httpx.AsyncClient() as client:
            auth_url = "https://accounts.spotify.com/api/token"
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.spotify_client_id,
                "client_secret": self.spotify_client_secret
            }
            
            response = await client.post(auth_url, data=auth_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in - 60)
                return self.access_token
        
        return None
    
    async def analyze_latest_releases(self, artist_name: str) -> Dict[str, Any]:
        """
        Analyze artist's latest releases for current signing status
        
        Returns comprehensive analysis of:
        - Latest release copyright info
        - Status change detection (historical vs current)
        - Distribution pattern analysis
        - Independence confidence scoring
        """
        
        token = await self.get_spotify_token()
        if not token:
            return self._create_unknown_result(artist_name, "No Spotify API access")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Search for artist
            search_url = "https://api.spotify.com/v1/search"
            search_params = {"q": artist_name, "type": "artist", "limit": 5}
            
            search_response = await client.get(
                search_url, params=search_params, headers=headers
            )
            
            if search_response.status_code != 200:
                return self._create_unknown_result(
                    artist_name, f"Spotify search failed: {search_response.status_code}"
                )
            
            search_data = search_response.json()
            artists = search_data.get("artists", {}).get("items", [])
            
            if not artists:
                return self._create_unknown_result(artist_name, "Artist not found on Spotify")
            
            # Get the best match artist
            artist = self._select_best_artist_match(artists, artist_name)
            artist_id = artist["id"]
            
            # Get latest albums/singles (last 2 years)
            albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
            albums_params = {
                "include_groups": "album,single",
                "market": "US", 
                "limit": 20
            }
            
            albums_response = await client.get(
                albums_url, params=albums_params, headers=headers
            )
            
            if albums_response.status_code != 200:
                return self._create_unknown_result(
                    artist_name, f"Albums fetch failed: {albums_response.status_code}"
                )
            
            albums_data = albums_response.json()
            releases = albums_data.get("items", [])
            
            # Analyze latest releases
            return await self._analyze_release_pattern(
                client, headers, artist_name, releases
            )
    
    def _select_best_artist_match(self, artists: List[Dict], target_name: str) -> Dict:
        """Select the best artist match from search results"""
        
        # Prefer exact name matches and higher follower counts
        target_lower = target_name.lower()
        
        for artist in artists:
            if artist["name"].lower() == target_lower:
                return artist
        
        # Fallback to first result
        return artists[0]
    
    async def _analyze_release_pattern(
        self, 
        client: httpx.AsyncClient, 
        headers: Dict[str, str],
        artist_name: str, 
        releases: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze release pattern to determine current independence status
        
        Focuses on LATEST releases (last 12 months) for current status
        Compares to historical releases to detect status changes
        """
        
        latest_releases = []
        historical_releases = []
        current_date = datetime.now()
        
        # Categorize releases by recency
        for release in releases:
            release_date_str = release.get("release_date", "")
            if release_date_str:
                try:
                    # Handle different date formats (YYYY, YYYY-MM, YYYY-MM-DD)
                    if len(release_date_str) == 4:
                        release_date = datetime.strptime(release_date_str, "%Y")
                    elif len(release_date_str) == 7:
                        release_date = datetime.strptime(release_date_str, "%Y-%m")
                    else:
                        release_date = datetime.strptime(release_date_str[:10], "%Y-%m-%d")
                    
                    days_ago = (current_date - release_date).days
                    
                    if days_ago <= 365:  # Last 12 months = LATEST
                        latest_releases.append((release, release_date))
                    elif days_ago <= 730:  # 1-2 years ago = HISTORICAL
                        historical_releases.append((release, release_date))
                        
                except ValueError:
                    continue
        
        # Sort by date (newest first)
        latest_releases.sort(key=lambda x: x[1], reverse=True)
        historical_releases.sort(key=lambda x: x[1], reverse=True)
        
        # Analyze copyright info for latest releases
        latest_analysis = []
        historical_analysis = []
        
        # Get detailed copyright info for up to 5 latest releases
        for release, release_date in latest_releases[:5]:
            copyright_info = await self._get_release_copyright(
                client, headers, release["id"]
            )
            latest_analysis.append({
                "name": release["name"],
                "date": release_date.isoformat(),
                "copyright": copyright_info
            })
            
            await asyncio.sleep(0.2)  # Rate limiting
        
        # Get copyright info for historical comparison (up to 3)
        for release, release_date in historical_releases[:3]:
            copyright_info = await self._get_release_copyright(
                client, headers, release["id"]
            )
            historical_analysis.append({
                "name": release["name"],
                "date": release_date.isoformat(), 
                "copyright": copyright_info
            })
            
            await asyncio.sleep(0.2)  # Rate limiting
        
        # Determine current status based on latest releases
        return self._determine_current_status(
            artist_name, latest_analysis, historical_analysis
        )
    
    async def _get_release_copyright(
        self, 
        client: httpx.AsyncClient, 
        headers: Dict[str, str],
        album_id: str
    ) -> List[Dict[str, str]]:
        """Get copyright information for a specific release"""
        
        album_url = f"https://api.spotify.com/v1/albums/{album_id}"
        
        try:
            response = await client.get(album_url, headers=headers)
            
            if response.status_code == 200:
                album_data = response.json()
                return album_data.get("copyrights", [])
                
        except Exception:
            pass
        
        return []
    
    def _determine_current_status(
        self,
        artist_name: str,
        latest_analysis: List[Dict],
        historical_analysis: List[Dict]
    ) -> Dict[str, Any]:
        """
        Determine current independence status based on latest vs historical releases
        
        Logic:
        1. LATEST releases determine CURRENT status
        2. Compare to historical to detect status changes
        3. Major label indicators: Universal, Sony, Warner + subsidiaries
        4. Independence indicators: Self-released, small indie, distribution only
        """
        
        # Major label identifiers
        major_labels = {
            "universal", "umg", "interscope", "capitol", "republic", "def jam",
            "sony", "columbia", "rca", "epic", "arista",
            "warner", "atlantic", "elektra", "rhino", "parlophone"
        }
        
        # Analyze latest releases (current status)
        current_status = self._analyze_copyright_pattern(latest_analysis, major_labels)
        
        # Analyze historical releases (past status)  
        historical_status = self._analyze_copyright_pattern(historical_analysis, major_labels)
        
        # Detect status changes
        status_change_detected = (
            current_status["primary_status"] != historical_status["primary_status"]
            and len(historical_analysis) > 0
        )
        
        # Determine final independence status
        if current_status["primary_status"] == "major_label":
            independence_status = "signed_major"
            confidence = 0.90
            actionable = False
            red_flag = "🚨 SIGNED TO MAJOR LABEL - NOT AVAILABLE FOR A&R"
            
        elif current_status["primary_status"] == "indie_label":
            independence_status = "signed_indie"
            confidence = 0.75
            actionable = False  # Requires negotiation with indie label
            red_flag = "⚠️ Signed to indie label - complex A&R situation"
            
        elif current_status["primary_status"] == "independent":
            independence_status = "unsigned"
            confidence = 0.85
            actionable = True
            red_flag = None
            
        else:
            independence_status = "unknown"
            confidence = 0.30
            actionable = False
            red_flag = "❓ Independence status requires verification"
        
        # Build comprehensive result
        result = {
            "artist_name": artist_name,
            "independence_status": independence_status,
            "confidence_score": confidence,
            "label_relationship": current_status.get("detected_label"),
            "evidence": current_status["evidence"],
            "red_flags": [red_flag] if red_flag else [],
            "a_and_r_actionable": actionable,
            "verification_timestamp": datetime.now().isoformat(),
            "latest_release_analysis": {
                "latest_releases_analyzed": len(latest_analysis),
                "historical_releases_analyzed": len(historical_analysis),
                "current_status": current_status["primary_status"],
                "historical_status": historical_status["primary_status"],
                "status_change_detected": status_change_detected,
                "status_change_note": self._generate_status_change_note(
                    historical_status["primary_status"], 
                    current_status["primary_status"],
                    status_change_detected
                )
            }
        }
        
        return result
    
    def _analyze_copyright_pattern(
        self, 
        releases: List[Dict], 
        major_labels: set
    ) -> Dict[str, Any]:
        """Analyze copyright patterns across releases"""
        
        if not releases:
            return {
                "primary_status": "unknown",
                "detected_label": None,
                "evidence": ["No release data available"]
            }
        
        major_count = 0
        indie_count = 0 
        independent_count = 0
        detected_labels = []
        evidence = []
        
        for release in releases:
            copyright_texts = []
            
            for copyright_info in release.get("copyright", []):
                copyright_text = copyright_info.get("text", "").lower()
                copyright_texts.append(copyright_text)
                
                # Check for major labels
                for major_label in major_labels:
                    if major_label in copyright_text:
                        major_count += 1
                        detected_labels.append(copyright_info.get("text", ""))
                        evidence.append(f"Major label detected: {copyright_info.get('text', '')}")
                        break
                else:
                    # Check for indie indicators
                    if any(word in copyright_text for word in ["records", "music", "entertainment"]):
                        if not any(major in copyright_text for major in major_labels):
                            indie_count += 1
                            evidence.append(f"Indie label detected: {copyright_info.get('text', '')}")
                    else:
                        independent_count += 1
                        evidence.append(f"Independent release: {copyright_info.get('text', '')}")
        
        # Determine primary status
        if major_count > 0:
            primary_status = "major_label"
            detected_label = detected_labels[0] if detected_labels else None
        elif indie_count > independent_count:
            primary_status = "indie_label"
            detected_label = None
        else:
            primary_status = "independent"
            detected_label = None
        
        return {
            "primary_status": primary_status,
            "detected_label": detected_label,
            "evidence": evidence[:5]  # Limit evidence items
        }
    
    def _generate_status_change_note(
        self, 
        historical_status: str, 
        current_status: str,
        status_changed: bool
    ) -> str:
        """Generate human-readable status change note"""
        
        if not status_changed:
            return f"Status consistent: {current_status.replace('_', ' ')}"
        
        if historical_status == "major_label" and current_status == "independent":
            return "🔄 MAJOR → INDEPENDENT: Deal finished, now available for A&R"
        elif historical_status == "independent" and current_status == "major_label":
            return "🔄 INDEPENDENT → MAJOR: Recently signed, no longer available"
        elif historical_status == "indie_label" and current_status == "independent":
            return "🔄 INDIE → INDEPENDENT: Indie deal finished, potentially available"
        elif historical_status == "independent" and current_status == "indie_label":
            return "🔄 INDEPENDENT → INDIE: Signed to indie label, complex situation"
        else:
            return f"🔄 Status changed: {historical_status} → {current_status}"
    
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
            "latest_release_analysis": {
                "error": reason,
                "status_change_detected": False
            }
        }

# Test the enhanced verifier
async def test_latest_release_verification():
    """Test the latest release verification with known status-change examples"""
    
    verifier = LatestReleaseVerifier()
    
    test_artists = [
        "Wisp",  # Known: Interscope signed
        "Frank Ocean",  # Historical: Def Jam → Independent
        "Chance the Rapper",  # Consistently independent
        "Tyler the Creator"  # Complex: XL → Own label
    ]
    
    print("🎯 LATEST RELEASE INDEPENDENCE VERIFICATION TEST")
    print("=" * 70)
    
    for artist in test_artists:
        print(f"\n🔍 Testing: {artist}")
        
        result = await verifier.analyze_latest_releases(artist)
        
        print(f"   Status: {result['independence_status']}")
        print(f"   Confidence: {result['confidence_score']:.0%}")
        
        if result.get('label_relationship'):
            print(f"   Label: {result['label_relationship']}")
        
        print(f"   A&R Available: {result['a_and_r_actionable']}")
        
        # Latest release analysis
        latest_analysis = result.get('latest_release_analysis', {})
        if latest_analysis.get('status_change_detected'):
            print(f"   Status Change: {latest_analysis.get('status_change_note')}")
        
        print(f"   Evidence: {result['evidence'][:2]}")  # First 2 pieces of evidence

if __name__ == "__main__":
    asyncio.run(test_latest_release_verification())