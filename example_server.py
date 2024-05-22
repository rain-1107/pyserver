import pythreadserver

server = pythreadserver.server.Server()

@server.on_connection
def connection(client):
    print("Hello",client)

@server.on_receive
def handle(client, data):
    server.sendall(data)


server.run()
