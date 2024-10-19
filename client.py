import asyncio
import json
import getpass

import sys
sys.path.append("./")
from utils.messaging import STATUS_CODES


# Client class
class ChatClient:

    def __init__(self, host="localhost", port=9999):
        self.host = host
        self.port = port
        self.username = None

    async def authenticate_user(self, register=False):
        if register:
            print("Registering new user..")

        # Get username and password
        username = input("Input your username: ")
        password = getpass.getpass("Input your password: ")

        # Send server request
        msg_struct = {
            "msg_type": "client_register_request" if register else "client_login_request",
            "username": username,
            "password": password
        }
        await self.send_message(msg_struct)

        # Get response from server
        response_struct = await self.receive_message()

        # Parse server response
        assert response_struct["msg_type"] == "server_client_response"
        status = response_struct["status"]
        response_msg = response_struct["message"]
        print(f"Server: [{STATUS_CODES[status]}] {response_msg}")

        # Set username
        self.username = (username if status == 0 else None)

    async def send_message(self, msg_struct):
        msg = json.dumps(msg_struct)
        self.writer.write(msg.encode())
        await self.writer.drain()

    async def receive_message(self):
        response = await self.reader.read(4096)
        if response:
            return json.loads(response.decode())

    async def start(self):
        # Connect to server
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

        # Register/login
        while not self.username:
            intent = input("Enter 0 to register or any other key to login: ")
            if intent == "0":
                await self.authenticate_user(register=True)
            else:
                await self.authenticate_user(register=False)

        # Chat loop
        while True:
            # Send message
            content = input(f"{self.username}: ")
            msg_struct = {
                "msg_type": "client_server_message",
                "username": self.username,
                "message": content
            }
            await self.send_message(msg_struct)

            # Receive response
            response_struct = await self.receive_message()
            assert response_struct["msg_type"] == "server_client_response"
            assert response_struct["username"] == self.username
            status = response_struct["status"]
            response_msg = response_struct["message"]
            print(f"Server: {response_msg}")
        
        # Close connection
        self.writer.close()
        self.username = None


# Create a client and send a message
client = ChatClient()
asyncio.run(client.start())