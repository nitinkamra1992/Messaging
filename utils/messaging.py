import datetime
import pickle
from typing import Optional

# Server constants
SERVER_NAME = "__server__"
SERVER_DISPLAY_NAME = "Server"


# Status codes
STATUS_CODES = {-1: "N/A", 0: "SUCCESS", 1: "FAILURE"}


# Message send and receive functions
async def send_message(msg, writer):
    msg = pickle.dumps(msg)
    writer.write(msg)
    await writer.drain()


async def receive_message(reader, max_len: int = 4096):
    response = await reader.read(max_len)
    if response:
        return pickle.loads(response)
    else:
        raise ValueError("None message received likely due to a disconnect.")


# Message base class
class Message:
    """Message base class to be derived from"""

    def __init__(self, sender: str, recipient: str):
        self.sender = sender
        self.recipient = recipient
        self.timestamp = datetime.datetime.now(datetime.timezone.utc)

    def __repr__(self):
        sdr = SERVER_DISPLAY_NAME if self.sender == SERVER_NAME else self.sender
        rcpt = SERVER_DISPLAY_NAME if self.recipient == SERVER_NAME else self.recipient
        return f"{sdr} -> {rcpt} [{self.timestamp}]"


# Derived message classes
class RegisterRequest(Message):
    """Message class to support new user registration"""

    def __init__(self, sender: str, recipient: str, password: str):
        assert recipient == SERVER_NAME
        super().__init__(sender, recipient)
        self.password = password

    def __repr__(self):
        return super().__repr__() + ": Register Request."


class LoginRequest(Message):
    """Message class to support user login"""

    def __init__(self, sender: str, recipient: str, password: str):
        assert recipient == SERVER_NAME
        super().__init__(sender, recipient)
        self.password = password

    def __repr__(self):
        return super().__repr__() + ": Login Request."


class UserServerMessage(Message):
    """Message from user to server"""

    def __init__(self, sender: str, recipient: str, content: str):
        assert recipient == SERVER_NAME
        super().__init__(sender, recipient)
        self.content = content

    def __repr__(self):
        return super().__repr__() + f": {self.content}"


class ServerUserMessage(Message):
    """Message from server to user"""

    def __init__(
        self,
        sender: str,
        recipient: str,
        content: str,
        status: int,
        session: Optional[str] = None,
    ):
        assert sender == SERVER_NAME
        super().__init__(sender, recipient)
        self.content = content
        self.status = status
        self.session = session

    def __repr__(self):
        status_str = (
            "" if self.status == -1 else f"(Status: {STATUS_CODES[self.status]}) "
        )
        return (
            f"(Session: {self.session}) "
            + super().__repr__()
            + f": {status_str}{self.content}"
        )
