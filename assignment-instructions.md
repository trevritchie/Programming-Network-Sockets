# Programming Network Sockets

## Objective

Students will build a simple chat room application using Python's sockets and threading libraries. The project introduces fundamental networking concepts (client-server model, TCP sockets) and concurrent programming (handling multiple clients with threads). 

Sockets can be thought of as endpoints in a communication channel that is bi-directional and establishes communication between a server and one or more clients. Here, we set up a socket on each end and allow a client to interact with other clients via the server. The socket on the server side associates itself with some hardware port on the server-side. Any client that has a socket associated with the same port can communicate with the server socket.

---

## Learning Outcomes

By completing this project, students will be able to:

- Implement a TCP server and client using Python sockets
- Use threading to handle multiple clients concurrently
- Apply string formatting and timestamps to messages
- Understand the flow of data in a multi-user chat system
- Extend the base functionality with enhancements

---

## Project Description

Students will create:

### Chat Server (`chat_server.py`)

- Listens for incoming TCP connections
- Handles multiple clients simultaneously using threads
- Receives a username from each client
- Broadcasts messages to all connected clients (except the sender)
- Prefixes each message with a timestamp and username
- Notifies others when a user joins or leaves

### Chat Client (`chat_client.py`)

- Connects to the server
- Prompts the user for a username
- Runs a receive thread (to print messages from the server)
- Runs a send loop (to capture user input and send messages)

---

## Deliverables

1. A working `chat_server.py` and `chat_client.py`
2. Screenshot(s) showing at least three clients chatting simultaneously
3. A short (1–2 page) write-up explaining:
   - How the server manages multiple clients
   - How usernames and timestamps are handled
   - One improvement they would make (examples: private messaging, logging chat to a file, GUI)

---

## References

- [This article demonstrates](https://www.geeksforgeeks.org/simple-chat-room-using-python/) – How to set up a simple Chat Room server and allow multiple clients to connect to it using a client-side script. The code uses the concept of sockets and threading.
- [You can use this article as well](https://www.neuralnine.com/tcp-chat-in-python/) – This one is easier and has less issues with python2 vs python3

---

## Grading Rubric

| Criteria | Exceeds (4 pts) | Mastery (3 pts) | Near (2 pts) | Below (1 pt) | Points |
|----------|----------------|-----------------|--------------|--------------|---------|
| **Multiple Clients** | Fully functional with no crashes | Works with 2–3 clients but unstable | Limited to 1–2 clients reliably | Does not work | /4 pts |
| **Client Messaging** | Messages are broadcast correctly with username + timestamp | Messages broadcast but missing username or timestamp | Messages broadcast but incorrectly labeled | Messages not delivered | /4 pts |
| **Code Quality** | Well-structured, clear comments | Mostly readable, some comments | Messy, few comments | Very hard to follow | /4 pts |
| **Write-up** | Thorough, explains flow + improvements | Explains flow but lacks depth | Minimal explanation | Missing | /4 pts |
| | | | | **Total** | **/16 pts** |

---
