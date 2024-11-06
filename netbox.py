import httpx
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.core import HomeAssistant
from typing import TypedDict


class IPAddress(TypedDict):
    ip: str
    desc: str
    tags: list[str]

class Netbox:
    base_url: str
    token: str

    def __init__(self, base_url:str, token: str, hass: HomeAssistant) -> None:
        self.base_url = base_url
        self.token = token
        self.hass = hass

    async def get_ip_addresses(self) -> list[IPAddress]:
        addresses = await self._get_ip_addresses()

        result: list[IPAddress] = []
        for address in addresses:
            result.append({
                'ip': self._remove_subnet_mask(address['address']),
                'desc': address['description'],
                'tags': [tag['slug'] for tag in address.get('tags', [])],
            })

        return result

    async def _get_ip_addresses(self):
        headers = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
        }

        ip_addresses = []
        url = f"{self.base_url}/api/ipam/ip-addresses/"

        async with get_async_client(self.hass) as client:
        # async with httpx.AsyncClient() as client:
            while url:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                ip_addresses.extend(data.get("results", []))

                url = data.get("next")

        return ip_addresses

    def _remove_subnet_mask(self, ip_address: str) -> str:
        return ip_address.split('/')[0]

