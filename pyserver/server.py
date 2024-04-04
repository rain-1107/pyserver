import threading
import socket
import time
from .constants import *
from .textlog import Log


class ClientObject:
    def __init__(self, parent, sock_from, sock_to, addr):
        self.server = parent
        self.addr = addr
        self.socket_to = sock_to
        self.socket_from = sock_from
        self.connected = True
        self.packets = []
        self.send_loop_thread = None
        self.recv_loop_thread = None

    def run(self):
        self.send_loop_thread = threading.Thread(target=self.send_loop)
        self.send_loop_thread.start()
        self.recv_loop_thread = threading.Thread(target=self.recv_loop)
        self.recv_loop_thread.start()

    def send_loop(self,):
        while self.connected:
            init = time.time()
            try:
                self.server.client_send(self)
            except ConnectionResetError:
                self.connected = False
                self.close()
                break
            dt = time.time() - init
            if (1/self.server.tick_rate) - dt > 0:
                time.sleep((1/self.server.tick_rate) - dt)

    def recv_loop(self):
        while self.connected:
            try:
                self.server.client_receive(self)
            except ConnectionResetError:
                self.connected = False
                self.close()
                break

    def close(self):
        if self in self.server.clients:
            self.socket_from.close()
            self.socket_to.close()
            self.server.log.log(f"{self.addr} disconnected")
            self.server.clients.remove(self)

    def send(self, data):
        self.packets.append(data)


class Server:
    def __init__(self):
        self.running = True
        self.runtime = time.time()
        self.clients = []
        self.threads = []
        self.__listeners = []
        self.tick_rate = DEFAULT_TICK_RATE
        self.log = Log(True, "pyserver/log/serverlog.txt")

        self.socket_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = ""
        self.log.log("Binding sockets to ports...")
        self.socket_in.bind((host, PORT_C_TO_S))
        self.socket_out.bind((host, PORT_S_TO_C))
        self.log.log("Done")

    def run(self):
        self.log.log(f"Listening to connections...")
        try:
            self.socket_in.listen()
            self.socket_out.listen()
            while self.running:
                client_from, addr_from = self.socket_in.accept()
                client_to, addr_to = self.socket_out.accept()
                self.log.log(f"Handling connection from {addr_from}")
                if addr_from[0] == addr_to[0]:
                    client = ClientObject(self, sock_from=client_from, sock_to=client_to, addr=addr_to)
                    self.clients.append(client)
                    client.run()
        except OSError:
            self.log.log("Sockets closed")

    def client_send(self, client: ClientObject):
        try:
            for packet in client.packets:
                client.socket_to.send(packet)
            client.packets = []
        except OSError:
            client.close()
            return

    def client_receive(self, client: ClientObject):
        try:
            data = client.socket_from.recv(BUFFER_SIZE)
        except OSError:
            client.close()
            return
        if data == b'':
            client.close()
            return
        for func in self.__listeners:
            try:
                func(client, data)
            except:
                self.log.log(f"Error occurred in event handler: {func}")

    def sendall(self, data: bytes):
        for client in self.clients:
            client.send(data)

    def close(self):
        self.running = False
        for client in self.clients.copy():
            client.connected = False
            client.close()
        self.socket_in.close()
        self.socket_out.close()
        self.log.log("Server closed")
        self.log.close()

    @property
    def on_receive(self):
        def wrapper(func):
            self.add_listener(func)
            return func
        return wrapper

    def add_listener(self, func):
        if func in self.__listeners:
            return
        self.__listeners.append(func)

    def remove_listener(self, func):
        if func not in self.__listeners:
            return
        self.__listeners.remove(func)