import asyncio
import socket

import sys

sys.path.append("./")
from utils.llm import LLM

# Create an LLM object
llm = LLM()

# Create a TCP/IP socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_address = ("localhost", 10000)
print(f"Starting up on {server_address[0]} port {server_address[1]}")
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
while True:
    # Wait for a connection
    print("waiting for a connection..")

    # Accept an incoming connection
    connection, address = sock.accept()
    print(f"Connected to {connection} at {address=}")

    # Receive messages from the client
    while True:
        received_message = connection.recv(4096).decode()
        if not received_message:
            break
        print(f"Client: {received_message}")

        # Process client message and respond back
        response = asyncio.run(llm.query(received_message))
        connection.sendall(response.encode())
        print(f"Server: {response}")

    # Close the connection
    connection.close()
