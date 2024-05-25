from pythreadserver import server
s = server.Server()


@s.on_connection
def connection(client: server.ServerClient):
    print("Hello",client.addr)


@s.on_receive
def handle(client: server.ServerClient, data: bytes):
    s.sendall(data)


s.run()
