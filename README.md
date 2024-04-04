# About
pyserver is a python socket-based multi-threaded server package designed for simple server systems with event based handling calls.
---
# Documentation
# [client.py](/pyserver/client.py)

## class Client(ip: str, output_to_console: bool = False)
### *Functions*
#### def run()
- Attempts connection with server at IP specified in constructor
- This function is non-blocking
> returns ``0`` if connection is successful
> 
> returns ``1``if connection is refused
#### def send(data: bytes)
 - Adds ``data`` to the queue
> ``data`` should be bytes types or it will not be sent
> 
> returns `None`
#### def close()
- Closes connection with server and closes connection
- Log is outputted to `pyserver/log/clientlog.txt`
> returns `None`

#### @on_receive
- Decorator to signal function to be event handler for when client receive data from the server
```py
@client.on_receive
def handle(data: bytes):
	# Handler code here
```

# [server.py](/pyserver/server.py)
## class Server(output_to_console: bool = False)
#### def run()
- Starts listening for connections and handles incoming connections
- This function is blocking
> returns `None`
#### def sendall(data: bytes)
- Queues `data` to be sent to all clients
> If `data` is not a bytes object it will not be sent
> 
> returns `None`
 #### def close()
 - Disconnects all clients and closes the server
 - Log is outputted to `pyserver/log/serverlog.txt`
 > returns `None`
 #### @on_receive
- Decorator to signal function to be event handler for when the server receives data from a client
```py
@server.on_receive
def handle(client: ServerClient, data: bytes):
	# Handler code here
```

## class ServerClient(parent: Server, sock_from, sock_to, addr)
- ServerClient objects should not be created but will be given as a parameter in [server event call](README.md#on_receive-1)
#### def send(data: bytes)
- Queues `data` to be sent to client as a packet
> If `data` is not a bytes object it will not be sent
> 
> returns `None`
 #### def close()
 - Will disconnect the client from the server and remove all references of the client
 > returns `None`
# [textlog.py](/pyserver/textlog.py)
- Utility file for logging console to file
## class Log(write_to_console: bool, filename: str)
#### def log(text: str)
- Stores text to log
- Prints text if write_to_console is `True`
> returns `None`
#### def close()
- Opens the file with `filename` and writes log to it
> This clears the log but each call writes over contents of the file
>
> returns `None`
# [constants.py](/pyserver/constants.py)
- This file only holds constants that are used within the package classes

|name|description  |
|--|--|
|BUFFER_SIZE | Max number of bytes received each tick  |
| PORT_C_TO_S | Default port for network path from client to server |
| PORT_S_TO_C | Default port for network path from server to client |
| DEFAULT_TICK_RATE | Default number of ticks per second (Hz) |

