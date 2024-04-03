import threading


class ClientObject:
    def __init__(self, c, addr):
        self.c = c
        self.addr = addr
        self.loops = []
        self.connected = True


class Server:
    def __init__(self):
        # bind to ports
        # connect to client through to ports

        # create loop for sending
        # create loop for receiving
        pass

    def run(self):
        def do_connection_stuff():
            pass

        threading.Thread(target=do_connection_stuff).run()
        pass

    def send_loop(self, client: ClientObject):
        pass

    def recv_loop(self, client: ClientObject):
        pass

    def send(self):
        pass

    def get(self):
        pass