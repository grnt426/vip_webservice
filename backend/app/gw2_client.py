import os
import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import asyncio

from .rate_limiter import TokenBucketRateLimiter
from app.models.guild_logs import create_log_entry

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GW2Client:
    def __init__(self):
        self.api_key = self._load_api_key()
        self.base_url = "https://api.guildwars2.com/v2"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # Initialize rate limiter with GW2 API limits
        self.rate_limiter = TokenBucketRateLimiter(bucket_size=300, refill_rate=5.0)
        logger.info(f"Initialized GW2 client with API key: {self.api_key[:8]}...")

        self.timeout = httpx.Timeout(30.0, connect=10.0)  # 30s read timeout, 10s connect timeout
        self.stale_after = timedelta(minutes=5)  # Consider data stale after 5 minutes

    def _load_api_key(self) -> str:
        """Load API key from .secrets file"""
        try:
            # Try to find .secrets in the app root directory
            secrets_paths = [
                '.secrets',  # Current directory
                '/app/.secrets',  # Docker container app directory
                os.path.join(os.path.dirname(__file__), '..', '..', '.secrets')  # Two levels up from this file
            ]
            
            for path in secrets_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('API_KEY='):
                                api_key = line.split('=', 1)[1].strip()
                                if api_key:
                                    return api_key
            
            logger.error("No valid API_KEY entry found in any .secrets file")
            raise Exception("No valid API key found in any .secrets file")
        except Exception as e:
            logger.error(f"Error loading API key: {str(e)}")
            raise Exception(f"Failed to load API key: {str(e)}")

    def is_data_stale(self, last_updated: Optional[datetime]) -> bool:
        """Check if data is stale and needs to be refreshed"""
        if not last_updated:
            return True
        return datetime.utcnow() - last_updated > self.stale_after

    async def _make_request(self, url: str) -> Dict[str, Any]:
        """Make a request to the GW2 API"""
        logger.info(f"Making request to: {url}")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers)
            
            if not response.is_success:
                logger.error(f"API Error response: {response.text}")
                return {}
            
            return response.json()

    async def _fetch_guild_logs(self, guild_id: str, last_log_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch guild logs from the GW2 API"""
        url = f"{self.base_url}/guild/{guild_id}/log"
        if last_log_id and last_log_id > 0:  # Only add since parameter if we have a valid last_log_id
            url += f"?since={last_log_id}"
        
        logger.info(f"Fetching guild logs from: {url}")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers)
            if not response.is_success:
                logger.error(f"Failed to fetch guild logs for {guild_id}: {response.status_code}")
                return []
            
            logs = response.json()
            logger.info(f"Received {len(logs)} logs for guild {guild_id}")
            return logs

    async def _fetch_guild_data(self, guild_id: str) -> Dict[str, Any]:
        """Fetch guild data from the GW2 API"""
        url = f"{self.base_url}/guild/{guild_id}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers)
            if not response.is_success:
                logger.error(f"Failed to fetch guild data for {guild_id}: {response.status_code}")
                return {}
            
            return response.json()

    async def _fetch_guild_members(self, guild_id: str) -> List[Dict[str, Any]]:
        """Fetch guild members from the GW2 API"""
        url = f"{self.base_url}/guild/{guild_id}/members"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers)
            if not response.is_success:
                logger.error(f"Failed to fetch guild members for {guild_id}: {response.status_code}")
                return []
            
            return response.json()

    async def _fetch_guild_ranks(self, guild_id: str) -> List[Dict[str, Any]]:
        """Fetch guild ranks from the GW2 API"""
        url = f"{self.base_url}/guild/{guild_id}/ranks"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers)
            if not response.is_success:
                logger.error(f"Failed to fetch guild ranks for {guild_id}: {response.status_code}")
                return []
            
            return response.json()

    async def get_guild_data(self, guild_id: str, last_log_id: Optional[int] = None) -> Dict[str, Any]:
        """Get all guild data from the GW2 API"""
        try:
            # Fetch all data concurrently
            guild_data, logs, members, ranks = await asyncio.gather(
                self._fetch_guild_data(guild_id),
                self._fetch_guild_logs(guild_id, last_log_id),
                self._fetch_guild_members(guild_id),
                self._fetch_guild_ranks(guild_id)
            )
            
            if not guild_data:
                logger.error(f"Failed to fetch basic guild data for {guild_id}")
                return {}
            
            # Add additional data to the response
            guild_data["members"] = members
            guild_data["ranks"] = ranks
            guild_data["logs"] = logs
            
            # Add the last log ID to track pagination
            if logs:
                guild_data["last_log_id"] = max(log["id"] for log in logs)
            else:
                guild_data["last_log_id"] = last_log_id or 0
            
            return guild_data
            
        except Exception as e:
            logger.error(f"Error fetching guild data for {guild_id}: {str(e)}", exc_info=True)
            return {} 