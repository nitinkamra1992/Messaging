import argparse
import asyncio
import getpass

from utils.messaging import (
    SERVER_NAME,
    SERVER_DISPLAY_NAME,
    receive_message,
    send_message,
    RegisterRequest,
    LoginRequest,
    UserServerMessage,
)


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
        msg_class = RegisterRequest if register else LoginRequest
        msg = msg_class(username, SERVER_NAME, password)
        await send_message(msg, self.writer)

        # Get response from server
        response = await receive_message(self.reader)
        status = response.status
        content = response.content
        print(f"{SERVER_DISPLAY_NAME}: {content}")

        # Set username
        self.username = username if status == 0 else None

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
            msg = UserServerMessage(self.username, SERVER_NAME, content)
            await send_message(msg, self.writer)

            # Receive response
            try:
                response = await receive_message(self.reader)
                print(f"{SERVER_DISPLAY_NAME}: {response.content}")
            except ValueError:
                print(f"{SERVER_DISPLAY_NAME} disconnected!")
                break

        # Close connection
        self.writer.close()
        self.username = None


if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("-p", "--port", type=int, default=9999)
    args = parser.parse_args()

    # Create a client
    client = ChatClient(args.host, args.port)
    asyncio.run(client.start())
