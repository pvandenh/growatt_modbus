# Growatt Modbus Custom Integration for Home Assistant

A Home Assistant custom integration for Growatt MIN5000TL-X inverters via Modbus TCP. Supports multiple inverters with individual and combined statistics.

## Features

- **Multiple Inverter Support**: Add as many inverters as you need
- **Comprehensive Monitoring**:
  - PV string voltage and current (PV1, PV2)
  - AC output power, voltage, current, and frequency
  - Daily and total energy production
  - Inverter temperature and status
  - Calculated PV power
- **Power Control**:
  - Enable/disable inverter
  - Power curtailment (0-100%)
  - Configurable power limit slider
- **Combined Statistics**: Use Home Assistant template sensors to combine data from multiple inverters
- **Config Flow**: Easy setup through the UI

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right and select "Custom repositories"
4. Add this repository URL and select "Integration" as the category
5. Click "Install"
6. Restart Home Assistant

### Manual Installation

1. Copy the `growatt_modbus` folder to your `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

### Adding an Inverter

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Growatt Modbus"
4. Enter the inverter details:
   - **Name**: Friendly name (e.g., "Growatt Inverter 1")
   - **Host**: IP address of the inverter
   - **Port**: Modbus TCP port (default: 502)
   - **Slave ID**: Modbus slave ID (default: 1)
   - **Timeout**: Connection timeout in seconds (default: 5)

### Adding Multiple Inverters

Simply repeat the above process for each inverter. Each will have its own set of entities with the name you specified.

### Creating Combined Statistics

After adding multiple inverters, you can create template sensors to combine their statistics. Add this to your `configuration.yaml`:

```yaml
template:
  - sensor:
      # Combined PV Power
      - name: "Growatt Combined PV Power"
        unique_id: growatt_combined_pv_power
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        state: >
          {% set inv1 = states('sensor.growatt_inverter_1_pv_power') | float(0) %}
          {% set inv2 = states('sensor.growatt_inverter_2_pv_power') | float(0) %}
          {{ (inv1 + inv2) | round(0) }}
      
      # Combined AC Output Power
      - name: "Growatt Combined AC Output Power"
        unique_id: growatt_combined_ac_power
        unit_of_measurement: "W"
        device_class: power
        state_class: measurement
        state: >
          {% set inv1 = states('sensor.growatt_inverter_1_ac_output_power') | float(0) %}
          {% set inv2 = states('sensor.growatt_inverter_2_ac_output_power') | float(0) %}
          {{ (inv1 + inv2) | round(0) }}
      
      # Combined Today Energy
      - name: "Growatt Combined Today Energy"
        unique_id: growatt_combined_today_energy
        unit_of_measurement: "kWh"
        device_class: energy
        state_class: total_increasing
        state: >
          {% set inv1 = states('sensor.growatt_inverter_1_today_energy') | float(0) %}
          {% set inv2 = states('sensor.growatt_inverter_2_today_energy') | float(0) %}
          {{ (inv1 + inv2) | round(1) }}
      
      # Combined Total Energy
      - name: "Growatt Combined Total Energy"
        unique_id: growatt_combined_total_energy
        unit_of_measurement: "kWh"
        device_class: energy
        state_class: total_increasing
        state: >
          {% set inv1 = states('sensor.growatt_inverter_1_total_energy') | float(0) %}
          {% set inv2 = states('sensor.growatt_inverter_2_total_energy') | float(0) %}
          {{ (inv1 + inv2) | round(1) }}
```

## Entities Created

For each inverter, the following entities are created:

### Sensors
- `sensor.{name}_pv1_voltage` - PV String 1 Voltage
- `sensor.{name}_pv1_current` - PV String 1 Current
- `sensor.{name}_pv2_voltage` - PV String 2 Voltage
- `sensor.{name}_pv2_current` - PV String 2 Current
- `sensor.{name}_pv_power` - Total PV Power (calculated)
- `sensor.{name}_ac_output_power` - AC Output Power
- `sensor.{name}_ac_voltage` - AC Voltage
- `sensor.{name}_ac_current` - AC Current
- `sensor.{name}_ac_frequency` - AC Frequency
- `sensor.{name}_today_energy` - Today's Energy Production
- `sensor.{name}_total_energy` - Total Energy Production
- `sensor.{name}_temperature` - Inverter Temperature
- `sensor.{name}_status` - Inverter Status

### Switches
- `switch.{name}_enable` - Enable/Disable Inverter
- `switch.{name}_curtailment` - Enable/Disable Power Curtailment

### Numbers
- `number.{name}_power_limit` - Power Limit Setting (0-100%)

## Usage

### Power Curtailment

To limit the inverter's output power:

1. Set the desired power limit using the **Power Limit** slider (0-100%)
2. Turn on the **Curtailment** switch to activate the limit
3. Turn off the **Curtailment** switch to return to full power (100%)

The power limit can be adjusted while curtailment is active - changes apply immediately.

### Automations Example

```yaml
automation:
  # Reduce power during peak pricing
  - alias: "Solar Curtailment - Peak Hours"
    trigger:
      - platform: time
        at: "14:00:00"
    action:
      - service: number.set_value
        target:
          entity_id: number.growatt_inverter_1_power_limit
        data:
          value: 70
      - service: switch.turn_on
        target:
          entity_id: switch.growatt_inverter_1_curtailment
  
  # Restore full power
  - alias: "Solar Curtailment - Off Peak"
    trigger:
      - platform: time
        at: "19:00:00"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.growatt_inverter_1_curtailment
```

## Troubleshooting

### Connection Issues

- Verify the inverter's IP address and port
- Check that Modbus TCP is enabled on the inverter
- Ensure your Home Assistant instance can reach the inverter's network
- Try increasing the timeout value in the integration options

### Status Codes

- **Standby**: Inverter is on but not producing (e.g., at night)
- **Normal**: Inverter is operating normally
- **Fault**: Inverter has detected a fault condition

### Multiple Inverters on Same Host

If you have multiple inverters sharing one Modbus gateway, ensure:
- Each inverter has a unique slave ID
- Use the appropriate port for each connection
- Consider adding a small delay between requests if experiencing communication issues

## Contributing

Contributions are welcome! Please submit issues and pull requests on GitHub.

## License

This project is licensed under the MIT License.

## Credits

Based on the Growatt Modbus protocol for MIN5000TL-X inverters.