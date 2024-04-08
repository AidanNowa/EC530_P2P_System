
import socket
import threading

def handle_incoming_messages(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            print("Peer disconnected.")
            break
        print(f"Peer says: {data.decode()}")

def send_messages(conn):
    while True:
        message = input()
        conn.sendall(message.encode())

def serve_peer(bind_host, bind_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((bind_host, bind_port))
        server_socket.listen()
        print(f"Listening as {bind_host}:{bind_port}...")
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")

        # Start thread for handling incoming messages
        threading.Thread(target=handle_incoming_messages, args=(conn,), daemon=True).start()

        # Main thread is used for sending messages
        send_messages(conn)

def connect_to_peer(target_host, target_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((target_host, target_port))
            print(f"Connected to {target_host}:{target_port}")

            # Start thread for handling incoming messages
            threading.Thread(target=handle_incoming_messages, args=(client_socket,), daemon=True).start()

            # Main thread is used for sending messages
            send_messages(client_socket)
        except ConnectionRefusedError:
            print("Connection failed. Listening as a server...")
            serve_peer(target_host, target_port)

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 65432
    connect_to_peer(HOST, PORT)
