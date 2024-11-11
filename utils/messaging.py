import datetime
import pickle
import struct

from typing import Optional
from utils.constants import SERVER_NAME, SERVER_DISPLAY_NAME, STATUS_CODES


# Helpful transmission methods
async def send_message(msg, writer):
    # Serialize the message
    msg = pickle.dumps(msg)
    
    # Create a header with the length of the message
    header = struct.pack('!I', len(msg))
    
    # Write the header followed by the message
    writer.write(header + msg)
    await writer.drain()


async def receive_message(reader):
    # Read the fixed-size header (4 bytes for int)
    header = await reader.readexactly(4)
    msg_len = struct.unpack('!I', header)[0]
    
    # Read the full message based on length from header
    msg = await reader.readexactly(msg_len)
    if msg:
        return pickle.loads(msg)
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


class ServerMessage(Message):
    """Message from server"""

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


class UserMessage(Message):
    """Message from a user"""
    def __init__(self, sender: str, recipient: str, content: str):
        super().__init__(sender, recipient)
        self.content = content

    def __repr__(self):
        return super().__repr__() + f": {self.content}"