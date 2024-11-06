import logging
import httpx
from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client


_LOGGER = logging.getLogger(__name__)

class TelegramBot:
    token: str

    def __init__(self, token: str, hass: HomeAssistant):
        self.token = token
        self.hass = hass

    async def send_telegram_message(self, message: str, chat_id: str):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        async with get_async_client(self.hass) as client:
        # async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                _LOGGER.debug("Success send message.")
            else:
                _LOGGER.debug(f"Error while send message: {response.status_code}")