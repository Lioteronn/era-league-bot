import aiohttp
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class BloxlinkAPI:
    """
    Utility class for interacting with the Bloxlink API
    """
    BASE_URL = "https://api.blox.link/v4/public"
    
    @staticmethod
    async def get_roblox_user(server_id: int, discord_id: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if a Discord user is verified with Bloxlink and get their Roblox info.
        
        Args:
            server_id: The Discord server ID
            discord_id: The Discord user ID
            
        Returns:
            Tuple containing:
                - Success status (True if verified, False if not)
                - User data if verified, or None if not verified
        """
        url = f"{BloxlinkAPI.BASE_URL}/guilds/{server_id}/discord-to-roblox/{discord_id}"
        headers = {
            'Authorization': '819a60d0-21b2-4a93-acc6-abfc19d8f013'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return True, data
                    elif response.status == 404:
                        # User not found/not verified
                        return False, None
                    else:
                        # Other API error
                        logger.error(f"Bloxlink API error: {response.status}, {await response.text()}")
                        return False, None
        except Exception as e:
            logger.error(f"Error checking Bloxlink verification: {str(e)}")
            return False, None
