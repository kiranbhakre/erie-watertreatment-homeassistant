# Erie Water Treatment IQ26 — Home Assistant Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2023.1%2B-blue.svg)](https://www.home-assistant.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A Home Assistant custom integration for **Erie IQ26 water softeners** that connect via the Erie Connect (Pentair) cloud API.

Polls the cloud API every 120 seconds and exposes 15 sensors and 6 binary sensors — including remaining softening capacity, days until regeneration, water consumption for the Energy Dashboard, and per-category warning binary sensors.

> Forked from [tgebarowski/erie-watertreatment-homeassistant](https://github.com/tgebarowski/erie-watertreatment-homeassistant) and extended with additional sensors, device page support, and HACS compatibility.

---

## Features

- **Device page** — all entities grouped under one device card showing Name, Manufacturer, Model, Firmware version and Serial Number
- **Energy Dashboard** — cumulative water consumption sensor compatible with HA's built-in water panel
- **Live capacity sensors** — remaining %, remaining litres, days until next regeneration (direct from device firmware)
- **Warning binary sensors** — individual sensors per warning category (salt, filter, service, error) plus a catch-all
- **Derived time sensors** — days since last regeneration, days since last maintenance (calculated locally)
- **Holiday mode** — binary sensor that turns on when the softener is in bypass mode
- **Custom templates** — ready-to-paste YAML for template sensors, automations, and a full Lovelace dashboard

---

## Installation

### Option A — HACS (recommended)

1. Open **HACS** in Home Assistant → **Integrations**.
2. Click the ⋮ menu → **Custom repositories**.
3. Add `https://github.com/kiranbhakre/erie-watertreatment` with category **Integration**.
4. Search for **Erie Water Treatment IQ26** and click **Download**.
5. Restart Home Assistant.

### Option B — Manual

1. Download the [latest release](https://github.com/kiranbhakre/erie-watertreatment/releases) or clone this repo.
2. Copy the `custom_components/erie_watertreatment/` folder into your HA config:
   ```
   <ha-config-dir>/custom_components/erie_watertreatment/
   ```
3. Restart Home Assistant.

---

## Setup

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Erie Water Treatment IQ26**.
3. Enter your **Erie Connect** (Pentair) email and password.
4. The integration authenticates and selects the first active device automatically.

The device will appear under **Settings → Devices & Services** with all sensors and binary sensors grouped on one device page.

---

## Sensors

### Live Status (from dashboard API)

| Entity | Description | Unit |
|---|---|---|
| `sensor.erie_watertreatment_status_title` | Current device status, e.g. `In Service`, `Regenerating` | — |
| `sensor.erie_watertreatment_remaining_percentage` | Remaining softening capacity | % |
| `sensor.erie_watertreatment_remaining_litres` | Remaining softening capacity | L |
| `sensor.erie_watertreatment_days_remaining` | Days until the next auto-regeneration (from device firmware) | d |

### Water Usage

| Entity | Description | Unit |
|---|---|---|
| `sensor.erie_watertreatment_water_consumption` | Cumulative total volume — **Energy Dashboard compatible** | L |
| `sensor.erie_watertreatment_water_flow_rate` | Instantaneous flow rate (L/h), calculated between polls | L/h |
| `sensor.erie_watertreatment_total_volume` | Raw cumulative volume from the API | L |
| `sensor.erie_watertreatment_flow` | Volume delta since the previous poll | L |

### Maintenance & History

| Entity | Description | Unit |
|---|---|---|
| `sensor.erie_watertreatment_days_since_regeneration` | Days elapsed since the last regeneration cycle | d |
| `sensor.erie_watertreatment_days_since_maintenance` | Days elapsed since the last service visit | d |
| `sensor.erie_watertreatment_regeneration_count` | Total regeneration cycles since installation | — |
| `sensor.erie_watertreatment_last_regeneration` | ISO timestamp of the last regeneration | — |
| `sensor.erie_watertreatment_last_maintenance` | ISO date of the last maintenance visit | — |
| `sensor.erie_watertreatment_nr_regenerations` | Raw regeneration count string from the API | — |

### Warnings

| Entity | Description |
|---|---|
| `sensor.erie_watertreatment_warnings` | All active warnings as a formatted multi-line string |

---

## Binary Sensors

| Entity | Description | Device class |
|---|---|---|
| `binary_sensor.erie_watertreatment_low_salt` | On when any warning mentions salt | `problem` |
| `binary_sensor.erie_watertreatment_filter_warning` | On when any warning mentions "filter" | `problem` |
| `binary_sensor.erie_watertreatment_service_warning` | On when any warning mentions "service" | `problem` |
| `binary_sensor.erie_watertreatment_error_warning` | On when any warning mentions "error" | `problem` |
| `binary_sensor.erie_watertreatment_any_warning` | On when any warning is active | `problem` |
| `binary_sensor.erie_watertreatment_holiday_mode` | On when the softener is in bypass/holiday mode | `running` |

---

## Energy Dashboard

Add `sensor.erie_watertreatment_water_consumption` to the HA Energy Dashboard water panel:

1. **Settings → Energy → Water** → **Add Water Source**
2. Select `sensor.erie_watertreatment_water_consumption`
3. Set unit to **Litres (L)**

This sensor uses `device_class: water` and `state_class: total_increasing`, which is exactly what the HA Energy Dashboard requires for hourly / daily / monthly water statistics.

---

## Screenshots

<img src="img/entities-card.png" width="500" alt="Entities card showing all status sensors">

<img src="img/water-flow-week.png" width="700" alt="Weekly water consumption bar chart">

<img src="img/water-flow-24hrs.png" width="700" alt="24-hour water consumption bar chart">

---

## Custom Templates & Lovelace Dashboard

The `custom_templates/` folder contains ready-to-paste YAML files:

| File | Contents |
|---|---|
| [`sensors.yaml`](custom_templates/sensors.yaml) | Template sensors — formatted dates, daily average usage |
| [`binary_sensors.yaml`](custom_templates/binary_sensors.yaml) | Template binary sensors — maintenance overdue, high-flow alert |
| [`automations.yaml`](custom_templates/automations.yaml) | Example automations — low salt notify, maintenance alert, high flow alert |
| [`README.md`](custom_templates/README.md) | Full entity reference + complete Lovelace dashboard YAML |

Add to `configuration.yaml`:

```yaml
template:
  - sensor: !include custom_templates/sensors.yaml
  - binary_sensor: !include custom_templates/binary_sensors.yaml

automation: !include_dir_merge_list custom_templates/
```

---

## Requirements

- **Home Assistant** 2023.1 or later
- **Erie Connect** account (Pentair cloud login)
- Python package [`erie-connect==0.4.4`](https://github.com/tgebarowski/erie-connect) — installed automatically by HA

---

## Development & Testing

```bash
# Install test dependencies
pip install -r requirements_test.txt

# Run all tests
pytest tests/ -v
```

113 unit tests cover all sensors and binary sensors. No running HA instance is needed — all tests use mocked coordinators.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Integration not found in search | Make sure `custom_components/erie_watertreatment/` exists in your HA config dir and restart HA |
| Login fails | Verify credentials work at [my.eriewater.com](https://my.eriewater.com) |
| Sensors show `unavailable` | Check HA logs for API errors; the cloud API has occasional outages |
| Device page missing firmware / serial | These populate after the first successful poll; reload the integration if still blank |

---

## Credits

Original integration by [Tomasz Gebarowski](https://github.com/tgebarowski/erie-watertreatment-homeassistant).  
Extended by [kiranbhakre](https://github.com/kiranbhakre) — additional sensors, device page, HACS support, unit tests.
