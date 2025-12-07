"""Modbus client for Growatt inverters."""
import logging
import struct
from typing import Any

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import REGISTERS

_LOGGER = logging.getLogger(__name__)


class GrowattModbusClient:
    """Growatt Modbus TCP client."""

    def __init__(self, host: str, port: int, slave: int, timeout: int = 5):
        """Initialize the Modbus client."""
        self.host = host
        self.port = port
        self.slave = slave
        self.timeout = timeout
        self._client = ModbusTcpClient(
            host=host,
            port=port,
            timeout=timeout,
        )

    def connect(self) -> bool:
        """Connect to the Modbus device."""
        if not self._client.connected:
            return self._client.connect()
        return True

    async def close(self):
        """Close the Modbus connection."""
        if self._client.connected:
            self._client.close()

    def read_register(self, address: int, count: int = 1, register_type: str = "input") -> list:
        """Read from a Modbus register."""
        if not self.connect():
            raise ModbusException("Failed to connect to inverter")

        try:
            if register_type == "input":
                result = self._client.read_input_registers(address, count, slave=self.slave)
            else:  # holding
                result = self._client.read_holding_registers(address, count, slave=self.slave)

            if result.isError():
                raise ModbusException(f"Error reading register {address}")

            return result.registers
        except Exception as e:
            _LOGGER.error(f"Error reading register {address}: {e}")
            raise

    def write_register(self, address: int, value: int, register_type: str = "holding") -> bool:
        """Write to a Modbus register."""
        if not self.connect():
            raise ModbusException("Failed to connect to inverter")

        try:
            if register_type == "holding":
                result = self._client.write_register(address, value, slave=self.slave)
                return not result.isError()
            else:
                raise ValueError("Can only write to holding registers")
        except Exception as e:
            _LOGGER.error(f"Error writing register {address}: {e}")
            raise

    def read_all_data(self) -> dict[str, Any]:
        """Read all data from the inverter."""
        data = {}
        
        for key, reg_info in REGISTERS.items():
            try:
                address = reg_info["address"]
                reg_type = reg_info["type"]
                data_type = reg_info["data_type"]
                
                # Determine count based on data type
                count = 2 if data_type == "uint32" else 1
                
                # Read register
                registers = self.read_register(address, count, reg_type)
                
                # Parse value
                if data_type == "uint16":
                    value = registers[0]
                elif data_type == "uint32":
                    # Combine two registers for 32-bit value
                    value = (registers[0] << 16) | registers[1]
                else:
                    value = registers[0]
                
                # Apply scaling if present
                if "scale" in reg_info:
                    value = value * reg_info["scale"]
                
                data[key] = value
                
            except Exception as e:
                _LOGGER.warning(f"Failed to read {key}: {e}")
                data[key] = None
        
        # Calculate PV power
        if all(data.get(k) is not None for k in ["pv1_voltage", "pv1_current", "pv2_voltage", "pv2_current"]):
            data["pv_power"] = (
                data["pv1_voltage"] * data["pv1_current"] +
                data["pv2_voltage"] * data["pv2_current"]
            )
        else:
            data["pv_power"] = None
        
        return data

    def enable_cmd_memory(self) -> bool:
        """Enable command memory mode."""
        return self.write_register(REGISTERS["cmd_memory"]["address"], 1)

    def set_power_limit(self, limit_percent: int) -> bool:
        """Set power limit (0-100%)."""
        if not 0 <= limit_percent <= 100:
            raise ValueError("Power limit must be between 0 and 100")
        
        # Enable command memory first
        self.enable_cmd_memory()
        
        # Set power limit
        return self.write_register(REGISTERS["power_limit"]["address"], limit_percent)

    def set_inverter_enable(self, enable: bool) -> bool:
        """Enable or disable the inverter."""
        value = 1 if enable else 0
        return self.write_register(REGISTERS["inverter_enable"]["address"], value)