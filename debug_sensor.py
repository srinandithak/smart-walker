# -*- coding: utf-8 -*-
"""
Debug script to find the correct data_ready register.
Run with: sudo python3 debug_sensor.py
"""
import smbus2
import time

bus = smbus2.SMBus(1)
addr = 0x29

def write8(reg, val):
    data = [(reg >> 8) & 0xFF, reg & 0xFF, val & 0xFF]
    msg = smbus2.i2c_msg.write(addr, data)
    bus.i2c_rdwr(msg)

def read8(reg):
    w = smbus2.i2c_msg.write(addr, [(reg >> 8) & 0xFF, reg & 0xFF])
    r = smbus2.i2c_msg.read(addr, 1)
    bus.i2c_rdwr(w, r)
    return list(r)[0]

def read16(reg):
    w = smbus2.i2c_msg.write(addr, [(reg >> 8) & 0xFF, reg & 0xFF])
    r = smbus2.i2c_msg.read(addr, 2)
    bus.i2c_rdwr(w, r)
    result = list(r)
    return (result[0] << 8) | result[1]

print("=== SENSOR DEBUG ===")
print(f"Model ID: 0x{read16(0x010F):04X}")
print(f"Boot status: 0x{read8(0x00E5):02X}")
print()

# Clear interrupt and start ranging
print("Starting ranging...")
write8(0x0086, 0x01)
write8(0x0087, 0x40)

print("Waiting 2 seconds for measurements...")
time.sleep(2)

print()
print("=== CHECKING ALL POSSIBLE READY REGISTERS ===")
for reg in [0x0030, 0x0031, 0x0034, 0x0089, 0x0090, 0x0091]:
    val = read8(reg)
    print(f"  Register 0x{reg:04X} = 0x{val:02X} ({val})")

print()
print("=== TRYING TO READ DISTANCE ANYWAY ===")
for i in range(10):
    dist = read16(0x0096)
    status = read8(0x0089)
    gpio = read8(0x0031)
    print(f"  Read {i+1}: distance={dist}mm  status=0x{status:02X}  gpio=0x{gpio:02X}")

    # Try clearing interrupt between reads
    write8(0x0086, 0x01)
    time.sleep(0.2)

print()
print("=== TRYING SINGLE-SHOT MODE ===")
write8(0x0087, 0x00)  # stop
time.sleep(0.1)
write8(0x0086, 0x01)  # clear
write8(0x0087, 0x10)  # single shot instead of 0x40
time.sleep(1)

for reg in [0x0030, 0x0031, 0x0089]:
    val = read8(reg)
    print(f"  Register 0x{reg:04X} = 0x{val:02X}")

dist = read16(0x0096)
print(f"  Distance: {dist}mm")

# Stop
write8(0x0087, 0x00)
bus.close()
print("\nDone. Share this output!")