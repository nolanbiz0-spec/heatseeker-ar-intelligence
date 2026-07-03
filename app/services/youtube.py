import asyncio
import httpx
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..config import settings
from ..database import redis_client


class YouTubeClient:
    """YouTube Data API v3 client with rate limiting and caching"""
    
    def __init__(self):
        self.api_key = settings.youtube_api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    async def _rate_limit_key(self) -> str:
        """Generate daily rate limit key for Redis"""
        current_date = datetime.utcnow().date()
        return f"youtube:rate_limit:{current_date.isoformat()}"
    
    async def _check_rate_limit(self, cost: int = 1) -> bool:
        """Check if we're within daily quota (10,000 units/day)"""
        key = await self._rate_limit_key()
        current_usage = await redis_client.get(key)
        current_usage = int(current_usage) if current_usage else 0
        
        if current_usage + cost > settings.youtube_rate_limit:
            return False
            
        # Increment usage
        await redis_client.incrby(key, cost)
        await redis_client.expire(key, 86400)  # Expire after 24 hours
        
        return True
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any], cost: int = 1) -> Dict[str, Any]:
        """Make rate-limited API request with caching"""
        
        # Check rate limit
        if not await self._check_rate_limit(cost):
            raise Exception("YouTube API daily quota exceeded")
        
        # Add API key to params
        params["key"] = self.api_key
        
        # Check cache
        cache_key = f"youtube:{endpoint}:{json.dumps(params, sort_keys=True)}"
        cached_response = await redis_client.get(cache_key)
        if cached_response:
            return json.loads(cached_response)
        
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            data = response.json()
            
            # Cache response for 10 minutes
            await redis_client.setex(cache_key, 600, json.dumps(data))
            return data
    
    async def search_channels(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for YouTube channels by name (cost: 100 units)"""
        params = {
            "part": "snippet",
            "type": "channel", 
            "q": query,
            "maxResults": max_results,
            "order": "relevance"
        }
        
        response = await self._make_request("search", params, cost=100)
        return response.get("items", [])
    
    async def get_channel_stats(self, channel_id: str) -> Dict[str, Any]:
        """Get channel statistics (cost: 1 unit)"""
        params = {
            "part": "statistics,snippet,brandingSettings",
            "id": channel_id
        }
        
        response = await self._make_request("channels", params, cost=1)
        items = response.get("items", [])
        return items[0] if items else {}
    
    async def get_channel_videos(self, channel_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent videos from channel (cost: 100 units)"""
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "type": "video",
            "order": "date",
            "maxResults": max_results
        }
        
        response = await self._make_request("search", params, cost=100)
        return response.get("items", [])
    
    async def get_video_stats(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """Get statistics for multiple videos (cost: 1 unit per video)"""
        if not video_ids:
            return []
            
        params = {
            "part": "statistics,snippet",
            "id": ",".join(video_ids[:50])  # Max 50 videos per request
        }
        
        response = await self._make_request("videos", params, cost=len(video_ids))
        return response.get("items", [])
    
    async def get_channel_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get channel details by username (cost: 1 unit)"""
        params = {
            "part": "statistics,snippet",
            "forUsername": username
        }
        
        response = await self._make_request("channels", params, cost=1)
        items = response.get("items", [])
        return items[0] if items else None


# Global YouTube client instance
youtube_client = YouTubeClient()