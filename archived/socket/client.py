import socket

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ("localhost", 9999)
sock.connect(server_address)

while True:
    # Send messages to the server
    message = input("Client: ")
    sock.sendall(message.encode())
    if message == "quit":
        break

    # Receive message from the server
    received_message = sock.recv(4096).decode()
    print(f"Server: {received_message}")

# Close the connection
sock.close()
