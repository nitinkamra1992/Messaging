# Messaging TODOs

## [Done] Accomodate arbitrary length receive_message

## Make separate send/receive processes for client as well as server

- For server, might also need send and receive queues associated with each process

## Build server logs for all messages

## Build unique message IDs: local (per user) and global (for server)

## Support contacts

- Support contacts (with server being default contact for everyone)

## Support peer-to-peer messages

- Need to also add support for storing online/offline users
- Need to store messages for offline users
- Need to support pushing all offline messages on user login

## Introduce command mode for client (e.g., :exit, :logout)

## Add persistent login for client, until manually logged out

## Add a flask UI for client

## Support chat histories for all conversations

## [P2] End-to-end encrypted messages