# -*- coding: utf-8 -*-
"""
Test the Modulino Distance sensor.
Run this to verify the sensor works before using it with the vision system.
"""
from vl53l4cd_smbus import VL53L4CD
import time

print("Connecting to VL53L4CD sensor...")
sensor = VL53L4CD(bus=1, address=0x29)
print("Sensor initialized!")
print("Move your hand in front of it. Press Ctrl+C to stop.")
print("-" * 40)

sensor.start_ranging()

try:
    while True:
        if sensor.data_ready():
            dist_mm = sensor.get_distance()
            sensor.clear_interrupt()
            dist_ft = dist_mm / 304.8
            print(f"Distance: {dist_mm} mm  ({dist_ft:.1f} ft)")
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    sensor.close()