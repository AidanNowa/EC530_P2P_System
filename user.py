import socket
import threading
import sys
import json

PORT = 65432

def register_user(username):
    #username = input("Please enter your username: ")
    if user_exists(username):
        print(f"\n  Welcome back, {username}!\n")
    else:
        choice = input("Username does not exist. Do you want to register? (yes/no): ")
        if choice.lower() == 'yes':
            ip_address = socket.gethostbyname(socket.gethostname())
            try:
                with open('user_registry.json', 'r+') as file:
                    users = json.load(file)
            except(FileNotFoundError, json.JSONDecodeError):
                users = {}

            users[username] = ip_address

            with open('user_registry.json', 'w') as file:
                json.dump(users, file)

            print(f"\n  User {username} registered with IP {ip_address}\n")
        else:
            print("Registration cancelled. Exiting...")
            sys.exit(0)


def user_exists(username):
    try:
        with open('user_registry.json', 'r') as file:
            users = json.load(file)
            if username in users:
                return True
    except(FileNotFoundError, json.JSONDecodeError):
        pass
    return False


def lookup_user(username):
    try:
        with open('user_registry.json', 'r') as file:
            users = json.load(file)
            return users.get(username)
    except(FileNotFoundError, json.JSONDecodeError):
        return None
    

def handle_incoming_messages(conn):
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                #print("Peer disconnected.")
                raise ConnectionResetError
                #break
            print(f"Peer says: {data.decode()}")
        except ConnectionResetError:
            print("\nPeer disconnected. Press Enter to continue...")
            break

def send_messages(conn, target_username):
    while True:
        full_message = input()
        if full_message == "/quit":
            print("Quitting...")
            conn.close() #close connection gracefully
            sys.exit(0) #exit the program
        target_username, message = full_message.split(':', 1) #assume simple format for demo
        target_ip = lookup_user(target_username)
        if target_ip:
            conn.sendall(message.encode())
        else:
            queue_message(target_username, message)
            print(f"Message queued for {target_username} as they are offline.")


def queue_message(recipient, message):
    try:
        with open('message_queue.json', 'r+') as file:
            messages = json.load(file)
    except(FileNotFoundError, json.JSONDecodeError):
        messages = {}
    if recipient not in messages:
        messages[recipient] = []

    message[recipient].append(message)

    with open('message_queue.json', 'w') as file:
        json.dump(messages, file)
        

def serve_peer(bind_host, bind_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((bind_host, bind_port))
        server_socket.listen()
        print(f"Listening as {bind_host}:{bind_port}...")
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")

        #start thread for handling incoming messages
        threading.Thread(target=handle_incoming_messages, args=(conn,), daemon=True).start()

        #main thread is used for sending messages
        send_messages(conn)

def connect_to_peer(username):
    target_ip = lookup_user(username)
    if not target_ip:
        print(f"User {username} not found.")
        return
    target_port = PORT #assume port is fixed for simplicity

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((target_ip, target_port))
            print(f"Connect to {target_ip}:{target_port}")
            
            #start thread for handling incoming messages
            threading.Thread(target=handle_incoming_messages, args=(client_socket,), daemon=True).start()

            #main thread is used for sending messages
            send_messages(client_socket)

        except ConnectionRefusedError:
            print("Connection to {username} failed. They might be offline.")
            #serve_peer(target_ip, target_port)

def authenticate_user():
    print("\n   Welcome to the P2P Chat System")
    print("1. Login")
    print("2. Register")
    print("3. Exit")
    choice = input("Enter your choice (1-3): ")

    if choice == "1" or choice == "2":
        username = input("Enter your username: ")
        if register_user(username):
            return username
    elif choice == "3":
        print("\nExiting...\n")
        sys.exit(0)
    else:
        print("Invalid choice. Please enter a number between 1-3.")



def main_menu(username):
    while True:
        print("    Main Menu")
        print("1. Chat with a user")
        print("2. Manage contacts")
        print("3. Log out")
        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            chat_username = input("Enter the username you want to chat with: ")
            if chat_username:
                connect_to_peer(chat_username)
            else:
                print("Invalid username.")
        elif choice == "2":
            #TODO: manage contacts
            print("\nContact managaement feature coming soon.\n")
        elif choice == "3":
            print("\nLogging out...\n")
            break #break out of loop
        else:
            print("Invalid choice. Please enter a number between 1-3.")

if __name__ == "__main__":
    user = authenticate_user() #user must log in or register first
    main_menu(user) # access to the main menu after successful login
