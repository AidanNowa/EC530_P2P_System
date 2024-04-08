import socket
import threading
from threading import Lock
import socket
import sys
import json
import queue

CHAT_REQUEST_PREFIX = "CHAT_REQUEST:"
#app_state_lock = Lock()
app_state = "idle" #possible states: idle, awaiting_approval, in_chat
PORT = 65432

def register_user(username):
    #username = input("Please enter your username: ")
    if user_exists(username):
        print(f"\n  Welcome back, {username}!\n")
    else:
        choice = input("Username does not exist. Do you want to register? (yes/no): ")
        if choice.lower() == 'yes':
            ip_address = socket.gethostbyname(socket.gethostname())
            #ip_address = '127.0.0.1'
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

def send_messages(conn):
    print("\n   You can now start chatting! Type '/quit' to exit.")
    while True:
        try:
            message = input()
            if message == "/quit":
                print("Quitting chat session...")
                conn.close()
                break
            conn.sendall(message.encode())
        
        except ConnectionResetError:
            print("Connection was lost.")
            conn.close()
            break


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
        

def serve_peer(bind_host, bind_port, username):
    global app_state
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        #setup server socket 
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((bind_host, bind_port))
        server_socket.listen()
        print(f"\n{username} listening for chat requests as {bind_host}:{bind_port}...\n")

        while True:
            conn, addr = server_socket.accept()
            #read the initial mesage to determine if it is a chat request
            initial_message = conn.recv(1024).decode()
            if initial_message.startswith(CHAT_REQUEST_PREFIX):
                requester_username = initial_message[len(CHAT_REQUEST_PREFIX):]
                print(f"\nIncoming chat request for {requester_username} at {addr[0]}\n")
                if app_state == "idle":
                    approve = input("Do you want to accept the chat? (yes/no): ")
                    if approve.lower() == 'yes':
                        app_state = "in_chat"
                        print(f"\nChat session started with {requester_username}")
                        threading.Thread(target=handle_incoming_messages, args=(conn,), daemon=True).start()
                        send_messages(conn)
                        app_state = "idle" #rest state after chat ends
                    else:
                        print("Chat request declined.")
                        conn.close()
                else:
                    print("Currently busy. Declining chat request.")
                    conn.close()

            else:
                #TODO: Handle other types of messages or unrecognized requests
                conn.close()

            '''

            print(f"\nIncoming conncection request from {addr}")

            #check current app state before proceeding
            if app_state != "idle":
                #if not in idle state, do not accept new connections
                conn.close()
                continue
            
            #handle incoming chat request
            print(f"\nIncoming chat request from {addr[0]}")
            approve = input(f"\nDo you want to accept the chat from {addr[0]}? (yes/no)")
            
            if approve.lower() == 'yes':
                app_state = "in_chat"
                print(f"\nChat session started with {addr[0]}\n")
            
                #start new thread for handling incoming messages
                threading.Thread(target=handle_incoming_messages, args=(conn,), daemon=True).start()
                    #enter chat session to send message
                send_messages(conn) #holds here until '/quit'
                app_state = "idle"
            
            else:
                print("\Chat request declined.\n")
                conn.close()
                #app_state = "idle" #reset to default
            '''

def connect_to_peer(username):
    global app_state
    target_ip = lookup_user(username)
    if not target_ip:
        print(f"User {username} not found.")
        return
    target_port = PORT #assume port is fixed for simplicity      

    try:
        print(f"\nSending chat request to {username} at IP: {target_ip}...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp_socket:
            temp_socket.connect((target_ip, target_port))
            chat_request_message = f"{CHAT_REQUEST_PREFIX}{username}"
            temp_socket.sendall(chat_request_message.encode())

        #after sending the chat request, start listening for the receiver's reponse
        print(f"\nWaiting for {username} to accept the chat request...")
        serve_peer('0.0.0.0', PORT, username)
    except ConnectionRefusedError:
        print(f"\nConnection to {username} failed. They may be offline.\n")


    '''
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"\nAttempting to connect to {username} at IP: {target_ip} at PORT: {target_port}...\n")
        
        client_socket.connect((target_ip, target_port))
        print(f"\nAttempting to connect to {username} at IP: {target_ip} on PORT: {target_port}...\n")
        #assume connection is accpeted for simplicity TODO:add check
        print(f"Connected to {username} at {target_ip}:{target_port}")
        handle_incoming_messages(client_socket) #handle incoming messages

    except ConnectionRefusedError:
        print(f"\nConnection to {username} failed. They might be offline.\n")
        return None
    '''

        
def authenticate_user():
    print("\n   Welcome to the P2P Chat System")
    print("1. Login")
    print("2. Register")
    print("3. Exit")
    choice = input("Enter your choice (1-3): ")

    if choice == "1" or choice == "2":
        username = input("Enter your username: ")
        if choice == '1':
            if user_exists(username):
                print(f"\n  Welcome back, {username}!\n")
                return True, username
            else:
                print("\nUser does not exist.\n")
                return False, None #user doe not exist, auth fails
        elif choice =="2":
            register_user(username)
            return True, username
    elif choice == "3":
        print("\nExiting...\n")
        sys.exit(0)
    else:
        print("Invalid choice. Please enter a number between 1-3.")

    return False, None


def start_server(port):
    server_thread = threading.Thread(target=serve_peer, args=('0.0.0.0', port), daemon=True)
    server_thread.start()


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
                conn = connect_to_peer(chat_username)
                if conn:
                    send_messages(conn) #used the established connection for messages
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

    authenticated, user = authenticate_user() #user must log in or register first
    if authenticated:
        #start listening for incoming connections and chat requests
        server_thread = threading.Thread(target=serve_peer, args=('0.0.0.0', PORT, user), daemon=True)
        server_thread.start()
        #start_server(PORT) #start listening for incoming connections
        main_menu(user) # access to the main menu after successful login


