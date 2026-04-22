import serial
import csv
import time
import socket
import threading

ser = serial.Serial('/dev/ttyACM0', 115200)

clients = []
clients_lock = threading.Lock()

def handle_client(conn):
    with clients_lock:
        clients.append(conn)
    try:
        while True:
            if conn.recv(1) == b'':
                break
    except:
        pass
    finally:
        with clients_lock:
            clients.remove(conn)
        conn.close()

def start_server(port=5005):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print(f"Broadcasting on port {port}")
    while True:
        conn, addr = server.accept()
        print(f"Client connected: {addr}")
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

threading.Thread(target=start_server, daemon=True).start()

with open("data.csv", "a", newline="") as file:
    writer = csv.writer(file)

    while True:
        line = ser.readline().decode().strip()

        if line:
            try:
                left, right = line.split(",")
                writer.writerow([time.time(), left, right])
                print("Left:", left, "Right:", right)

                msg = (line + "\n").encode()
                with clients_lock:
                    for conn in list(clients):
                        try:
                            conn.sendall(msg)
                        except:
                            clients.remove(conn)
            except:
                pass
