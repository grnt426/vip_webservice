import httpx
from typing import Any, Dict


def build_guild_entry(name, id):
    return {"name": name, "id": id}


class GuildWars2APIClient:
    BASE_URL = "https://api.guildwars2.com/v2"

    GUILD_IDS = [
        build_guild_entry("power", "C8260C3D-F677-E711-80D4-E4115BEBA648"),
        build_guild_entry("primal", "4C345327-7D78-E711-80D4-E4115BEBA648"),
        build_guild_entry("phoenix", "BDEF3AB3-7F78-E711-80DA-101F7433AF15"),
        build_guild_entry("pain", "11605C96-8578-E711-80DA-101F7433AF15"),
        build_guild_entry("perfect", "5C59E515-A66D-E811-81A8-83C7278578E0"),
        build_guild_entry("pips", "90EE62DE-B813-EF11-BA1F-12061042B485"),
    ]

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def fetch_guild_details(self, guild_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/guild/{guild_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def fetch_guild_logs(self, guild_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/guild/{guild_id}/log"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

