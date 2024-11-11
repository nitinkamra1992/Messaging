import asyncio
import os
import pickle

from utils.constants import SERVER_NAME


class ChatGraph:
    """Chat Graph Class"""

    def __init__(self, data_path: str = f"data/{SERVER_NAME}/cgraph.pkl"):
        self.data_path = data_path
        self.lock = asyncio.Lock()

        # Load existing chat graph
        if os.path.exists(data_path):
            with open(data_path, "rb") as f:
                self.cgraph = pickle.load(f)
        # Or create a new one
        else:
            print(f"ERROR: {data_path} not found!")
            print(f"WARNING: Creating new chat graph at {data_path}")            
            self.cgraph = {
                SERVER_NAME: {
                    "password": "",
                    "chats": {SERVER_NAME: []},
                }
            }
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            self.dump()

        # Check to ensure all users can talk to server and vice-versa
        print("Running user-chat checks...")
        assert self.exists_user(SERVER_NAME), f"Server name missing in the chat graph"
        for username in self.cgraph:
            assert username in self.cgraph[SERVER_NAME]["chats"], f"{SERVER_NAME} has not added {username} as friend"
            assert SERVER_NAME in self.cgraph[username]["chats"], f"{username} has not added {SERVER_NAME} as friend"
        print("Finished running user-chat checks.")

    def __del__(self):
        # Dump the chat graph to file before destroying it in memory
        self.dump()

    def dump(self):
        # Write cgraph to file
        with open(self.data_path, "wb") as f:
            pickle.dump(self.cgraph, f)

    def exists_user(self, username: str) -> bool:
        return username in self.cgraph

    def verify_login(self, username: str, password: str) -> bool:
        # First check to prevent direct server login
        if username == SERVER_NAME:
            return False
        # Verify login credentials
        return self.exists_user(username) and self.cgraph[username]["password"] == password

    async def add_new_user(self, username: str, password: str) -> bool:
        if self.exists_user(username):
            return False

        async with self.lock:
            # Add new user
            self.cgraph[username] = {
                "password": password,
                "chats": {SERVER_NAME: []}
            }
            self.cgraph[SERVER_NAME]["chats"][username] = []

            # Write cgraph to file
            self.dump()

        return True

    async def del_user(self, username: str) -> bool:
        if (username == SERVER_NAME) or (not self.exists_user(username)):
            return False

        async with self.lock:
            # Delete user
            for k in self.cgraph:
                if username in self.cgraph[k]["chats"]:
                    del self.cgraph[k]["chats"][username]
            del self.cgraph[username]

            # Write cgraph to file
            self.dump()

        return True

    async def add_friend(self, username: str, friend: str) -> bool:
        try:
            assert self.exists_user(username)
            assert self.exists_user(friend)
            assert friend not in self.cgraph[username]["chats"]
            async with self.lock:
                self.cgraph[username]["chats"][friend] = []
                self.dump()
            return True
        except:
            return False

    async def del_friend(self, username: str, friend: str) -> bool:
        try:
            assert self.exists_user(username)
            assert self.exists_user(friend)
            assert friend in self.cgraph[username]["chats"]
            async with self.lock:
                del self.cgraph[username]["chats"][friend]
                self.dump()
            return True
        except:
            return False

    def is_msg_valid(self, msg) -> bool:
        try:
            assert self.exists_user(msg.sender)
            assert self.exists_user(msg.recipient)
            assert msg.sender in self.cgraph[msg.recipient]["chats"]
            assert msg.recipient in self.cgraph[msg.sender]["chats"]
            return True
        except:
            return False

    async def log_msg(self, msg, check_valid=True) -> bool:
        valid = self.is_msg_valid(msg) if check_valid else True
        if valid:
            async with self.lock:
                self.cgraph[msg.sender]["chats"][msg.recipient].append(msg)
                self.dump()
            return True
        return False
