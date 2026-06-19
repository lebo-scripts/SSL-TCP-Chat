import socket
import threading
import ssl
import sys

nickname = ""
client_ssl_socket = None

def connect_to_server():
    """
    Establishes an SSL-encrypted connection to the chat server.
    Prompts the user for a nickname and starts separate threads for receiving and sending messages.
    """
    global nickname, client_ssl_socket
    nickname = input("What is your nickname: ")

    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(('127.0.0.1',55555))

    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE 

    try:
        client_ssl_socket = ssl_context.wrap_socket(client, server_hostname='127.0.0.1')
    except ssl.SSLError as e:
        print(f"SSL connection failed: {e}")
        sys.exit(1)
    
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()

def receive():
    """
    Continuously receives messages from the server.
    Handles special 'Nick' requests from the server and prints incoming chat messages.
    Manages disconnections and unexpected errors.
    """
    while True:
        try:
            message = client_ssl_socket.recv(1024).decode('ascii')
            if message == 'Nick':
                client_ssl_socket.send(nickname.encode('ascii'))
            else:
                print(message)
        except (ConnectionResetError, BrokenPipeError, ssl.SSLError) as e:
            print(f'Disconnected from server: {e}')
            client_ssl_socket.close()
            sys.exit(1) 
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            client_ssl_socket.close()
            sys.exit(1) 
            break

def write():
    """
    Continuously prompts the user for input and sends messages to the server.
    Prepends the user's nickname to the message and enforces a maximum message length.
    """
    while True:
        
        user_input = input("")
        message = f'{nickname}: {user_input}'
        
        if len(message.encode('ascii')) > 512: 
            print("Your message is too long. Please keep it under 512 characters.")
            continue
        client_ssl_socket.send(message.encode('ascii'))

if __name__ == "__main__":
    connect_to_server()
