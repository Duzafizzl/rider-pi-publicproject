# Code Execution API

This directory contains the Python API for code execution environments.

## Files

- `rider_pi.py` - Python functions for Rider-Pi control

## Usage

```python
import rider_pi_code_api as rp

# Basic movement
rp.move_forward(2.0, 0.5)
rp.rotate(90, 0.5)
rp.stop()

# Sensor reading
battery = rp.get_battery_level()
tilt = rp.get_tilt_angle()

# Display control
rp.set_display_expression(1)
rp.set_rgb_light(0, 255, 0)
```

## Benefits

- **98.7% token savings** compared to tool calls
- Better control flow (loops, conditionals)
- Privacy-preserving (intermediate results stay local)
- State persistence

## Setup

Make sure the module is importable in your code execution environment:

```python
import sys
sys.path.append('/path/to/rider-pi-mcp/src/code_api')
import rider_pi_code_api as rp
```

See [Setup Guide](../../docs/setup/SETUP.md) for more details.

