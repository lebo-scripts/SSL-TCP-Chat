import threading
import socket
import ssl
import logging

HOST = "127.0.0.1"
PORT = 55555
BUFFER_SIZE = 1024
MAX_NICKNAME_LENGTH = 15
MAX_MESSAGE_LENGTH = 512

CERTFILE = 'server.crt'
KEYFILE = 'server.key'

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Server Setup 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# SSL setup
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)

ssl_server_socket = ssl_context.wrap_socket(server, server_side=True)

ssl_server_socket.bind((HOST, PORT))
ssl_server_socket.listen()

# Dictionary to store connected clients: {nickname: ssl_socket_object}
connected_clients = {}
client_lock = threading.Lock() # To protect connected_clients dictionary

def broad_cast(message, sender_nickname=None):
    """
    Sends a message to all connected clients.

    Args:
        message (bytes): The message to be broadcast.
        sender_nickname (str, optional): The nickname of the sender. If provided, the message will not be sent back to the sender.
    """
    with client_lock:
        for nickname, client_socket in connected_clients.items():
            if sender_nickname and nickname == sender_nickname:
                continue 
            try:
                client_socket.send(message)
            except ssl.SSLError as e:
                logging.error(f"SSL Error sending to {nickname}: {e}")
            except Exception as e:
                logging.error(f"Error sending message to {nickname}: {e}")
        

def remove_client(nickname, client_socket):
    """
    Removes a client from the connected clients list and closes their socket.
    Broadcasts a message to other clients about the disconnection.

    Args:
        nickname (str): The nickname of the client to remove.
        client_socket (ssl.SSLSocket): The SSL socket object of the client to remove.
    """
    with client_lock:
        if nickname in connected_clients:
            del connected_clients[nickname]
            client_socket.close()
            logging.info(f"Client {nickname} removed and socket closed.")
    
    broad_cast(f'{nickname} left the chat.'.encode('ascii'))

def handle(client_ssl_socket, nickname):
    """
    Handles incoming messages from a single client.
    Receives messages, checks for length, and broadcasts them to other clients.
    Manages client disconnection.

    Args:
        client_ssl_socket (ssl.SSLSocket): The SSL socket object for the connected client.
        nickname (str): The nickname of the connected client.
    """
    logging.info(f"Handling connection for {nickname}.")
    while True:
        try:
            message = client_ssl_socket.recv(BUFFER_SIZE)
            if not message: 
                logging.info(f"Client {nickname} disconnected gracefully.")
                break
            
            if len(message) > MAX_MESSAGE_LENGTH:
                client_ssl_socket.send("Message too long. Max 512 bytes.".encode('ascii'))
                continue

            broad_cast(message, sender_nickname=nickname)
        except (ConnectionResetError, BrokenPipeError, ssl.SSLError) as e:
            logging.warning(f"Connection error with {nickname}: {e}")
            break #
        except Exception as e:
            logging.error(f"Unexpected error in handle for {nickname}: {e}")
            break 
    
    remove_client(nickname, client_ssl_socket)

def receive():
    """
    Continuously listens for new client connections, handles nickname registration,
    and starts a new thread for each connected client to handle their messages.
    Manages SSL handshake and initial client setup.
    """
    logging.info('Server is listening...')
    while True:
        try:
            client_socket, address = ssl_server_socket.accept() 
            logging.info(f"Connected with address: {address}.")

            client_socket.send('Nick'.encode('ascii'))
            
            nickname = client_socket.recv(BUFFER_SIZE).decode('ascii')
            
            if not nickname or len(nickname) > MAX_NICKNAME_LENGTH:
                client_socket.send("Nickname invalid or too long. Max 15 chars.".encode('ascii'))
                client_socket.close()
                logging.warning(f"Rejected connection from {address} due to invalid nickname: '{nickname}'")
                continue

            with client_lock:
                if nickname in connected_clients:
                    client_socket.send("Nickname already taken. Please choose another.".encode('ascii'))
                    client_socket.close()
                    logging.warning(f"Rejected connection from {address} due to duplicate nickname: '{nickname}'")
                    continue
                connected_clients[nickname] = client_socket

            logging.info(f'Client nickname is: {nickname}.')
            broad_cast(f'{nickname} joined the chat.'.encode('ascii'))
            client_socket.send('Connected to server.'.encode('ascii'))

            thread = threading.Thread(target=handle, args=(client_socket, nickname))
            thread.start()

        except ssl.SSLError as e:
            logging.error(f"SSL Handshake failed: {e}")
        except Exception as e:
            logging.error(f"Error accepting new connection: {e}")

if __name__ == "__main__":
    receive()
