"""
chat_client.py - TCP Chat Client

This client connects to the chat server and allows the user to send and receive
messages. It uses threading to simultaneously handle incoming messages from the
server and user input for sending messages.
"""

import socket
import threading
import sys

# Server connection configuration
HOST = '127.0.0.1'  # Server address (localhost)
PORT = 5555         # Server port (must match server's PORT)

# Flag to control the receive thread
running = True


def receive_messages(client_socket):
    """
    Continuously receive and display messages from the server.
    This function runs in a separate thread to allow simultaneous
    sending and receiving of messages.

    Args:
        client_socket (socket): The socket connected to the server
    """
    global running

    while running:
        try:
            # Receive message from server (buffer size 1024 bytes)
            message = client_socket.recv(1024).decode('utf-8')
            
            # If message is empty, server has closed the connection
            if not message:
                print("\n[CLIENT] Connection to server lost.")
                running = False
                break
            
            # Strip trailing whitespace but preserve message content
            message = message.rstrip('\n')
            
            # Display the message from the server
            # Add newline for proper formatting, then show prompt on new line
            print(f"\r{message}")
            print("You: ", end='', flush=True)
            
        except UnicodeDecodeError:
            # Handle invalid UTF-8 data
            print("\n[ERROR] Received invalid data from server.")
            continue

        except ConnectionResetError:
            # Server forcibly closed the connection
            print("\n[CLIENT] Server closed the connection.")
            running = False
            break
        
        except ConnectionAbortedError:
            # Connection was aborted
            print("\n[CLIENT] Connection aborted.")
            running = False
            break
        
        except OSError as e:
            # Handle socket-related errors
            if running:
                print(f"\n[ERROR] Socket error: {e}")
            running = False
            break
            
        except Exception as e:
            # Handle any other unexpected exceptions
            if running:  # Only print error if we're still supposed to be running
                print(f"\n[ERROR] Unexpected error receiving message: {e}")
            running = False
            break


def send_messages(client_socket):
    """
    Continuously read user input and send messages to the server.
    This function runs in the main thread.

    Args:
        client_socket (socket): The socket connected to the server
    """
    global running

    try:
        while running:
            # Get user input
            message = input("You: ")

            # Check if user wants to quit
            if message.lower() in ['quit', 'exit', 'q']:
                print("[CLIENT] Disconnecting from chat...")
                running = False
                break

            # Only send non-empty messages
            if message.strip():
                try:
                    # Send the message to the server (encode to bytes)
                    # Use sendall() to ensure all data is sent
                    client_socket.sendall(message.encode('utf-8'))
                except (BrokenPipeError, ConnectionResetError, OSError) as e:
                    print(f"[CLIENT] Failed to send message: {e}")
                    running = False
                    break

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n[CLIENT] Disconnecting from chat...")
        running = False

    except Exception as e:
        print(f"\n[ERROR] Error in send loop: {e}")
        running = False


def start_client():
    """
    Connect to the chat server and start the client application.
    Creates a receive thread for incoming messages and runs a send loop
    for user input in the main thread.
    """
    global running

    # Create a TCP socket
    # AF_INET = IPv4, SOCK_STREAM = TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        print(f"[CLIENT] Connecting to server at {HOST}:{PORT}...")
        client_socket.connect((HOST, PORT))
        print(f"[CLIENT] Connected successfully!")

        # Receive the username prompt from server
        prompt = client_socket.recv(1024).decode('utf-8')
        print(prompt, end='')

        # Get username from user
        username = input().strip()
        
        # Send username to server using sendall()
        client_socket.sendall(username.encode('utf-8'))

        # Receive welcome message
        welcome = client_socket.recv(1024).decode('utf-8')
        print(welcome)

        print("=" * 50)
        print("Chat room joined! Type your messages below.")
        print("Type 'quit', 'exit', or 'q' to leave the chat.")
        print("=" * 50)

        # Create and start the receive thread
        # This thread will continuously listen for messages from the server
        receive_thread = threading.Thread(
            target=receive_messages,
            args=(client_socket,),
            daemon=True  # Daemon thread will exit when main program exits
        )
        receive_thread.start()

        # Run the send loop in the main thread
        # This allows the user to type and send messages
        send_messages(client_socket)

    except ConnectionRefusedError:
        print(f"[ERROR] Could not connect to server at {HOST}:{PORT}")
        print("[ERROR] Make sure the server is running and try again.")

    except Exception as e:
        print(f"[ERROR] Client error: {e}")

    finally:
        # Clean up: close the socket connection
        running = False
        print("[CLIENT] Closing connection...")
        client_socket.close()
        print("[CLIENT] Disconnected. Goodbye!")

        # Give a moment for threads to finish
        import time
        time.sleep(0.5)


if __name__ == "__main__":
    # Entry point: start the client when script is run
    start_client()
