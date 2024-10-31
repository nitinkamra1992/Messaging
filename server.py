import argparse
import asyncio

from utils.llm import LLM
from utils.userbase import Userbase
from utils.constants import SERVER_NAME
from utils.messaging import (
    receive_message,
    send_message,
    RegisterRequest,
    LoginRequest,
    UserServerMessage,
    ServerUserMessage,
)


# Server class
class ChatServer:
    def __init__(self, host="localhost", port=10000):
        self.host = host
        self.port = port
        self.llm = LLM()
        self.userbase = Userbase()

    async def handle_client(self, reader, writer):
        # Get the client ID (peername) from the transport object
        client_id = writer.transport.get_extra_info("peername")
        session_id = str(client_id[1])
        print(f"New client connected: {session_id}")

        # Authenticate user
        username = None
        while not username:
            try:
                # Read message
                msg = await receive_message(reader)
                print(msg)

                # Attempt to authenticate user
                success = False
                response_content = None
                if type(msg) == RegisterRequest:
                    success = self.userbase.add_new_user(msg.sender, msg.password)
                    if success:
                        response_content = (
                            f"New username {msg.sender} registered and logged in."
                        )
                        username = msg.sender
                    else:
                        response_content = (
                            f"Username {msg.sender} is taken. Try another one."
                        )
                elif type(msg) == LoginRequest:
                    success = self.userbase.verify_login(msg.sender, msg.password)
                    if success:
                        response_content = f"Login successful."
                        username = msg.sender
                    else:
                        response_content = f"Incorrect username or password."
                else:
                    success = False
                    response_content = f"Bad request."

                # Respond back
                response = ServerUserMessage(
                    SERVER_NAME,
                    username,
                    response_content,
                    0 if success else 1,
                    session_id,
                )
                await send_message(response, writer)
                print(response)

            except Exception as e:
                print(f"[{session_id}] logged out.")
                return

        # Chat loop
        while True:
            try:
                # Read message
                msg = await receive_message(reader)
                assert type(msg) == UserServerMessage
                assert msg.sender == username
                print(msg)

                # Respond back to client
                response_content = await self.llm.query(msg.content)
                response = ServerUserMessage(
                    SERVER_NAME, username, response_content, -1, session_id
                )
                await send_message(response, writer)
                print(response)
            except Exception as e:
                print(f"{username}[{session_id}] logged out.")
                username = None
                break

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f"Server started on port {self.port}")
        async with server:
            await server.serve_forever()
        print(f"Server closed.")


if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("-p", "--port", type=int, default=10000)
    args = parser.parse_args()

    # Create and start the server
    server = ChatServer(args.host, args.port)
    asyncio.run(server.start())
