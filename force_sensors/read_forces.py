import serial
import csv
import time

ser = serial.Serial('/dev/ttyACM0', 115200)

with open("data.csv", "a", newline="") as file:
    writer = csv.writer(file)

    while True:
        line = ser.readline().decode().strip()

        if line:
            try:
                left, right = line.split(",")

                writer.writerow([time.time(), left, right])

                print("Left:", left, "Right:", right)

            except:
                pass