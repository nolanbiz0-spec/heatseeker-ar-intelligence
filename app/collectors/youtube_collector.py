import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class YouTubeCollector:
    def __init__(self):
        self.api_key = settings.youtube_api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.daily_quota_used = 0
        self.max_daily_quota = settings.youtube_rate_limit
        
    async def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make request to YouTube Data API"""
        if not self.api_key:
            logger.error("YouTube API key not configured")
            return None
            
        if self.daily_quota_used >= self.max_daily_quota:
            logger.warning("YouTube API daily quota exceeded")
            return None
            
        if params is None:
            params = {}
        params["key"] = self.api_key
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        self.daily_quota_used += 1  # Simplified quota tracking
                        return await response.json()
                    elif response.status == 403:
                        error_data = await response.json()
                        if "quotaExceeded" in str(error_data):
                            logger.error("YouTube API quota exceeded")
                            return None
                    else:
                        logger.error(f"YouTube API error {response.status}: {await response.text()}")
                        return None
        except Exception as e:
            logger.error(f"Error making YouTube request to {endpoint}: {e}")
            return None
    
    async def get_channel_data(self, channel_id: str) -> Optional[Dict]:
        """Get channel statistics and information"""
        params = {
            "part": "statistics,snippet,brandingSettings",
            "id": channel_id
        }
        
        result = await self._make_request("channels", params)
        if result and "items" in result and result["items"]:
            channel = result["items"][0]
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "channel_id": channel_id,
                "channel": channel
            }
        return None
    
    async def search_channels(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for channels by artist name"""
        params = {
            "part": "snippet",
            "type": "channel",
            "q": query,
            "maxResults": max_results
        }
        
        result = await self._make_request("search", params)
        if result and "items" in result:
            return result["items"]
        return []
    
    async def get_channel_videos(self, channel_id: str, max_results: int = 25) -> List[Dict]:
        """Get recent videos from a channel"""
        # First get the uploads playlist ID
        channel_data = await self.get_channel_data(channel_id)
        if not channel_data:
            return []
            
        uploads_playlist_id = (
            channel_data.get("channel", {})
            .get("contentDetails", {})
            .get("relatedPlaylists", {})
            .get("uploads")
        )
        
        if not uploads_playlist_id:
            return []
        
        params = {
            "part": "snippet,contentDetails",
            "playlistId": uploads_playlist_id,
            "maxResults": max_results
        }
        
        result = await self._make_request("playlistItems", params)
        if result and "items" in result:
            return result["items"]
        return []
    
    async def get_video_statistics(self, video_ids: List[str]) -> Dict[str, Dict]:
        """Get statistics for multiple videos"""
        if not video_ids:
            return {}
            
        # YouTube API allows up to 50 video IDs per request
        video_stats = {}
        
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            params = {
                "part": "statistics,snippet",
                "id": ",".join(batch)
            }
            
            result = await self._make_request("videos", params)
            if result and "items" in result:
                for video in result["items"]:
                    video_stats[video["id"]] = video
        
        return video_stats
    
    def extract_channel_metrics(self, channel_data: Dict) -> Dict:
        """Extract key metrics from channel data"""
        if not channel_data or "channel" not in channel_data:
            return {}
            
        channel = channel_data["channel"]
        stats = channel.get("statistics", {})
        
        return {
            "subscribers": int(stats.get("subscriberCount", 0)),
            "view_count": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "subscriber_count_hidden": stats.get("hiddenSubscriberCount", False),
            "channel_created": channel.get("snippet", {}).get("publishedAt"),
            "country": channel.get("snippet", {}).get("country")
        }
    
    def extract_video_metrics(self, video_data: Dict) -> Dict:
        """Extract key metrics from video data"""
        if not video_data:
            return {}
            
        stats = video_data.get("statistics", {})
        snippet = video_data.get("snippet", {})
        
        return {
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "published_at": snippet.get("publishedAt"),
            "duration": video_data.get("contentDetails", {}).get("duration"),
            "title": snippet.get("title"),
            "description": snippet.get("description", "")[:500]  # Truncate for storage
        }