"""Switch platform for Growatt Modbus."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Growatt Modbus switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]

    entities = [
        GrowattInverterEnableSwitch(coordinator, entry, client),
        GrowattCurtailmentSwitch(coordinator, entry, client),
    ]

    async_add_entities(entities)


class GrowattInverterEnableSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to enable/disable the inverter."""

    def __init__(self, coordinator, entry, client):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._client = client
        self._attr_unique_id = f"{entry.entry_id}_inverter_enable"
        self._attr_name = f"{entry.data['name']} Enable"
        self._attr_icon = "mdi:power"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.data["name"],
            "manufacturer": "Growatt",
            "model": "MIN5000TL-X",
        }

    @property
    def is_on(self):
        """Return true if inverter is enabled."""
        # Status 1 = Normal/Online
        status = self.coordinator.data.get("status")
        return status == 1 if status is not None else None

    async def async_turn_on(self, **kwargs):
        """Turn on the inverter."""
        await self.hass.async_add_executor_job(self._client.set_inverter_enable, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn off the inverter."""
        await self.hass.async_add_executor_job(self._client.set_inverter_enable, False)
        await self.coordinator.async_request_refresh()


class GrowattCurtailmentSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to enable/disable power curtailment."""

    def __init__(self, coordinator, entry, client):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._client = client
        self._attr_unique_id = f"{entry.entry_id}_curtailment"
        self._attr_name = f"{entry.data['name']} Curtailment"
        self._attr_icon = "mdi:solar-power-variant-outline"
        self._is_on = False

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.data["name"],
            "manufacturer": "Growatt",
            "model": "MIN5000TL-X",
        }

    @property
    def is_on(self):
        """Return true if curtailment is active."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Enable curtailment."""
        # Get power limit from number entity
        number_entity_id = f"number.{self._entry.data['name'].lower().replace(' ', '_')}_power_limit"
        limit = self.hass.states.get(number_entity_id)
        limit_value = int(float(limit.state)) if limit else 50
        
        await self.hass.async_add_executor_job(
            self._client.set_power_limit, limit_value
        )
        self._is_on = True
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Disable curtailment (set to 100%)."""
        await self.hass.async_add_executor_job(self._client.set_power_limit, 100)
        self._is_on = False
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()