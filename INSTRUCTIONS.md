# Setup

Set up client on your local machine and server on your devserver.

1. Run `python server.py` on devserver.
2. Set up port forwarding on your local machine so it can talk to the devserver.
```
ssh -L 9999:localhost:10000 -Nf nitinkamra@devserver
```
3. Start client on local machine: `python client.py` in a different terminal.