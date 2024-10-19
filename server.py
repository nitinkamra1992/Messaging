import asyncio
import json

import sys
sys.path.append("./")

from utils.llm import LLM
from utils.userbase import Userbase


# Server class
class ChatServer:

    def __init__(self, port=10000):
        self.port = port
        self.llm = LLM()
        self.userbase = Userbase()

    async def receive_message(self, reader):
        response = await reader.read(4096)
        if response:
            return json.loads(response.decode())

    async def send_message(self, msg_struct, writer):
        msg = json.dumps(msg_struct)
        writer.write(msg.encode())
        await writer.drain()

    async def handle_client(self, reader, writer):
        # Get the client ID (peername) from the transport object
        client_id = writer.transport.get_extra_info("peername")
        temp_client_name = str(client_id[1])
        print(f"New client connected: {temp_client_name}")

        # Authenticate user
        username = None
        while not username:
            try:
                # Read message
                msg_struct = await self.receive_message(reader)

                # Attempt to authenticate user
                assert msg_struct["msg_type"] in ["client_register_request", "client_login_request"]
                success = False
                response_msg = None
                if msg_struct["msg_type"] == "client_register_request":
                    success = self.userbase.add_new_user(msg_struct["username"], msg_struct["password"])
                    if success:
                        response_msg = f"New username {msg_struct['username']} registered and logged in."
                        username = msg_struct["username"]
                    else:
                        response_msg = f"Username {msg_struct['username']} is taken. Try another one."
                elif msg_struct["msg_type"] == "client_login_request":
                    success = self.userbase.verify_login(msg_struct["username"], msg_struct["password"])
                    if success:
                        response_msg = f"Login successful."
                        username = msg_struct["username"]
                    else:
                        response_msg = f"Incorrect username or password."
                print(f"Server -> {temp_client_name}: {response_msg}")

                # Respond back
                response_struct = {
                    "msg_type": "server_client_response",
                    "username": username,
                    "message": response_msg,
                    "status": 0 if success else 1
                }
                await self.send_message(response_struct, writer)
            except Exception as e:
                print(f"ERROR occurred while handling client {temp_client_name}: {e}")
                print(f"{temp_client_name} logged out.")
                return

        # Chat loop
        while True:
            try:
                # Read message
                msg_struct = await self.receive_message(reader)
                assert msg_struct["msg_type"] == "client_server_message"
                assert msg_struct["username"] == username
                message = msg_struct["message"]
                print(f"{username}[{temp_client_name}]: {message}")

                # Process client message and respond back
                response = await self.llm.query(message)
                print(f"Server -> {username}[{temp_client_name}]: {response}")
                response_struct = {
                    "msg_type": "server_client_response",
                    "username": username,
                    "message": response,
                    "status": -1
                }
                await self.send_message(response_struct, writer)
            except Exception as e:
                print(f"ERROR occurred while handling {username}[{temp_client_name}]: {e}")
                print(f"{username}[{temp_client_name}] logged out.")
                username = None
                break

    async def start(self):
        server = await asyncio.start_server(self.handle_client, "localhost", self.port)
        print(f"Server started on port {self.port}")
        async with server:
            await server.serve_forever()
        print(f"Server closed.")


# Create and start the server
server = ChatServer()
asyncio.run(server.start())