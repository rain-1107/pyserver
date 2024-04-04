import pyserver

server = pyserver.server.Server()


@server.on_receive
def handle(client, data):
    # Echoes data back to the client
    client.send(data)


server.run()
