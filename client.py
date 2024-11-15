import argparse
import asyncio
import dataclasses
import inspect
import urwid

from typing import Any, Tuple

from utils.constants import (
    APP_NAME,
    APP_VERSION,
    SERVER_NAME,
    SERVER_DEFAULT_HOST,
    SERVER_DEFAULT_PORT,
    SERVER_DISPLAY_NAME,
    AppStates,
    HELP_TEXT
)
from utils.messaging import (
    receive_message,
    send_message,
    RegisterRequest,
    LoginRequest,
    UserMessage,
)


class CommandBox(urwid.Edit):
    signals = urwid.Edit.signals + ["submit"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def keypress(self, size, key: str) -> str | None:
        if key == "enter":
            urwid.emit_signal(self, "submit", self.get_edit_text())
            self.edit_text = ""
        elif key == "esc":
            self.edit_text = ""
        else:
            return super().keypress(size, key)


# AppState class
@dataclasses.dataclass
class AppState:
    state: AppStates = AppStates.LOGOUT
    username: str | None = None
    recipient: str = SERVER_NAME
    reader = None
    writer = None


# AppAttributes class
@dataclasses.dataclass
class AppAttributes:
    host: str = SERVER_DEFAULT_HOST
    port: int = SERVER_DEFAULT_PORT


# Client class
class ChatClient:
    def __init__(self, host: str = SERVER_DEFAULT_HOST, port: int = SERVER_DEFAULT_PORT):
        # App state and attributes
        self.app_attributes = AppAttributes(host=host, port=port)
        self.app_state = AppState()

        # Event loop
        self.evl = asyncio.new_event_loop()
        asyncio.set_event_loop(self.evl)

        # UI widgets
        self.display = urwid.Text(HELP_TEXT, align="left")
        self.display_box = urwid.LineBox(self.display)
        self.chats = urwid.Text("", align="center")
        self.chats_box = urwid.LineBox(self.chats)
        self.main = urwid.Columns([self.chats_box, self.display_box])
        self.div = urwid.Divider()
        self.command = CommandBox("Command: ", edit_text="")
        self.command_box = urwid.LineBox(self.command)
        self.pile = urwid.Pile([self.main, self.div, self.command_box])
        self.top = urwid.Filler(self.pile, valign="top")

        # Signals
        urwid.connect_signal(self.command, "submit", self.executor_wrapper)

        # Commands
        self.commands = {
            "help": self.help,
            "attributes": self.attributes,
            "set": self.set,
            "login": self.login,
            "logout": self.logout,
            "exit": self.exit,
            "register": self.register,
            "back": self.back,
        }

    def _generate_help_str(self) -> str:
        func_helps = []
        for func_name, func in self.commands.items():
            func_doc = inspect.getdoc(func)
            func_args = inspect.signature(func).parameters
            func_help = f":{func_name} " + " ".join([a for a in func_args]) + f"\n{func_doc}"
            func_helps.append(func_help)
        full_text = HELP_TEXT + "\n\nCOMMANDS:\n" + "\n".join(func_helps)
        return full_text

    def help(self):
        """Get help text with all commands and their descriptions"""
        self.display.set_text(self._generate_help_str())

    def attributes(self):
        """Display all app attributes"""
        attributes_str = "ATTRIBUTES:\n"
        for attr_name, attr_val in dataclasses.asdict(self.app_attributes).items():
            attributes_str += f"{attr_name}: {attr_val}\n"
        self.display.set_text(self.display.text + "\n\n" + attributes_str)

    def set(self, attr: str, val: Any):
        """Set an app attribute to a value"""
        if attr in self.app_attributes.__dict__:
            setattr(self.app_attributes, attr, val)
            self.display.set_text(self.display.text + "\n\n" + f"{attr} set to {val}" + "\n")
        else:
            self.display.set_text(self.display.text + "\n\n" + f"Unknown attribute: {attr}" + "\n")

    def login(self):
        """Log in"""
        if self.app_state.state != AppStates.LOGIN:
            self.display.set_text("Enter your username:")
            self.app_state.state = AppStates.LOGIN_START

    def logout(self):
        """Log out"""
        self.app_state = AppState()
        self.display.set_text("Logged out.")

    def exit(self) -> None:
        """Log out and exit the app"""
        self.logout()
        raise urwid.ExitMainLoop()

    def register(self):
        """Create a new username and password"""
        if self.app_state.state != AppStates.LOGIN:
            self.display.set_text("Registering new user..\nEnter your username:")
            self.app_state.state = AppStates.REG_START

    def back(self):
        """Go back"""
        pass

    def executor_wrapper(self, text: str) -> None:
        asyncio.ensure_future(self.executor(text), loop=self.evl)

    async def executor(self, text: str) -> None:
        # Command mode
        if text.startswith(":"):
            cmd_split = text[1:].split()
            cmd = cmd_split[0]
            args = cmd_split[1:] if len(cmd_split) > 1 else []
            if cmd in self.commands:
                self.commands[cmd](*args)
            else:
                self.display.set_text(self.display.text + "\n\n" + f"Unknown command: {cmd}" + "\n")
        # Text mode
        else:
            # REG_START or LOGIN_START
            if self.app_state.state in [AppStates.REG_START, AppStates.LOGIN_START]:
                self.app_state.username = text
                self.display.set_text("Enter your password:")
                self.app_state.state = (AppStates.REG_USER if self.app_state.state == AppStates.REG_START else AppStates.LOGIN_USER)
            # REG_USER or LOGIN_USER
            elif self.app_state.state in [AppStates.REG_USER, AppStates.LOGIN_USER]:
                password = text
                register = (self.app_state.state == AppStates.REG_USER)
                success, response = await self.authenticate_user(self.app_state.username, password, register)
                self.display.set_text(f"{SERVER_DISPLAY_NAME}: {response}")
                if success:
                    assert self.app_state.username is not None
                    assert self.app_state.reader is not None
                    assert self.app_state.writer is not None
                    self.app_state.state = AppStates.LOGIN
                else:
                    self.app_state = AppState()  # Reset app_state
            # LOGIN
            elif self.app_state.state == AppStates.LOGIN:
                msg = UserMessage(self.app_state.username, self.app_state.recipient, text)
                try:
                    # Send message
                    await send_message(msg, self.app_state.writer)
                    self.display.set_text(self.display.text + "\n" + f"{self.app_state.username}: {text}")
                except:
                    self.app_state = AppState()
                    self.display.set_text(f"{SERVER_DISPLAY_NAME} disconnected!")
            # LOGOUT
            else:  # self.app_state.state in [AppStates.LOGOUT]
                pass

        # Redraw UI
        self.evl.call_soon(self.urwid_loop.draw_screen)

    async def authenticate_user(self, username: str, password: str, register: bool = False) -> Tuple[bool, str]:
        # Connect to server
        self.app_state.reader, self.app_state.writer = await asyncio.open_connection(self.app_attributes.host, self.app_attributes.port)

        # Send server request
        msg_class = RegisterRequest if register else LoginRequest
        msg = msg_class(username, SERVER_NAME, password)
        await send_message(msg, self.app_state.writer)

        # Get response from server
        response = await receive_message(self.app_state.reader)
        status = response.status
        content = response.content
        success = (status == 0)

        # Return response
        return success, content

    async def continuous_receiver(self):
        while True:
            if self.app_state.state == AppStates.LOGIN:
                try:
                    msg = await receive_message(self.app_state.reader)
                    self.display.set_text(self.display.text + "\n" + f"{SERVER_DISPLAY_NAME}: {msg.content}")
                    self.evl.call_soon(self.urwid_loop.draw_screen)
                except:
                    pass
            else:
                await asyncio.sleep(0.1)

    def start(self):
        self.receiver_task = self.evl.create_task(self.continuous_receiver())
        self.urwid_loop = urwid.MainLoop(self.top, event_loop=urwid.AsyncioEventLoop(loop=self.evl))
        self.urwid_loop.run()


if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=SERVER_DEFAULT_HOST)
    parser.add_argument("-p", "--port", type=int, default=SERVER_DEFAULT_PORT)
    args = parser.parse_args()

    # Create a client
    client = ChatClient(args.host, args.port)
    client.start()
