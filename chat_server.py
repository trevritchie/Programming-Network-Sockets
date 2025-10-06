"""
chat_server.py - Multi-client TCP Chat Server

This server listens for incoming TCP connections and handles multiple clients
simultaneously using threads. It broadcasts messages from one client to all
other connected clients with timestamps and usernames.
"""

import socket
import threading
from datetime import datetime

# Server configuration
HOST = '127.0.0.1'  # Localhost - server will run on local machine
PORT = 5555         # Port to listen on (non-privileged ports are > 1023)

# Global list to keep track of all connected clients
# Each element will be a tuple: (connection_socket, username)
clients = []

# Lock for thread-safe operations on the clients list
clients_lock = threading.Lock()


def broadcast(message, sender_conn=None):
    """
    Broadcast a message to all connected clients except the sender.

    Args:
        message (str): The message to broadcast
        sender_conn (socket): The connection socket of the sender (to exclude them)
    """
    with clients_lock:
        # Iterate through all connected clients
        for client_conn, username in clients:
            # Don't send the message back to the sender
            if client_conn != sender_conn:
                try:
                    # Send the message (encode to bytes) with newline delimiter
                    # Use sendall() to ensure all data is sent
                    client_conn.sendall((message + '\n').encode('utf-8'))
                except (BrokenPipeError, ConnectionResetError, OSError):
                    # If sending fails, the client likely disconnected
                    # We'll handle cleanup in the client handler
                    pass


def get_timestamp():
    """
    Get current timestamp in a readable format.

    Returns:
        str: Formatted timestamp [HH:MM:SS]
    """
    return datetime.now().strftime('[%H:%M:%S]')


def handle_client(client_socket, client_address):
    """
    Handle communication with a single client in a separate thread.

    Args:
        client_socket (socket): The socket connection to the client
        client_address (tuple): The (IP, port) of the client
    """
    username = None

    try:
        # First, receive the username from the client
        # Use sendall() to ensure the prompt is sent completely
        client_socket.sendall("Please enter your username: ".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8').strip()

        # Validate username
        if not username:
            username = f"Guest_{client_address[1]}"  # Use port number if no username

        # Add the client to our list of connected clients
        with clients_lock:
            clients.append((client_socket, username))

        # Notify all other clients that this user has joined
        join_message = f"{get_timestamp()} {username} has joined the chat!\n"
        print(f"[SERVER] {username} connected from {client_address}")
        broadcast(join_message, client_socket)

        # Send welcome message to the new client
        welcome_message = f"{get_timestamp()} Welcome to the chat, {username}!\n"
        client_socket.sendall(welcome_message.encode('utf-8'))

        # Main loop: continuously receive and broadcast messages from this client
        while True:
            try:
                # Receive message from client (buffer size 1024 bytes)
                message = client_socket.recv(1024).decode('utf-8')

                # If message is empty, client has disconnected
                if not message:
                    break

                # Strip any trailing whitespace/newlines
                message = message.strip()

                # Skip empty messages
                if not message:
                    continue

                # Format the message with timestamp and username
                formatted_message = f"{get_timestamp()} {username}: {message}"
                print(f"{formatted_message.strip()}")

                # Broadcast to all other clients
                broadcast(formatted_message, client_socket)

            except UnicodeDecodeError:
                # Handle invalid UTF-8 data
                print(f"[ERROR] Invalid UTF-8 data received from {username}")
                continue

    except ConnectionResetError:
        # Client forcibly closed the connection
        print(f"[SERVER] {username or client_address} connection reset")

    except ConnectionAbortedError:
        # Connection was aborted
        print(f"[SERVER] {username or client_address} connection aborted")

    except OSError as e:
        # Handle socket-related errors
        print(f"[ERROR] Socket error for {username or client_address}: {e}")

    except Exception as e:
        # Handle any other unexpected exceptions
        print(f"[ERROR] Unexpected error handling client {username or client_address}: {e}")

    finally:
        # Clean up: remove client from the list and close the connection
        with clients_lock:
            # Remove this client from the clients list
            clients[:] = [(conn, user) for conn, user in clients
                         if conn != client_socket]

        # Notify others that this user has left
        if username:
            leave_message = f"{get_timestamp()} {username} has left the chat.\n"
            print(f"[SERVER] {username} disconnected")
            broadcast(leave_message)

        # Close the socket connection
        client_socket.close()


def start_server():
    """
    Start the chat server and listen for incoming connections.
    Creates a new thread for each connecting client.
    """
    # Create a TCP socket
    # AF_INET = IPv4, SOCK_STREAM = TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set socket option to reuse address (helps avoid "Address already in use" errors)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # Bind the socket to the host and port
        server_socket.bind((HOST, PORT))

        # Start listening for connections (backlog of 5)
        server_socket.listen(5)

        print(f"[SERVER] Chat server started on {HOST}:{PORT}")
        print(f"[SERVER] Waiting for connections...")

        # Main server loop: accept connections indefinitely
        while True:
            # Accept a new connection (this blocks until a client connects)
            client_socket, client_address = server_socket.accept()

            print(f"[SERVER] New connection attempt from {client_address}")

            # Create a new thread to handle this client
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address),
                daemon=True  # Daemon thread will exit when main program exits
            )

            # Start the thread
            client_thread.start()

            # Show current connection count
            print(f"[SERVER] Active connections: {len(clients) + 1}")

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n[SERVER] Server shutting down...")

    except Exception as e:
        print(f"[ERROR] Server error: {e}")

    finally:
        # Clean up: close all client connections
        with clients_lock:
            for client_conn, username in clients:
                try:
                    client_conn.close()
                except:
                    pass

        # Close the server socket
        server_socket.close()
        print("[SERVER] Server closed")


if __name__ == "__main__":
    # Entry point: start the server when script is run
    start_server()
