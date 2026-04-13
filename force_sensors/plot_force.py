import serial
import matplotlib.pyplot as plt
from collections import deque

ser = serial.Serial('/dev/ttyACM0', 115200)

left_data = deque(maxlen=100)
right_data = deque(maxlen=100)

plt.ion()

while True:
    line = ser.readline().decode().strip()

    try:
        left, right = line.split(",")

        left = int(left)
        right = int(right)

        left_data.append(left)
        right_data.append(right)

        plt.clf()
        plt.plot(left_data, label="Left foot")
        plt.plot(right_data, label="Right foot")
        plt.legend()
        plt.pause(0.01)

    except:
        pass