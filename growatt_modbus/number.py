"""Number platform for Growatt Modbus."""
import logging

from homeassistant.components.number import NumberEntity, NumberMode
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
    """Set up Growatt Modbus number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]

    entities = [
        GrowattPowerLimitNumber(coordinator, entry, client),
    ]

    async_add_entities(entities)


class GrowattPowerLimitNumber(CoordinatorEntity, NumberEntity):
    """Number entity for power limit setting."""

    def __init__(self, coordinator, entry, client):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._entry = entry
        self._client = client
        self._attr_unique_id = f"{entry.entry_id}_power_limit"
        self._attr_name = f"{entry.data['name']} Power Limit"
        self._attr_icon = "mdi:gauge"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 5
        self._attr_native_unit_of_measurement = "%"
        self._attr_mode = NumberMode.SLIDER
        self._value = 100

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
    def native_value(self):
        """Return the current value."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Set new power limit value."""
        self._value = int(value)
        
        # Check if curtailment is active
        curtailment_switch_id = f"switch.{self._entry.data['name'].lower().replace(' ', '_')}_curtailment"
        curtailment_switch = self.hass.states.get(curtailment_switch_id)
        
        # Only apply immediately if curtailment is active
        if curtailment_switch and curtailment_switch.state == "on":
            await self.hass.async_add_executor_job(
                self._client.set_power_limit, self._value
            )
            await self.coordinator.async_request_refresh()
        
        self.async_write_ha_state()