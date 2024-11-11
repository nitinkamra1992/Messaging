import argparse
import asyncio

from utils.llm import LLM
from utils.chat import ChatGraph
from utils.connections import ConnectionManager
from utils.constants import SERVER_NAME
from utils.messaging import (
    receive_message,
    send_message,
    RegisterRequest,
    LoginRequest,
    UserMessage,
    ServerMessage,
)
from utils.outgoing import OutgoingManager


# Server class
class ChatServer:
    def __init__(self, host="localhost", port=10000):
        self.host = host
        self.port = port
        self.llm = LLM()
        self.chat_graph = ChatGraph()
        self.connection_manager = ConnectionManager()
        self.outgoing_manager = OutgoingManager()

    async def attempt_delivery(self, msg, enqueue=False):
        writer = self.connection_manager.get_writer(msg.recipient)
        success = False
        if writer is not None:
            try:
                await send_message(msg, writer)
                await self.chat_graph.log_msg(msg, check_valid=False)
                success = True
                print(msg)
            except Exception as e:
                print(e)
        if not success and enqueue:
            await self.outgoing_manager.put(msg)

    async def deliver_outgoing_msgs(self, username):
        while (msg := await self.outgoing_manager.get(username)) is not None:
            await self.attempt_delivery(msg, enqueue=True)

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
                    registered = await self.chat_graph.add_new_user(msg.sender, msg.password)
                    if not registered:
                        response_content = (
                            f"Username {msg.sender} is taken. Try another one."
                        )
                    else:
                        logged_in = await self.connection_manager.login(msg.sender, reader, writer)
                        if not logged_in:
                            response_content = f"Can only log in from a single session. Username {msg.sender} is already logged in from a different session."
                        else:
                            response_content = (
                                f"New username {msg.sender} registered and logged in."
                            )
                            username = msg.sender
                            success = True
                elif type(msg) == LoginRequest:
                    verified = self.chat_graph.verify_login(msg.sender, msg.password)
                    if not verified:
                        response_content = f"Incorrect username or password."
                    else:
                        logged_in = await self.connection_manager.login(msg.sender, reader, writer)
                        if not logged_in:
                            response_content = f"Can only log in from a single session. Username {msg.sender} is already logged in from a different session."
                        else:
                            response_content = f"Login successful."
                            username = msg.sender
                            success = True
                else:
                    success = False
                    response_content = f"Bad request."

                # Respond back
                response = ServerMessage(
                    SERVER_NAME,
                    username,
                    response_content,
                    0 if success else 1,
                    session_id,
                )

                # Do not use attempt_delivery below since the user is not yet
                # logged in or may not even be registered
                await send_message(response, writer)
                print(response)

            except Exception as e:
                print(e)
                if username:
                    await self.connection_manager.logout(username)
                print(f"[{session_id}] logged out.")
                return

        # Deliver pending outgoing messages
        if username:
            await self.deliver_outgoing_msgs(username)

        # Chat loop
        while username:
            try:
                # Read message
                msg = await receive_message(reader)
                assert type(msg) == UserMessage
                assert msg.sender == username
                print(msg)

                # Take action on the message
                if msg.recipient == SERVER_NAME:
                    # Log message
                    log_status = await self.chat_graph.log_msg(msg, check_valid=True)

                    # Respond back to client
                    if log_status:
                        response_content = await self.llm.query(msg.content)
                    else:
                        response_content = "Invalid user message"
                    response = ServerMessage(
                        SERVER_NAME, username, response_content, -1, session_id
                    )
                    await self.attempt_delivery(response, enqueue=True)
                else:
                    # TODO(nitin): Implement this
                    raise NotImplementedError("Peer-to-peer messages are currently not implemented.")
            except Exception as e:
                await self.connection_manager.logout(username)
                print(f"{username}[{session_id}] logged out.")
                username = None

    async def start(self):
        # Create server
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f"Server started on port {self.port}")

        # Start serving clients
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("-p", "--port", type=int, default=10000)
    args = parser.parse_args()

    # Create and start the server
    server = ChatServer(args.host, args.port)
    asyncio.run(server.start())
