from enum import Enum


# App constants
APP_NAME = "Messaging"
APP_VERSION = 0.1
HELP_TEXT = f"""Welcome to {APP_NAME} v{APP_VERSION}.\nINSTRUCTIONS:\n- Messages starting with a colon (:) are treated as commands.\n- Pressing <enter> sends a command/message, while pressing <esc> clears it.\n-Type :help if stuck.\n- You can start by registering with `:register` command or by logging in with `:login` if you already have an account."""


# Server constants
SERVER_NAME: str = "__server__"
SERVER_DISPLAY_NAME: str = "Server"
SERVER_DEFAULT_HOST: str = "localhost"
SERVER_DEFAULT_PORT: str = 10000


# Status codes
STATUS_CODES = {-1: "N/A", 0: "SUCCESS", 1: "FAILURE"}


# Possible App States
class AppStates(Enum):
    LOGOUT = 1
    REG_START = 2
    REG_USER = 3
    LOGIN_START = 4
    LOGIN_USER = 5
    LOGIN = 6