import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta
from .const import DOMAIN, DEFAULT_DELAY, DEFAULT_MESSAGE_FAIL, DEFAULT_MESSAGE_SUCCESS, DEFAULT_PORT
from .monitor import monitor


_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Modbus component."""
    if DOMAIN not in config:
        return True

    modbus_config = config[DOMAIN]
    netbox_token = modbus_config.get("netbox_token")
    tg_bot_token = modbus_config.get("tg_bot_token")
    chat_id = modbus_config.get("chat_id")
    base_url = modbus_config.get("base_url")
    modbus_port = modbus_config.get("modbus_port", DEFAULT_PORT)
    message_fail = modbus_config.get("message_fail", DEFAULT_MESSAGE_FAIL)
    message_success = modbus_config.get("message_success", DEFAULT_MESSAGE_SUCCESS)
    delay = modbus_config.get("delay", DEFAULT_DELAY)

    if not (netbox_token and tg_bot_token and chat_id and base_url):
        _LOGGER.error("Required configuration parameters are missing for modbusmonitor.")
        return False

    hass.data[DOMAIN] = {
        "netbox_token": netbox_token,
        "tg_bot_token": tg_bot_token,
        "chat_id": chat_id,
        "base_url": base_url,
        "modbus_port": modbus_port,
        "message_fail": message_fail,
        "message_success": message_success
    }
    
    try:
        async_track_time_interval(
            hass,
            lambda now: hass.loop.create_task(monitor(hass)),
            timedelta(seconds=delay)
        )
        return True
    except Exception as e:
        _LOGGER.error(f"Failed to set up modbusmonitor: {e}")
        return False