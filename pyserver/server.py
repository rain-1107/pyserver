import threading
import socket
import math
import time
from .constants import *
from .textlog import Log


class ClientObject:
    def __init__(self, sock_from, sock_to, addr):
        self.addr = addr
        self.socket_to = sock_to
        self.socket_from = sock_from
        self.connected = True
        self.packets = []
        self.send_loop_thread = None
        self.recv_loop_thread = None

    def run(self, server):
        self.send_loop_thread = threading.Thread(target=self.send_loop, args=(server,))
        self.send_loop_thread.start()
        self.recv_loop_thread = threading.Thread(target=self.recv_loop, args=(server,))
        self.recv_loop_thread.start()

    def send_loop(self, server):
        while self.connected:
            init = time.time()
            server.client_send(self)
            dt = time.time() - init
            if (1/server.tick_rate) - dt > 0:
                time.sleep((1/server.tick_rate) - dt)

    def recv_loop(self, server):
        while self.connected:
            server.client_receive(self)

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
        self.socket_in.listen()
        self.socket_out.listen()
        while self.running:
            client_from, addr_from = self.socket_in.accept()
            client_to, addr_to = self.socket_out.accept()
            self.log.log(f"Handling connection from {addr_from}")
            if addr_from[0] == addr_to[0]:
                client = ClientObject(sock_from=client_from, sock_to=client_to, addr=addr_to)
                client.run(self)

    def client_send(self, client: ClientObject):
        for packet in client.packets:
            client.socket_to.send(packet)
        client.packets = []

    def client_receive(self, client: ClientObject):
        data = client.socket_from.recv(BUFFER_SIZE)
        for func in self.__listeners:
            func(client, data)

    def sendall(self, data: bytes):
        for client in self.clients:
            client.send(data)

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