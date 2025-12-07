"""Constants for Growatt Modbus integration."""

DOMAIN = "growatt_modbus"

# Configuration
CONF_SLAVE = "slave"
CONF_INVERTER_NAME = "name"

# Default values
DEFAULT_PORT = 502
DEFAULT_SLAVE = 1
DEFAULT_TIMEOUT = 5
DEFAULT_SCAN_INTERVAL = 5

# Modbus register addresses
REGISTERS = {
    # Status
    "status": {"address": 0, "type": "input", "data_type": "uint16"},
    
    # PV Strings
    "pv1_voltage": {"address": 3, "type": "input", "data_type": "uint16", "scale": 0.1},
    "pv1_current": {"address": 4, "type": "input", "data_type": "uint16", "scale": 0.1},
    "pv2_voltage": {"address": 7, "type": "input", "data_type": "uint16", "scale": 0.1},
    "pv2_current": {"address": 8, "type": "input", "data_type": "uint16", "scale": 0.1},
    
    # AC Output
    "ac_frequency": {"address": 37, "type": "input", "data_type": "uint16", "scale": 0.01},
    "ac_power": {"address": 36, "type": "input", "data_type": "uint16", "scale": 0.1},
    "ac_voltage": {"address": 38, "type": "input", "data_type": "uint16", "scale": 0.1},
    "ac_current": {"address": 39, "type": "input", "data_type": "uint16", "scale": 0.1},
    
    # Energy
    "today_energy": {"address": 53, "type": "input", "data_type": "uint32", "scale": 0.1},
    "total_energy": {"address": 91, "type": "input", "data_type": "uint32", "scale": 0.1},
    
    # Temperature
    "temperature": {"address": 93, "type": "input", "data_type": "uint16", "scale": 0.1},
    
    # Control
    "cmd_memory": {"address": 2, "type": "holding", "data_type": "uint16"},
    "power_limit": {"address": 3, "type": "holding", "data_type": "uint16"},
    "inverter_enable": {"address": 0, "type": "holding", "data_type": "uint16"},
}

# Status codes
STATUS_CODES = {
    0: "Standby",
    1: "Normal",
    3: "Fault",
}

# Inverter model
MODEL = "MIN5000TL-X"