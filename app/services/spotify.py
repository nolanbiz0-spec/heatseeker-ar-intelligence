import asyncio
import httpx
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from ..config import settings
from ..database import redis_client


class SpotifyClient:
    """Spotify Web API client with rate limiting and caching"""
    
    def __init__(self):
        self.client_id = settings.spotify_client_id
        self.client_secret = settings.spotify_client_secret
        self.base_url = "https://api.spotify.com/v1"
        self.token_url = "https://accounts.spotify.com/api/token"
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None
        
    async def _get_access_token(self) -> str:
        """Get or refresh OAuth2 access token using Client Credentials flow"""
        
        # Check if current token is still valid
        if self._access_token and self._token_expires and datetime.utcnow() < self._token_expires:
            return self._access_token
            
        # Check Redis cache for token
        cached_token = await redis_client.get("spotify:access_token")
        if cached_token:
            token_data = json.loads(cached_token)
            if datetime.fromisoformat(token_data["expires"]) > datetime.utcnow():
                self._access_token = token_data["token"]
                self._token_expires = datetime.fromisoformat(token_data["expires"])
                return self._access_token
        
        # Request new token
        async with httpx.AsyncClient() as client:
            auth = httpx.BasicAuth(self.client_id, self.client_secret)
            data = {"grant_type": "client_credentials"}
            
            response = await client.post(self.token_url, auth=auth, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires = datetime.utcnow() + timedelta(seconds=expires_in - 60)  # 1min buffer
            
            # Cache token in Redis
            cache_data = {
                "token": self._access_token,
                "expires": self._token_expires.isoformat()
            }
            await redis_client.setex(
                "spotify:access_token",
                expires_in - 60,
                json.dumps(cache_data)
            )
            
            return self._access_token
    
    async def _rate_limit_key(self) -> str:
        """Generate rate limit key for Redis"""
        current_minute = datetime.utcnow().replace(second=0, microsecond=0)
        return f"spotify:rate_limit:{current_minute.isoformat()}"
    
    async def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits (100 requests/minute)"""
        key = await self._rate_limit_key()
        current_count = await redis_client.incr(key)
        
        if current_count == 1:
            await redis_client.expire(key, 60)  # Expire after 1 minute
            
        return current_count <= settings.spotify_rate_limit
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make rate-limited API request with caching"""
        
        # Check rate limit
        if not await self._check_rate_limit():
            await asyncio.sleep(60)  # Wait for rate limit reset
        
        # Check cache
        cache_key = f"spotify:{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        cached_response = await redis_client.get(cache_key)
        if cached_response:
            return json.loads(cached_response)
        
        # Make API request
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                params=params or {}
            )
            response.raise_for_status()
            data = response.json()
            
            # Cache response for 5 minutes
            await redis_client.setex(cache_key, 300, json.dumps(data))
            return data
    
    async def search_artist(self, query: str, limit: int = 1) -> List[Dict[str, Any]]:
        """Search for artists by name"""
        params = {
            "q": query,
            "type": "artist",
            "limit": limit
        }
        
        response = await self._make_request("search", params)
        return response.get("artists", {}).get("items", [])
    
    async def get_artist(self, artist_id: str) -> Dict[str, Any]:
        """Get artist details by Spotify ID"""
        return await self._make_request(f"artists/{artist_id}")
    
    async def get_artist_top_tracks(self, artist_id: str, market: str = "US") -> List[Dict[str, Any]]:
        """Get artist's top tracks"""
        params = {"market": market}
        response = await self._make_request(f"artists/{artist_id}/top-tracks", params)
        return response.get("tracks", [])
    
    async def get_artist_albums(self, artist_id: str, limit: int = 20, market: str = "US") -> List[Dict[str, Any]]:
        """Get artist's albums"""
        params = {
            "include_groups": "album,single",
            "market": market,
            "limit": limit
        }
        response = await self._make_request(f"artists/{artist_id}/albums", params)
        return response.get("items", [])


# Global Spotify client instance
spotify_client = SpotifyClient()