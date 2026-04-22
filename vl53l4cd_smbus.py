# -*- coding: utf-8 -*-
"""
VL53L4CD Time-of-Flight sensor driver using smbus2.
No Adafruit/Blinka dependencies. Works directly on Jetson Nano.
Based on ST Ultra Lite Driver register map.
"""
import smbus2
import time

# Default configuration written to register 0x002D (from ST ULD)
_DEFAULT_CONFIG = [
    0x12, 0x00, 0x00, 0x40, 0x00, 0x00, 0x10, 0x06,
    0x10, 0x06, 0x01, 0x06, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
    0x0F, 0x0D, 0x0E, 0x0E, 0x00, 0x00, 0x02, 0xC7,
    0xFF, 0x9B, 0x00, 0x00, 0x00, 0x01, 0x01, 0x40,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x50,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x07,
    0x05, 0x06, 0x06, 0x01, 0x00, 0x00, 0x00, 0x00,
]


class VL53L4CD:
    """Minimal VL53L4CD driver using smbus2."""

    def __init__(self, bus=1, address=0x29):
        self.address = address
        self.bus = smbus2.SMBus(bus)
        self._init_sensor()

    # ----------------------------------------------------------
    # Low-level I2C helpers (VL53L4CD uses 16-bit register addresses)
    # ----------------------------------------------------------
    def _write8(self, reg, val):
        """Write 1 byte to a 16-bit register address."""
        data = [(reg >> 8) & 0xFF, reg & 0xFF, val & 0xFF]
        msg = smbus2.i2c_msg.write(self.address, data)
        self.bus.i2c_rdwr(msg)

    def _write16(self, reg, val):
        """Write 2 bytes (big-endian) to a 16-bit register address."""
        data = [
            (reg >> 8) & 0xFF, reg & 0xFF,
            (val >> 8) & 0xFF, val & 0xFF,
        ]
        msg = smbus2.i2c_msg.write(self.address, data)
        self.bus.i2c_rdwr(msg)

    def _write32(self, reg, val):
        """Write 4 bytes (big-endian) to a 16-bit register address."""
        data = [
            (reg >> 8) & 0xFF, reg & 0xFF,
            (val >> 24) & 0xFF, (val >> 16) & 0xFF,
            (val >> 8) & 0xFF, val & 0xFF,
        ]
        msg = smbus2.i2c_msg.write(self.address, data)
        self.bus.i2c_rdwr(msg)

    def _write_block(self, reg, data):
        """Write a block of bytes starting at a 16-bit register address.
        Splits into 30-byte chunks to stay within I2C buffer limits."""
        offset = 0
        while offset < len(data):
            chunk = data[offset:offset + 30]
            r = reg + offset
            msg_data = [(r >> 8) & 0xFF, r & 0xFF] + list(chunk)
            msg = smbus2.i2c_msg.write(self.address, msg_data)
            self.bus.i2c_rdwr(msg)
            offset += 30

    def _read8(self, reg):
        """Read 1 byte from a 16-bit register address."""
        write = smbus2.i2c_msg.write(self.address, [(reg >> 8) & 0xFF, reg & 0xFF])
        read = smbus2.i2c_msg.read(self.address, 1)
        self.bus.i2c_rdwr(write, read)
        return list(read)[0]

    def _read16(self, reg):
        """Read 2 bytes (big-endian) from a 16-bit register address."""
        write = smbus2.i2c_msg.write(self.address, [(reg >> 8) & 0xFF, reg & 0xFF])
        read = smbus2.i2c_msg.read(self.address, 2)
        self.bus.i2c_rdwr(write, read)
        result = list(read)
        return (result[0] << 8) | result[1]

    # ----------------------------------------------------------
    # Sensor initialization
    # ----------------------------------------------------------
    def _init_sensor(self):
        """Full initialization sequence for the VL53L4CD."""
        # Wait for the sensor to boot (poll firmware status)
        timeout = time.time() + 3.0
        while self._read8(0x00E5) == 0x00:
            if time.time() > timeout:
                raise RuntimeError("VL53L4CD did not boot (timeout on 0x00E5)")
            time.sleep(0.01)

        # Write default configuration starting at register 0x002D
        self._write_block(0x002D, _DEFAULT_CONFIG)

        # Set inter-measurement period to 0 (continuous)
        self._write32(0x006C, 0)

        # Set timing budget to 50ms
        self._set_timing_budget(50)

        # Run a calibration ranging
        # self.start_ranging()
        # timeout = time.time() + 3.0
        # while not self.data_ready():
        #     if time.time() > timeout:
        #         raise RuntimeError("VL53L4CD calibration timeout")
        #     time.sleep(0.01)
        # Run a calibration ranging
        time.sleep(0.5)
        self.start_ranging()
        time.sleep(0.1)
        timeout = time.time() + 10.0
        while not self.data_ready():
            if time.time() > timeout:
                raise RuntimeError("VL53L4CD calibration timeout")
            time.sleep(0.05)
        self.clear_interrupt()
        self.stop_ranging()

        # Finalize VHV config
        self._write8(0x0022, 0x00)
        self._write8(0x0025, 0x00)

    def _set_timing_budget(self, budget_ms):
        """Set the timing budget in milliseconds (10-200)."""
        osc_freq = self._read16(0x0006)
        if osc_freq == 0:
            # Sensor not calibrated yet, use a default
            osc_freq = 1024
        macro_period_us = (2304 * (0x40000000 // osc_freq)) >> 6
        val_a = ((budget_ms * 16 * macro_period_us) + 500) // 1000 - 1
        self._write32(0x005E, val_a)
        val_b = ((budget_ms * 16 * macro_period_us * 12 // 10) + 500) // 1000 - 1
        self._write32(0x0060, val_b)

    # ----------------------------------------------------------
    # Ranging operations
    # ----------------------------------------------------------
    def start_ranging(self):
        """Start continuous ranging."""
        # Clear any pending interrupt first
        system_status = self._read8(0x0089)
        if system_status & 0x01:
            self.clear_interrupt()
        self._write8(0x0087, 0x40)

    def stop_ranging(self):
        """Stop ranging."""
        self._write8(0x0087, 0x00)

    def data_ready(self):
        """Check if new distance data is available."""
        return (self._read8(0x0089) & 0x01) == 0x01

    def clear_interrupt(self):
        """Clear the data-ready interrupt."""
        self._write8(0x0086, 0x01)

    def get_distance(self):
        """Read the distance in millimeters."""
        return self._read16(0x0096)

    def close(self):
        """Stop ranging and close the I2C bus."""
        try:
            self.stop_ranging()
        except Exception:
            pass
        self.bus.close()