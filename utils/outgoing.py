import asyncio

from utils.constants import SERVER_NAME


class OutgoingManager:
    """Outgoing messages manager class for server"""

    def __init__(self):
        self.lock = asyncio.Lock()
        self.outgoing_msgs = {}

    async def put(self, msg):
        async with self.lock:
            if msg.recipient not in self.outgoing_msgs:
                self.outgoing_msgs[msg.recipient] = asyncio.Queue()
            await self.outgoing_msgs[msg.recipient].put(msg)

    async def get(self, username):
        async with self.lock:
            if len(self.outgoing_msgs.get(username, [])) == 0:
                return None
            else:
                return self.outgoing_msgs[username].get()
