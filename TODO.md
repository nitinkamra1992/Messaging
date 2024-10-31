# Messaging TODOs

## Build unique message IDs in format {sdr.rcpt.uuid}

## Build login manager

- Need to support managing of online/offline users
- Show online/offline symbol on client frontend
- Needs to track user "last active" and auto-logout after ~15 mins of inactivity

## Make separate send/receive processes for client as well as server

- For server, might also need send and receive queues associated with each process

## Build conversation graph for all conversations

- Design a conversation graph data structure for conversations
- Support contacts (with server being default contact for everyone)
- Server must store the full conversation graph, while client must only have their own node and all attached nodes
- Contact addition/deletion must update both server and client graphs
- Server must log all messages in this data structure

## Peer-to-peer chat in backend

- Support peer-to-peer type messages in backend
- Must support user-to-server message with AI responses and also user-self-messaging
- Need to store messages for offline users
- Need to support pushing all offline messages on user login

## Introduce command mode for frontend

- Allow basic commands like :exit, :logout, :chat <username>, :adduser <username>, :deluser <username> etc.
- Revise current client frontend to support peer-to-peer chat and add relevant commands

## Chat histories

- Support chat histories for all conversations on client frontend and server backend using conversation graph
- Add chat history to AI response from server

## [P1] Add persistent login for frontend, until manually logged out

## [P1] Add a flask UI for frontend

## [P1] Add convenient commands and tools

- E.g., search a conversation for messages matching a keyword

## [P2] End-to-end encrypted messages