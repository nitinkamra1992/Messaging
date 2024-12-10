# Messaging TODOs

## Add a urwid UI for frontend

- [Done] Support login/register page
- Revise current client frontend to support peer-to-peer chat
- Support main page with all chats
- Support specific chat page
- [Done] Support settings and other actions
- Show online/offline symbol on client frontend for all friends
- Optimize UI viz (bold in help), dynamic box sizing for display and chats boxes

## Make 2 separate processes/tasks for send/receive for users

- [Done] Make 2 separate processes/tasks for send/receive for users
- Make corresponding front-end changes to show incoming messages from chats separately
- Play a sound on incoming msg for client

## Build conversation graph for all conversations

- Server must store the full conversation graph, while client must only have their own node and all attached nodes
- Contact addition/deletion must update both server and client graphs
- Build unique message IDs for each message in format {sdr_rcpt_uuid}
- Server must log all messages in this data structure, while users log their own messages in their own sub-copies
- This structure needs to be synced with files when server closing or when client exiting/logging off. Similarly needs to be loaded from file when server starting and when client logging in.

## Introduce command mode for frontend

- [Done] Allow basic commands like :help, :settings, :set, :exit, :login, :register, :logout
-Allow peer2peer commands: :deluser, :chat <username>, :addfriend <username>, :delfriend <username>, :delchat <username>, :back, :listfriends etc.

## Chat histories

- Support chat histories for all conversations on client frontend and server backend using conversation graph
- Add chat history to AI response from server

## [P1] Add persistent login for frontend, until manually logged out

## [P1] Add convenient commands and tools

- E.g., search a conversation for messages matching a keyword

## [P2] End-to-end encrypted messages