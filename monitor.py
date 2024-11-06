import asyncio
import logging
from homeassistant.core import HomeAssistant
from .netbox import Netbox, IPAddress
from .socket_cheker import SocketChecker
from .telegram_bot import TelegramBot
from httpx import HTTPStatusError
from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)

failed_devices = set()

async def monitor(hass: HomeAssistant):
    config = hass.data[DOMAIN]
    netbox_token = config["netbox_token"]
    tg_bot_token = config["tg_bot_token"]
    chat_id = config["chat_id"]
    base_url = config["base_url"]
    modbus_port = config["modbus_port"]
    message_fail = config["message_fail"]
    message_success = config["message_success"]

    netbox = Netbox(base_url, netbox_token, hass)
    checker = SocketChecker(modbus_port)
    bot = TelegramBot(tg_bot_token, hass)

    try:
        ip_addresses = await netbox.get_ip_addresses()
        modbus_ip_addresses = filter_modbus_ip_addresses(ip_addresses)
        failed_list = await checker.check_failed(modbus_ip_addresses)

        current_failed_ips = {addr.get('ip') for addr in failed_list}
        new_failures = [addr for addr in failed_list if addr.get('ip') not in failed_devices]
        
        recovered_ips = failed_devices - current_failed_ips
        recovered_devices = [addr for addr in modbus_ip_addresses if addr.get('ip') in recovered_ips]

        if new_failures:
            await send_messages(new_failures, message_fail, bot, chat_id)
            failed_devices.update(addr.get('ip') for addr in new_failures)

        if recovered_devices:
            await send_messages(recovered_devices, message_success, bot, chat_id)
            failed_devices.difference_update(recovered_ips)

    except HTTPStatusError as e:
        _LOGGER.debug(f"HTTP error occurred: {e}")
    except Exception as e:
        _LOGGER.debug(f"An error occurred: {e}")

async def send_messages(addresses: list[IPAddress], msg: str, bot: TelegramBot, chat_id: str) -> str:
    for address in addresses:
        message = f"{address.get('ip')} - {address.get('desc')} - {msg}"
        await bot.send_telegram_message(message, chat_id)

    return msg

def filter_modbus_ip_addresses(addresses: list[IPAddress]) -> list[IPAddress]:
    modbus_ips = []

    for address in addresses:
        tags = address.get('tags', [])
        if any(tag.lower() == 'modbus' for tag in tags):
            modbus_ips.append(address)

    return modbus_ips

# async def main():
#     while True:
#         await monitor({})
#         await asyncio.sleep(10)

# asyncio.run(main())