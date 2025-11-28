# Examples

This directory contains example code demonstrating how to use the Rider-Pi MCP integration.

## Basic Usage

See `basic_usage.py` for common operations:

- Basic movement (forward, backward, rotate, stop)
- Sensor reading (battery, tilt angle)
- Display and RGB light control
- Conditional behavior
- Movement sequences

## Running Examples

```bash
# Make sure Rider-Pi is connected and configured
export RIDER_PI_HOST="riderpi.local"
export RIDER_PI_USER="pi"
export RIDER_PI_SSH_KEY="~/.ssh/rider_pi_key"

# Run example
python3 examples/basic_usage.py
```

## Code Execution API

The examples use the Code Execution API, which provides:

- **98.7% token savings** compared to tool calls
- Better control flow (loops, conditionals)
- Privacy-preserving (intermediate results stay local)
- State persistence

## Example: Conditional Behavior

```python
import rider_pi_code_api as rp

# Check battery and react
battery = rp.get_battery_level()
if battery < 20:
    rp.set_display_expression(10)  # Warning
    rp.set_rgb_light(255, 0, 0)     # Red
    rp.move_forward(1.0, 0.3)       # To charging station
else:
    rp.set_display_expression(1)   # Happy
    rp.set_rgb_light(0, 255, 0)    # Green
```

## Example: Movement Sequence

```python
import rider_pi_code_api as rp

# Greeting sequence
rp.set_display_expression(1)      # Happy face
rp.set_rgb_light(0, 255, 0)       # Green light
rp.move_forward(0.5, 0.3)           # Small movement
rp.rotate(45, 0.3)                 # Wave right
rp.rotate(-45, 0.3)                # Wave left
rp.stop()
```

## More Examples

More examples will be added as features are implemented:

- Computer Vision examples
- Voice control examples
- Self-editing examples
- Advanced movement patterns

---

**Note:** All examples require actual Rider-Pi hardware and proper SSH configuration.

