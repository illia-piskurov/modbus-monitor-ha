import asyncio
from .netbox import IPAddress


class SocketChecker:
    port: int

    def __init__(self, port: int) -> None:
        self.port = port

    async def check_failed(self, ip_addresses: list[IPAddress]) -> list[IPAddress]:
        check_results = await self.check(ip_addresses)
        return [address for (address, flag) in check_results if not flag]

    async def check(self, ip_addresses: list[IPAddress]) -> list[tuple[IPAddress, bool]]:
        tasks = [
            self._check_ip(address) for address in ip_addresses
        ]
        check_results = await asyncio.gather(*tasks)

        return check_results

    async def _check_ip(self, address: IPAddress) -> tuple[IPAddress, bool]:
        result = await self._is_port_open(address.get('ip'), self.port)
        return address, result

    async def _is_port_open(self, ip: str, port: int, timeout: float = 5.0) -> bool:
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port),
                timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return False