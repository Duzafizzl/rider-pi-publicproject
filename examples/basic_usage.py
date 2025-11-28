"""
Basic usage examples for Rider-Pi MCP integration.

This file demonstrates how to use the Rider-Pi Code API for common operations.
"""

import sys
import os

# Add code_api to path (adjust if needed)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'code_api'))

try:
    import rider_pi as rp
except ImportError:
    print("ERROR: Could not import rider_pi module.")
    print("Make sure the code_api is in your Python path.")
    sys.exit(1)


def example_basic_movement():
    """Example: Basic robot movement"""
    print("Example 1: Basic Movement")
    print("-" * 40)
    
    # Move forward for 2 seconds at 50% speed
    print("Moving forward...")
    rp.move_forward(2.0, 0.5)
    
    # Rotate 90 degrees
    print("Rotating 90 degrees...")
    rp.rotate(90, 0.5)
    
    # Stop
    print("Stopping...")
    rp.stop()
    
    print("Done!\n")


def example_sensor_reading():
    """Example: Reading sensors"""
    print("Example 2: Sensor Reading")
    print("-" * 40)
    
    # Get battery level
    battery = rp.get_battery_level()
    print(f"Battery Level: {battery}%")
    
    # Get tilt angle
    tilt = rp.get_tilt_angle()
    print(f"Tilt Angle: Roll={tilt['roll']}°, Pitch={tilt['pitch']}°, Yaw={tilt['yaw']}°")
    
    print("Done!\n")


def example_display_control():
    """Example: Display and RGB light control"""
    print("Example 3: Display Control")
    print("-" * 40)
    
    # Set display expression (e.g., happy face)
    print("Setting display expression...")
    rp.set_display_expression(1)
    
    # Set RGB light to green
    print("Setting RGB light to green...")
    rp.set_rgb_light(0, 255, 0)
    
    print("Done!\n")


def example_conditional_behavior():
    """Example: Conditional behavior based on sensor data"""
    print("Example 4: Conditional Behavior")
    print("-" * 40)
    
    # Check battery level
    battery = rp.get_battery_level()
    print(f"Battery Level: {battery}%")
    
    if battery < 20:
        # Low battery warning
        print("⚠️  Low battery! Showing warning...")
        rp.set_display_expression(10)  # Warning expression
        rp.set_rgb_light(255, 0, 0)   # Red light
        rp.move_forward(1.0, 0.3)       # Slow movement to charging station
    else:
        # Normal operation
        print("✅ Battery OK. Normal operation.")
        rp.set_display_expression(1)   # Happy expression
        rp.set_rgb_light(0, 255, 0)    # Green light
    
    print("Done!\n")


def example_sequence():
    """Example: Complex movement sequence"""
    print("Example 5: Movement Sequence")
    print("-" * 40)
    
    print("Executing greeting sequence...")
    
    # Greeting sequence
    rp.set_display_expression(1)      # Happy face
    rp.set_rgb_light(0, 255, 0)       # Green light
    rp.move_forward(0.5, 0.3)         # Small forward movement
    rp.rotate(45, 0.3)                 # Wave right
    rp.rotate(-45, 0.3)               # Wave left
    rp.rotate(0, 0.3)                 # Return to center
    rp.stop()
    
    print("Done!\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Rider-Pi MCP - Basic Usage Examples")
    print("=" * 50)
    print()
    
    # Note: These examples require actual Rider-Pi hardware
    # Uncomment the examples you want to run:
    
    # example_basic_movement()
    # example_sensor_reading()
    # example_display_control()
    # example_conditional_behavior()
    # example_sequence()
    
    print("Note: Uncomment examples in the code to run them.")
    print("Make sure your Rider-Pi is connected and configured correctly.")

