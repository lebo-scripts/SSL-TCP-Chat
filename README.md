# Secure Chat Application

This is a simple, secure chat application built with Python, featuring SSL/TLS encryption for communication between the server and clients.

## Features

- **Secure Communication**: All messages are encrypted using SSL/TLS, ensuring privacy and data integrity.
- **Multi-client Support**: The server can handle multiple clients concurrently.
- **Nickname-based Chat**: Users join the chat with a unique nickname.
- **Basic Messaging**: Send and receive text messages in real-time.

## How to Run

### Prerequisites

- Python 3.x installed.
- OpenSSL for generating SSL certificates (usually pre-installed on Linux/macOS).

### 1. Generate SSL Certificates

Before running the server, you need to generate a self-signed SSL certificate and key.

```bash
openssl req -newkey rsa:2048 -nodes -keyout server.key -x509 -days 365 -out server.crt
```

When prompted, you can enter any information, but ensure the "Common Name (e.g. server FQDN or YOUR name)" matches the `HOST` variable in `chat.py` (which is `127.0.0.1` by default).

### 2. Start the Server

Navigate to the directory containing `chat.py` and run:

```bash
python chat.py
```

The server will start listening for incoming connections on `127.0.0.1:55555`.

### 3. Start a Client

Open a new terminal, navigate to the directory containing `client.py`, and run:

```bash
python client.py
```

You will be prompted to enter a nickname. Once connected, you can start sending and receiving messages. Open multiple client instances to chat with yourself or others!