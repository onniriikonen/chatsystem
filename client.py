import socket
import threading

HOST = input("Enter server IP: ")
PORT = 8000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def receive_messages():
    while True:
        data = s.recv(1024)
        if not data:
            break
        print(data.decode())

thread = threading.Thread(target=receive_messages, daemon=True)
thread.start()

while True:
    msg = input()
    if msg:
        s.sendall(msg.encode())
    if msg == "/exit":
        break

s.close()
print("Disconnected")
