# Messaging TODOs

## Make 2 separate processes/tasks for send/receive for users

- Make 2 separate processes/tasks for send/receive for users
- Make corresponding front-end changes to show incoming messages from chats separately
- Play a sound on incoming msg for client

## Build conversation graph for all conversations

- [Done] Users can only message two-way contacts
- Server must store the full conversation graph, while client must only have their own node and all attached nodes
- Contact addition/deletion must update both server and client graphs
- Build unique message IDs for each message in format {sdr.rcpt.uuid}
- Server must log all messages in this data structure, while users log their own messages in their own sub-copies
- This structure needs to be synced with files when server closing or when client exiting/logging off. Similarly needs to be loaded from file when server starting and when client logging in.

## Peer-to-peer chat in backend

- [Done] Support peer-to-peer type messages in backend
- [Done] Must support user-to-server message with AI responses and also user-self-messaging
- [Done] Need to store messages for offline users
- [Done] Need to support pushing all offline messages on user login

## Introduce command mode for frontend

- Allow basic commands like :help, :exit, :login, :logout, :chat <username>, :addfriend <username>, :delfriend <username>, delchat <username>, :back, :listfriends etc.
- Revise current client frontend to support peer-to-peer chat and add relevant commands
- Show online/offline symbol on client frontend for all users

## Chat histories

- Support chat histories for all conversations on client frontend and server backend using conversation graph
- Add chat history to AI response from server

## [P1] Add persistent login for frontend, until manually logged out

## [P1] Add a flask UI for frontend

## [P1] Add convenient commands and tools

- E.g., search a conversation for messages matching a keyword

## [P2] End-to-end encrypted messages