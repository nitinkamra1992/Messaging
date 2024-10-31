import json
import os

from utils.messaging import SERVER_NAME


# Userbase
class Userbase:
    """Userbase manager class"""

    def __init__(self, data_path: str = f"data/{SERVER_NAME}/users.json"):
        self.data_path = data_path

        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                self.user_data = json.load(f)
        else:
            print(f"ERROR: {data_path} not found!")
            print(f"WARNING: Creating new userbase at {data_path}")
            self.user_data = {SERVER_NAME: ""}

    def __post_init__(self):
        # Check to ensure server name exists as a user in the userbase
        assert self.exists_user(SERVER_NAME), f"Server name missing in the userbase"

    def exists_user(self, username: str) -> bool:
        return username in self.user_data

    def verify_login(self, username: str, password: str) -> bool:
        # First check to prevent direct server login
        if username == SERVER_NAME:
            return False
        # Verify login credentials
        return self.exists_user(username) and self.user_data[username] == password

    def add_new_user(self, username: str, password: str) -> bool:
        if self.exists_user(username):
            return False

        self.user_data[username] = password

        # Write userbase to file
        with open(self.data_path, "w") as f:
            json.dump(self.user_data, f, indent=2)

        return True
