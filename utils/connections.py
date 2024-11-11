from utils.constants import SERVER_NAME


# Connection manager
class ConnectionManager:
    """Connection manager class"""

    def __init__(self):
        self.online = {SERVER_NAME: (None, None)}

    def __post_init__(self):
        assert self.is_online(SERVER_NAME), f"{SERVER_NAME} must be online at launch time!"

    def is_online(self, username: str) -> bool:
        return username in self.online

    def login(self, username: str, reader, writer) -> bool:
        if not self.is_online(username):
            self.online[username] = (reader, writer)
            return True
        else:
            return False

    def logout(self, username: str) -> bool:
        if self.is_online(username):
            del self.online[username]
        return True

    def get_reader(self, username: str):
        if self.is_online(username):
            return self.online[username][0]

    def get_writer(self, username: str):
        if self.is_online(username):
            return self.online[username][1]
