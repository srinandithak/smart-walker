import socket
import matplotlib.pyplot as plt
from collections import deque
import sys

JETSON_IP = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.100"
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((JETSON_IP, PORT))
print(f"Connected to {JETSON_IP}:{PORT}")

buf = ""
left_data = deque(maxlen=100)
right_data = deque(maxlen=100)

plt.ion()

while True:
    chunk = sock.recv(1024).decode()
    if not chunk:
        break
    buf += chunk
    while "\n" in buf:
        line, buf = buf.split("\n", 1)
        try:
            left, right = line.strip().split(",")
            left_data.append(int(left))
            right_data.append(int(right))

            plt.clf()
            plt.plot(left_data, label="Left foot")
            plt.plot(right_data, label="Right foot")
            plt.legend()
            plt.pause(0.01)
        except:
            pass
