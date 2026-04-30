# Erie Water Treatment IQ26 — Home Assistant Integration

A Home Assistant custom integration for Erie IQ26 water softeners that connect via the **Erie Connect** (Pentair) cloud API.

> **Note:** This is a fork of [tgebarowski/erie-watertreatment-homeassistant](https://github.com/tgebarowski/erie-watertreatment-homeassistant) with additional sensors, binary sensors, device page support, and HACS compatibility.

---

## Installation

### Option A — HACS (recommended)

1. Open HACS in Home Assistant → **Integrations**.
2. Click the three-dot menu → **Custom repositories**.
3. Add `https://github.com/kiranbhakre/erie-watertreatment` as category **Integration**.
4. Search for **Erie Water Treatment** and install.
5. Restart Home Assistant.

### Option B — Manual

1. Download or clone this repository.
2. Copy the `custom_components/erie_watertreatment/` folder into your HA config directory:
   ```
   <ha-config>/custom_components/erie_watertreatment/
   ```
3. Restart Home Assistant.

---

## Setup

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Erie Water Treatment IQ26**.
3. Enter your **Erie Connect** email and password.
4. The integration discovers your device automatically.

---

## Sensors

| Entity ID | Description | Unit |
|---|---|---|
| `sensor.erie_watertreatment_water_consumption` | Cumulative volume (Energy Dashboard) | L |
| `sensor.erie_watertreatment_water_flow_rate` | Instantaneous flow rate | L/h |
| `sensor.erie_watertreatment_flow` | Volume delta since last poll | L |
| `sensor.erie_watertreatment_last_regeneration` | Last regeneration timestamp | — |
| `sensor.erie_watertreatment_nr_regenerations` | Total regenerations (raw) | — |
| `sensor.erie_watertreatment_last_maintenance` | Last maintenance date | — |
| `sensor.erie_watertreatment_total_volume` | Total litres softened | L |
| `sensor.erie_watertreatment_warnings` | Active warnings (formatted text) | — |
| `sensor.erie_watertreatment_days_since_regeneration` | Days since last regen | d |
| `sensor.erie_watertreatment_days_since_maintenance` | Days since last maintenance | d |
| `sensor.erie_watertreatment_regeneration_count` | Total regen count (statistics) | — |
| `sensor.erie_watertreatment_status_title` | Current status (e.g. "In Service") | — |
| `sensor.erie_watertreatment_remaining_percentage` | Remaining softening capacity | % |
| `sensor.erie_watertreatment_remaining_litres` | Remaining softening capacity | L |
| `sensor.erie_watertreatment_days_remaining` | Days until next auto-regen | d |

## Binary Sensors

| Entity ID | Description |
|---|---|
| `binary_sensor.erie_watertreatment_low_salt` | On when a "salt" warning is active |
| `binary_sensor.erie_watertreatment_filter_warning` | On when a "filter" warning is active |
| `binary_sensor.erie_watertreatment_service_warning` | On when a "service" warning is active |
| `binary_sensor.erie_watertreatment_error_warning` | On when an "error" warning is active |
| `binary_sensor.erie_watertreatment_any_warning` | On when any warning is present |
| `binary_sensor.erie_watertreatment_holiday_mode` | On when device is in bypass/holiday mode |

---

## Energy Dashboard

`sensor.erie_watertreatment_water_consumption` uses `device_class: water` and `state_class: total_increasing` — add it directly in **Settings → Energy → Water** to get hourly/daily/monthly water graphs.

---

## Custom Templates & Lovelace Dashboard

The `custom_templates/` folder contains ready-to-paste YAML:

| File | Contents |
|---|---|
| `sensors.yaml` | Template sensors (formatted dates, daily average, etc.) |
| `binary_sensors.yaml` | Template binary sensors (maintenance overdue, high flow alert) |
| `automations.yaml` | Example automations (low salt notify, maintenance alert, etc.) |
| `README.md` | Full entity reference + Lovelace dashboard YAML |

See [`custom_templates/README.md`](custom_templates/README.md) for setup instructions and the full Lovelace dashboard.

---

## Requirements

- Home Assistant 2023.1+
- Erie Connect account (Pentair cloud)
- [`erie-connect`](https://github.com/tgebarowski/erie-connect) Python package (installed automatically)

---

## Development & Tests

```bash
pip install -r requirements_test.txt
pytest tests/ -v
```

All sensor and binary sensor logic is unit-tested without a running HA instance.

---

## Credits

Original integration by [Tomasz Gebarowski](https://github.com/tgebarowski).  
Extended with additional sensors, device page, and HACS support by [kiranbhakre](https://github.com/kiranbhakre).
