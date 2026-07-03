import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class SpotifyCollector:
    def __init__(self):
        self.client_id = settings.spotify_client_id
        self.client_secret = settings.spotify_client_secret
        self.access_token = None
        self.token_expires_at = None
        self.base_url = "https://api.spotify.com/v1"
        
    async def authenticate(self) -> bool:
        """Get Spotify access token using Client Credentials flow"""
        if not self.client_id or not self.client_secret:
            logger.error("Spotify credentials not configured")
            return False
            
        url = "https://accounts.spotify.com/api/token"
        data = {"grant_type": "client_credentials"}
        
        auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, auth=auth) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data["access_token"]
                        expires_in = token_data.get("expires_in", 3600)
                        self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
                        logger.info("Successfully authenticated with Spotify API")
                        return True
                    else:
                        logger.error(f"Spotify authentication failed: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error authenticating with Spotify: {e}")
            return False
    
    async def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid access token"""
        if not self.access_token or (self.token_expires_at and datetime.utcnow() >= self.token_expires_at):
            return await self.authenticate()
        return True
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated request to Spotify API"""
        if not await self._ensure_authenticated():
            return None
            
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limited
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limited, waiting {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                        return await self._make_request(endpoint, params)
                    else:
                        logger.error(f"Spotify API error {response.status}: {await response.text()}")
                        return None
        except Exception as e:
            logger.error(f"Error making Spotify request to {endpoint}: {e}")
            return None
    
    async def get_artist_data(self, artist_id: str) -> Optional[Dict]:
        """Get comprehensive artist data from Spotify"""
        if not artist_id:
            return None
            
        # Get basic artist info
        artist_data = await self._make_request(f"artists/{artist_id}")
        if not artist_data:
            return None
            
        # Get top tracks
        top_tracks_data = await self._make_request(f"artists/{artist_id}/top-tracks", {"market": "US"})
        
        # Get albums/singles
        albums_data = await self._make_request(
            f"artists/{artist_id}/albums", 
            {"include_groups": "album,single", "market": "US", "limit": 50}
        )
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "artist_id": artist_id,
            "artist": artist_data,
            "top_tracks": top_tracks_data.get("tracks", []) if top_tracks_data else [],
            "albums": albums_data.get("items", []) if albums_data else []
        }
    
    async def get_track_data(self, track_id: str) -> Optional[Dict]:
        """Get detailed track information"""
        track_data = await self._make_request(f"tracks/{track_id}")
        if not track_data:
            return None
            
        # Get audio features
        audio_features = await self._make_request(f"audio-features/{track_id}")
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "track": track_data,
            "audio_features": audio_features
        }
    
    async def search_artists(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for artists by name or other criteria"""
        params = {
            "q": query,
            "type": "artist",
            "limit": limit,
            "market": "US"
        }
        
        result = await self._make_request("search", params)
        if result and "artists" in result:
            return result["artists"]["items"]
        return []
    
    def extract_artist_metrics(self, artist_data: Dict) -> Dict:
        """Extract key metrics from artist data"""
        if not artist_data or "artist" not in artist_data:
            return {}
            
        artist = artist_data["artist"]
        
        return {
            "followers": artist.get("followers", {}).get("total", 0),
            "popularity": artist.get("popularity", 0),
            "genres": artist.get("genres", []),
            "monthly_listeners": None,  # Not available in public API
            "top_tracks_count": len(artist_data.get("top_tracks", [])),
            "albums_count": len(artist_data.get("albums", []))
        }
    
    def extract_track_metrics(self, track_data: Dict) -> Dict:
        """Extract key metrics from track data"""
        if not track_data or "track" not in track_data:
            return {}
            
        track = track_data["track"]
        
        return {
            "popularity": track.get("popularity", 0),
            "duration_ms": track.get("duration_ms", 0),
            "explicit": track.get("explicit", False),
            "release_date": track.get("album", {}).get("release_date"),
            "markets": len(track.get("available_markets", [])),
        }