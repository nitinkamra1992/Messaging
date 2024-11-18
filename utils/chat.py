import asyncio
import os
import pickle

from utils.constants import SERVER_NAME


class ChatGraph:
    """Chat Graph Class"""

    def __init__(self, mainuser: str, datapath: str):
        self.datapath = datapath
        self.lock = asyncio.Lock()
        self.mainuser = mainuser

        # Load existing chat graph
        if (datapath is not None) and os.path.exists(datapath):
            with open(datapath, "rb") as f:
                self.cgraph = pickle.load(f)
        # Or create a new one
        else:
            if self.mainuser == SERVER_NAME:
                print(f"ERROR: datapath {datapath} not found!")
                print(f"WARNING: Creating new chat graph")
                self.cgraph = {
                    SERVER_NAME: {
                        "password": "",
                        "chats": {SERVER_NAME: []},
                    }
                }
            else:
                self.cgraph = {
                    self.mainuser: {
                        "chats": {
                            SERVER_NAME: [],
                            self.mainuser: [],
                        },
                    },
                    SERVER_NAME: {
                        "chats": {
                            self.mainuser: []
                        }
                    }
                }
            if datapath:
                os.makedirs(os.path.dirname(datapath), exist_ok=True)
                self.dump()

        # Run basic checks
        self._run_checks()

    def _run_checks(self):
        """Run basic checks on cgraph"""
        # Check mainuser exists in cgraph
        assert self.exists_user(self.mainuser), f"{self.mainuser} missing in the chat graph"
        assert self.exists_user(SERVER_NAME), f"{SERVER_NAME} missing in the chat graph"
        # Check to ensure all users can talk to mainuser and vice-versa
        for username in self.cgraph:
            assert username in self.cgraph[self.mainuser]["chats"], f"{self.mainuser} has not added {username} as friend"
            if self.mainuser == SERVER_NAME:
                assert self.mainuser in self.cgraph[username]["chats"], f"{username} has not added {self.mainuser} as friend"
        # Check non-server graphs don't have excess connections
        if self.mainuser != SERVER_NAME:
            for username in self.cgraph:
                if username != self.mainuser:
                    assert len(self.cgraph[username]["chats"]) == 1

    def dump(self):
        # Write cgraph to file
        if self.datapath is not None:
            with open(self.datapath, "wb") as f:
                pickle.dump(self.cgraph, f)

    def exists_user(self, username: str) -> bool:
        return username in self.cgraph

    def verify_login(self, username: str, password: str) -> bool:
        # This function is only possible on server's graph
        if self.mainuser != SERVER_NAME:
            return False
        # Check to prevent direct server login
        if username == SERVER_NAME:
            return False
        # Verify login credentials
        return self.exists_user(username) and self.cgraph[username]["password"] == password

    async def add_user(self, username: str, password: str | None = None) -> bool:
        if self.exists_user(username):
            return False

        async with self.lock:
            # Add new user
            if self.mainuser == SERVER_NAME:
                self.cgraph[username] = {
                    "password": password,
                    "chats": {SERVER_NAME: [], username: []}
                }
                self.cgraph[SERVER_NAME]["chats"][username] = []
            else:
                self.cgraph[username] = {"chats": {}}
                self.cgraph[self.mainuser]["chats"][username] = []

            # Write cgraph to file
            self.dump()

        return True

    async def del_user(self, username: str) -> bool:
        if (username == self.mainuser) or (not self.exists_user(username)):
            return False

        async with self.lock:
            # Delete user
            if self.mainuser == SERVER_NAME:
                for k in self.cgraph:
                    if username in self.cgraph[k]["chats"]:
                        del self.cgraph[k]["chats"][username]
                del self.cgraph[username]
            else:
                if username in self.cgraph[self.mainuser]["chats"]:
                    del self.cgraph[self.mainuser]["chats"][username]
                del self.cgraph[username]

            # Write cgraph to file
            self.dump()

        return True

    async def add_friend(self, username: str, friend: str) -> bool:
        if self.mainuser == SERVER_NAME:
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
        return False

    async def del_friend(self, username: str, friend: str) -> bool:
        if self.mainuser == SERVER_NAME:
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
        else:
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

    def get_user_graph(self, username) -> dict:
        # Only server can generate graphs for users
        if (self.mainuser != SERVER_NAME) or (not self.exists_user(username)):
            return None

        user_cgraph = {username: {"chats": {}}}
        for connection, chats in self.cgraph[username]["chats"].items():
            user_cgraph[username]["chats"][connection] = chats
            if (connection != username) and (username in self.cgraph[connection]["chats"]):
                user_cgraph[connection] = {
                    "chats": {
                        username: self.cgraph[connection]["chats"][username]
                    }
                }
        return user_cgraph

    async def load_cgraph(self, cgraph: dict) -> bool:
        # Only users can load external cgraphs
        if self.mainuser != SERVER_NAME:
            async with self.lock:
                self.cgraph = cgraph
                self._run_checks()  # Run sanity checks
                self.dump()
            return True
        return False
