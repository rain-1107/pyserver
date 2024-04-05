import pythreadserver

server = pythreadserver.server.Server(True)


@server.on_receive
def handle(client, data):
    server.sendall(data)


server.run()
