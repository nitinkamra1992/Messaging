from utils.constants import SERVER_NAME


# Connection manager
class ConnectionManager:
    """Connection manager class"""

    def __init__(self):
        self.online = set([SERVER_NAME])

    def __post_init__(self):
        assert self.is_online(SERVER_NAME), f"{SERVER_NAME} must be online at launch time!"

    def is_online(self, username: str) -> bool:
        return username in self.online

    def login(self, username: str) -> bool:
        if not self.is_online(username):
            self.online.add(username)
            return True
        else:
            return False

    def logout(self, username: str) -> bool:
        if self.is_online(username):
            self.online.remove(username)
        return True