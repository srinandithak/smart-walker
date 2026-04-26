import serial
import time

ser = serial.Serial('COM5', 115200, timeout=1)
time.sleep(3)

print("Listening for 10 seconds...")
for i in range(100):
    if ser.in_waiting:
        line = ser.readline().decode(errors='ignore').strip()
        print(f"Got: {line}")
    else:
        if i % 20 == 0:
            print("(nothing yet...)")
    time.sleep(0.1)

ser.close()