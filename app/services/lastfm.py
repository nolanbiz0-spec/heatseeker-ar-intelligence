import asyncio
import httpx
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..config import settings
from ..database import redis_client


class LastFmClient:
    """Last.fm API client with rate limiting and caching"""
    
    def __init__(self):
        self.api_key = settings.lastfm_api_key
        self.secret = settings.lastfm_secret
        self.base_url = "https://ws.audioscrobbler.com/2.0/"
        
    async def _rate_limit_key(self) -> str:
        """Generate rate limit key for Redis (5 requests/second)"""
        current_second = datetime.utcnow().replace(microsecond=0)
        return f"lastfm:rate_limit:{current_second.isoformat()}"
    
    async def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits (5 requests/second)"""
        key = await self._rate_limit_key()
        current_count = await redis_client.incr(key)
        
        if current_count == 1:
            await redis_client.expire(key, 1)  # Expire after 1 second
            
        return current_count <= settings.lastfm_rate_limit
    
    async def _make_request(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make rate-limited API request with caching"""
        
        # Check rate limit
        if not await self._check_rate_limit():
            await asyncio.sleep(0.2)  # Brief pause for rate limiting
        
        # Prepare request parameters
        request_params = {
            "method": method,
            "api_key": self.api_key,
            "format": "json"
        }
        if params:
            request_params.update(params)
        
        # Check cache
        cache_key = f"lastfm:{method}:{json.dumps(request_params, sort_keys=True)}"
        cached_response = await redis_client.get(cache_key)
        if cached_response:
            return json.loads(cached_response)
        
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=request_params)
            response.raise_for_status()
            data = response.json()
            
            # Cache response for 5 minutes
            await redis_client.setex(cache_key, 300, json.dumps(data))
            return data
    
    async def get_artist_info(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """Get artist information and statistics"""
        try:
            response = await self._make_request("artist.getinfo", {"artist": artist_name})
            return response.get("artist")
        except Exception:
            return None
    
    async def get_artist_top_tracks(self, artist_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get artist's top tracks"""
        try:
            params = {"artist": artist_name, "limit": limit}
            response = await self._make_request("artist.gettoptracks", params)
            return response.get("toptracks", {}).get("track", [])
        except Exception:
            return []
    
    async def get_artist_similar(self, artist_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get similar artists"""
        try:
            params = {"artist": artist_name, "limit": limit}
            response = await self._make_request("artist.getsimilar", params)
            return response.get("similarartists", {}).get("artist", [])
        except Exception:
            return []
    
    async def search_artist(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for artists by name"""
        try:
            params = {"artist": query, "limit": limit}
            response = await self._make_request("artist.search", params)
            results = response.get("results", {}).get("artistmatches", {})
            return results.get("artist", []) if isinstance(results.get("artist"), list) else [results.get("artist", {})]
        except Exception:
            return []


class MusicBrainzClient:
    """MusicBrainz API client with rate limiting"""
    
    def __init__(self):
        self.email = settings.musicbrainz_email
        self.base_url = "https://musicbrainz.org/ws/2"
        self.headers = {
            "User-Agent": f"Heatseeker/1.0 ( {self.email} )"
        }
        
    async def _rate_limit_key(self) -> str:
        """Generate rate limit key for Redis (1 request/second)"""
        current_second = datetime.utcnow().replace(microsecond=0)
        return f"musicbrainz:rate_limit:{current_second.isoformat()}"
    
    async def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits (1 request/second)"""
        key = await self._rate_limit_key()
        current_count = await redis_client.incr(key)
        
        if current_count == 1:
            await redis_client.expire(key, 1)  # Expire after 1 second
            
        return current_count <= int(settings.musicbrainz_rate_limit)
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make rate-limited API request with caching"""
        
        # Check rate limit
        if not await self._check_rate_limit():
            await asyncio.sleep(1.0)  # Wait 1 second for rate limit
        
        # Add format parameter
        request_params = {"fmt": "json"}
        if params:
            request_params.update(params)
        
        # Check cache
        cache_key = f"musicbrainz:{endpoint}:{json.dumps(request_params, sort_keys=True)}"
        cached_response = await redis_client.get(cache_key)
        if cached_response:
            return json.loads(cached_response)
        
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                params=request_params
            )
            response.raise_for_status()
            data = response.json()
            
            # Cache response for 30 minutes (MusicBrainz data changes slowly)
            await redis_client.setex(cache_key, 1800, json.dumps(data))
            return data
    
    async def search_artist(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for artists by name"""
        try:
            params = {
                "query": f'artist:"{query}"',
                "limit": limit
            }
            response = await self._make_request("artist", params)
            return response.get("artists", [])
        except Exception:
            return []
    
    async def get_artist(self, mbid: str) -> Optional[Dict[str, Any]]:
        """Get artist details by MusicBrainz ID"""
        try:
            params = {"inc": "labels+genres+tags+relationships"}
            response = await self._make_request(f"artist/{mbid}", params)
            return response
        except Exception:
            return None
    
    async def get_artist_relationships(self, mbid: str) -> List[Dict[str, Any]]:
        """Get artist relationships (labels, management, etc.)"""
        try:
            params = {"inc": "relationships"}
            response = await self._make_request(f"artist/{mbid}", params)
            return response.get("relations", [])
        except Exception:
            return []


# Global client instances
lastfm_client = LastFmClient()
musicbrainz_client = MusicBrainzClient()