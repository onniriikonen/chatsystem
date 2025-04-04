import socket
import threading

HOST = '0.0.0.0'
PORT = 8000

users = {}
channels = {"#general": set()}
lock = threading.Lock()

def channelMessage(message, nickname, channel):
    with lock:
        if channel not in channels:
            return
        for client in channels[channel]:
            if client != nickname:
                users[client].sendall(f"[{channel}] {nickname}: {message}".encode())
    return None

def privateMessage(sender, recipient, message):
    if recipient in users:
        users[recipient].sendall(f"[Private Message from {sender}]: {message}".encode())
    return None

def handle(conn, addr):
    conn.sendall(b"Enter nickname: ")
    name = conn.recv(1024).decode().strip()
    with lock:
        users[name] = conn
        channels["#general"].add(name)

    conn.sendall(b"Connected. Type /help for commands.\n")

    while True:
        data = conn.recv(1024)
        if not data:
            break

        msg = data.decode().strip()

        if msg.startswith("/join"):
            _, chan = msg.split()
            with lock:
                if chan not in channels:
                    channels[chan] = set()
                for ch in channels.values():
                    ch.discard(name)
                channels[chan].add(name)
            conn.sendall(f"Joined {chan}\n".encode())

        elif msg.startswith("/pm"):
            parts = msg.split(' ', 2)
            if len(parts) >= 3:
                _, target, pm = parts
                privateMessage(name, target, pm)

        elif msg == "/exit":
            break

        elif msg == "/help":
            help_text = "/join #channel - join a channel\n/pm user msg - private message\n/exit - quit\n"
            conn.sendall(help_text.encode())

        else:
            chan = next((ch for ch in channels if name in channels[ch]), "#general")
            channelMessage(msg, name, chan)

    with lock:
        del users[name]
        for ch in channels.values():
            ch.discard(name)
    conn.close()
    print(f"{name} disconnected")


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
print(f"Server listening on {HOST}:{PORT}")

while True:
    conn, addr = s.accept()
    threading.Thread(target=handle, args=(conn, addr), daemon=True).start()


s.close()
