# Erie Water Treatment — Custom Templates

Ready-to-paste YAML for Home Assistant template sensors, binary sensors, automations, and a Lovelace dashboard.

---

## Quick Start

Add the following includes to your `configuration.yaml`:

```yaml
template:
  - sensor: !include custom_templates/sensors.yaml
  - binary_sensor: !include custom_templates/binary_sensors.yaml

automation: !include_dir_merge_list custom_templates/
```

> **Note:** If you already use `automation: !include automations.yaml`, add
> the Erie automations manually from `automations.yaml` instead.

---

## Entity ID Reference

### Sensors (from Python integration)

| Entity ID | Description |
|---|---|
| `sensor.erie_watertreatment_water_consumption` | Cumulative water use (L) — Energy Dashboard |
| `sensor.erie_watertreatment_water_flow_rate` | Instantaneous flow rate (L/h) |
| `sensor.erie_watertreatment_last_regeneration` | Last regeneration ISO timestamp |
| `sensor.erie_watertreatment_nr_regenerations` | Total regeneration count |
| `sensor.erie_watertreatment_last_maintenance` | Last maintenance ISO date |
| `sensor.erie_watertreatment_total_volume` | Total volume used (L) |
| `sensor.erie_watertreatment_warnings` | Active warnings as formatted text |
| `sensor.erie_watertreatment_days_since_regeneration` | Days since last regeneration |
| `sensor.erie_watertreatment_next_regeneration_in` | Days until next regeneration due |
| `sensor.erie_watertreatment_days_since_maintenance` | Days since last maintenance |
| `sensor.erie_watertreatment_regeneration_count` | Regeneration count (for statistics) |

### Binary Sensors (from Python integration)

| Entity ID | Description |
|---|---|
| `binary_sensor.erie_watertreatment_low_salt` | On when any warning mentions "salt" |
| `binary_sensor.erie_watertreatment_filter_warning` | On when any warning mentions "filter" |
| `binary_sensor.erie_watertreatment_service_warning` | On when any warning mentions "service" |
| `binary_sensor.erie_watertreatment_error_warning` | On when any warning mentions "error" |
| `binary_sensor.erie_watertreatment_any_warning` | On when any warning is active |

### Template Sensors (from sensors.yaml)

| Entity ID | Description |
|---|---|
| `sensor.erie_last_regeneration_formatted` | Human-readable regeneration date/time |
| `sensor.erie_last_maintenance_formatted` | Human-readable maintenance date |
| `sensor.erie_days_since_regeneration` | YAML fallback (integer days) |
| `sensor.erie_days_since_maintenance` | YAML fallback (integer days) |
| `sensor.erie_avg_litres_per_day` | Rolling average daily water usage |
| `sensor.erie_regeneration_overdue` | `'true'`/`'false'` string based on 7-day threshold |

### Template Binary Sensors (from binary_sensors.yaml)

| Entity ID | Description |
|---|---|
| `binary_sensor.erie_maintenance_overdue` | On when maintenance > 365 days ago |
| `binary_sensor.erie_high_flow_alert` | On when flow > 500 L/h for 60 s (leak detection) |
| `binary_sensor.erie_regeneration_overdue_binary` | On when regeneration overdue (>7 days) |

---

## Configurable Thresholds

| Threshold | Where to change | Default |
|---|---|---|
| Regeneration interval | `const.py` → `REGEN_INTERVAL_DAYS` | 7 days |
| Regen overdue (templates) | `binary_sensors.yaml` → `threshold = 7` | 7 days |
| High flow alert | `binary_sensors.yaml` → `flow > 500` | 500 L/h |
| Maintenance overdue | `binary_sensors.yaml` → `days > 365` | 365 days |

---

## Lovelace Dashboard

Copy and paste the YAML below into a new dashboard view (**Settings → Dashboards → Add Dashboard → YAML mode**).

> The `custom:mini-graph-card` requires [mini-graph-card](https://github.com/kalkih/mini-graph-card) from HACS. All other cards use standard HA cards.

```yaml
title: Erie Water Softener
path: erie-water-softener
icon: mdi:water-pump

cards:

  # ── Row 1: Regeneration gauge + warning status ───────────────────────────
  - type: horizontal-stack
    cards:

      - type: gauge
        entity: sensor.erie_watertreatment_days_since_regeneration
        name: Days Since Regen
        unit: d
        min: 0
        max: 14
        needle: true
        severity:
          green: 0
          yellow: 5
          red: 7

      - type: entity
        entity: binary_sensor.erie_watertreatment_low_salt
        name: Low Salt
        icon: mdi:shaker-outline
        state_color: true

      - type: entity
        entity: binary_sensor.erie_watertreatment_any_warning
        name: Active Warnings
        icon: mdi:alert
        state_color: true

  # ── Row 2: Active warnings (only shown when warnings are active) ─────────
  - type: conditional
    conditions:
      - entity: binary_sensor.erie_watertreatment_any_warning
        state: "True"
    card:
      type: markdown
      title: Active Warnings
      content: >
        {{ states('sensor.erie_watertreatment_warnings') }}

  # ── Row 3: Status sensors ────────────────────────────────────────────────
  - type: entities
    title: Softener Status
    show_header_toggle: false
    entities:
      - entity: sensor.erie_last_regeneration_formatted
        name: Last Regeneration
        icon: mdi:recycle
      - entity: sensor.erie_watertreatment_days_since_regeneration
        name: Days Since Regeneration
        icon: mdi:clock-outline
      - entity: sensor.erie_watertreatment_next_regeneration_in
        name: Next Regeneration In
        icon: mdi:clock-fast
      - entity: sensor.erie_watertreatment_regeneration_count
        name: Total Regenerations
        icon: mdi:counter
      - entity: sensor.erie_last_maintenance_formatted
        name: Last Maintenance
        icon: mdi:tools
      - entity: sensor.erie_watertreatment_days_since_maintenance
        name: Days Since Maintenance
        icon: mdi:clock-outline
      - entity: sensor.erie_watertreatment_total_volume
        name: Total Volume Used (L)
        icon: mdi:water
      - entity: sensor.erie_avg_litres_per_day
        name: Average Daily Usage
        icon: mdi:water-percent

  # ── Row 4: Water consumption history ────────────────────────────────────
  - type: history-graph
    title: Water Consumption (7 days)
    hours_to_show: 168
    refresh_interval: 300
    entities:
      - entity: sensor.erie_watertreatment_water_consumption
        name: Total Volume (L)

  # ── Row 5: Flow rate graph (requires mini-graph-card from HACS) ──────────
  - type: custom:mini-graph-card
    entities:
      - entity: sensor.erie_watertreatment_water_flow_rate
        name: Flow Rate
    name: Water Flow Rate (L/h)
    hours_to_show: 24
    points_per_hour: 6
    smoothing: true
    show:
      extrema: true
      average: true
      icon: true
    color_thresholds:
      - value: 0
        color: "#03a9f4"
      - value: 300
        color: "#f39c12"
      - value: 500
        color: "#e74c3c"

  # ── Row 6: Maintenance overdue alert (only shown when overdue) ───────────
  - type: conditional
    conditions:
      - entity: binary_sensor.erie_maintenance_overdue
        state: "on"
    card:
      type: markdown
      title: Service Required
      content: >
        **⚠️ Maintenance is overdue.**
        Last service: {{ states('sensor.erie_last_maintenance_formatted') }}
        ({{ states('sensor.erie_watertreatment_days_since_maintenance') }} days ago)

  # ── Row 7: Warning binary sensors overview ───────────────────────────────
  - type: glance
    title: Warning Sensors
    show_state: true
    entities:
      - entity: binary_sensor.erie_watertreatment_low_salt
        name: Salt
      - entity: binary_sensor.erie_watertreatment_filter_warning
        name: Filter
      - entity: binary_sensor.erie_watertreatment_service_warning
        name: Service
      - entity: binary_sensor.erie_watertreatment_error_warning
        name: Error
      - entity: binary_sensor.erie_watertreatment_any_warning
        name: Any
      - entity: binary_sensor.erie_maintenance_overdue
        name: Maint.
      - entity: binary_sensor.erie_high_flow_alert
        name: High Flow
```
