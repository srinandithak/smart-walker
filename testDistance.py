# # -*- coding: utf-8 -*-
# """
# Test the Modulino Distance sensor.
# Run this to verify the sensor works before using it with the vision system.
# """
# from vl53l4cd_smbus import VL53L4CD
# import time

# print("Connecting to VL53L4CD sensor...")
# sensor = VL53L4CD(bus=1, address=0x29)
# print("Sensor initialized!")
# print("Move your hand in front of it. Press Ctrl+C to stop.")
# print("-" * 40)

# sensor.start_ranging()

# try:
#     while True:
#         if sensor.data_ready():
#             dist_mm = sensor.get_distance()
#             sensor.clear_interrupt()
#             dist_ft = dist_mm / 304.8
#             print(f"Distance: {dist_mm} mm  ({dist_ft:.1f} ft)")
#         time.sleep(0.05)
# except KeyboardInterrupt:
#     print("\nStopped.")
# finally:
#     sensor.close()

# -*- coding: utf-8 -*-
"""
Test the Modulino Distance sensor.
Run with: sudo python3 testDistance.py
"""
from vl53l4cd_smbus import VL53L4CD
import time

print("Connecting to VL53L4CD sensor...")
print("=" * 40)

try:
    sensor = VL53L4CD(bus=1, address=0x29)
except Exception as e:
    print(f"\nFailed on bus 1: {e}")
    print("Trying bus 0...")
    try:
        sensor = VL53L4CD(bus=0, address=0x29)
    except Exception as e2:
        print(f"Failed on bus 0 too: {e2}")
        print("\nCheck your wiring and run: sudo i2cdetect -r -y 1")
        exit(1)

print("=" * 40)
print("Starting distance readings...")
print("Move your hand in front of sensor. Ctrl+C to stop.")
print("-" * 40)

sensor.start_ranging()

try:
    no_data_count = 0
    while True:
        if sensor.data_ready():
            dist_mm = sensor.get_distance()
            sensor.clear_interrupt()
            dist_ft = dist_mm / 304.8
            print(f"Distance: {dist_mm} mm  ({dist_ft:.1f} ft)")
            no_data_count = 0
        else:
            no_data_count += 1
            if no_data_count > 100:
                print("No data for 5 seconds, sensor may not be working")
                no_data_count = 0
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    sensor.close()