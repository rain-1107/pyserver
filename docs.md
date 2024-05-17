# Documentation
# [client.py](pythreadserver/client.py)

## class Client(**kwargs)
### *Parameters*
```py
console: bool = True  # If true will output log messages to console
log_path: str = ""  # Path to save log text file. Leave empty for no saving.
```
### *Functions*
#### def connect(ip: str)
- Attempts connection with server at IP passed in function
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
- Log is outputted to `log_path`
> returns `None`

#### @on_receive
- Decorator to signal function to be event handler for when client receive data from the server
```py
@client.on_receive
def handle(data: bytes):
	# Handler code here
```

# [server.py](pythreadserver/server.py)
## class Server(output_to_console: bool = False)
### *Parameters*
```py
console: bool = True  # If true will output log messages to console
log_path: str = ""  # Path to save log text file. Leave empty for no saving.
```
### *Attributes*
#### clients
- `clients` is an array of `ServerClient` objects that are currently connected
### *Functions*
#### def run()
- Starts listening for connections and handles incoming connections
- This function is blocking
> returns `None`
#### def sendall(data: bytes)
- Queues `data` to be sent to all clients
> If `data` is not a bytes object it will not be sent
> 
> returns `None`
#### def get_clients()
- Returns a copy of the `clients` array
> returns `None`
 #### def close()
 - Disconnects all clients and closes the server
 - Log is outputted to `log_path`
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
# [textlog.py](pythreadserver/textlog.py)
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
# [constants.py](pythreadserver/constants.py)
- This file only holds constants that are used within the package classes

|name|description  |
|--|--|
|BUFFER_SIZE | Max number of bytes received each tick  |
| PORT_C_TO_S | Default port for network path from client to server |
| PORT_S_TO_C | Default port for network path from server to client |
