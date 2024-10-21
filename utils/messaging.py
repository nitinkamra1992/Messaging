import datetime


# Server constants
SERVER_NAME = "__server__"


# Message types
MSG_TYPES = set([
    "client_register_request",
    "client_login_request",
    "client_server_message",
    "server_client_response"
])


# Status codes
STATUS_CODES = {
    -1: "N/A",
    0: "SUCCESS",
    1: "FAILURE"
}


# Message type templates
MSG_TEMPLATES = {
    "client_register_request": {
        "msg_type": "str",
        "username": "str",
        "password": "str"
    },
    "client_login_request": {
        "msg_type": "str",
        "username": "str",
        "password": "str"
    },
    "client_server_message": {
        "msg_type": "str",
        "username": "str",
        "message": "str"
    },
    "server_client_response": {
        "msg_type": "str",
        "username": "str",
        "message": "str",
        "status": "int"
    },
}