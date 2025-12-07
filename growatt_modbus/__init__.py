"""Growatt Modbus Integration for Home Assistant."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .modbus_client import GrowattModbusClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.BUTTON]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Growatt Modbus component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Growatt Modbus from a config entry."""
    
    # Create Modbus client
    client = GrowattModbusClient(
        host=entry.data["host"],
        port=entry.data["port"],
        slave=entry.data["slave"],
        timeout=entry.data.get("timeout", 5),
    )
    
    # Create coordinator for data updates
    coordinator = GrowattDataUpdateCoordinator(
        hass,
        client=client,
        entry=entry,
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
    }
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["client"].close()
    
    return unload_ok


class GrowattDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Growatt data."""

    def __init__(self, hass, client, entry):
        """Initialize."""
        self.client = client
        self.entry = entry
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.data['name']}",
            update_interval=timedelta(seconds=5),
        )

    async def _async_update_data(self):
        """Fetch data from Growatt inverter."""
        try:
            return await self.hass.async_add_executor_job(self.client.read_all_data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with inverter: {err}")