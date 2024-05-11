import threading
import socket
import time
from .constants import *
from .textlog import Log


class ServerClient:
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
            try:
                self.server.client_send(self)
            except ConnectionResetError:
                self.connected = False
                self.close()
                break

    def recv_loop(self):
        while self.connected:
            try:
                self.server.client_receive(self)
            except ConnectionResetError:
                self.connected = False
                self.close()
                break

    def close(self):
        if not self.connected:
            return
        self.connected = False
        if self in self.server.clients:
            self.server.clients.remove(self)
            self.socket_from.close()
            self.socket_to.close()
            self.server.log.log(f"Connection from {self.addr[0]} closed.")

    def send(self, data):
        self.packets.append(data)


class Server:
    def __init__(self, **kwargs):
        output_to_console = True
        log_path = ""
        if "console" in kwargs:
            output_to_console = kwargs["console"]
        if "log_path" in kwargs:
            log_path = kwargs["log_path"]

        self.running = True
        self.runtime = time.time()
        self.clients = []
        self.threads = []
        self.__listeners = []
        self.log = Log(output_to_console, log_path)

        self.socket_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = ""
        self.log.log("Binding sockets to ports...")
        self.socket_in.bind((host, PORT_C_TO_S))
        self.socket_out.bind((host, PORT_S_TO_C))
        self.log.log("Done.")

    def run(self):
        threading.Thread(target=self.input_check).start()
        self.log.log(f"Listening to connections...")
        try:
            self.socket_in.listen()
            self.socket_out.listen()
            while self.running:
                client_from, addr_from = self.socket_in.accept()
                client_to, addr_to = self.socket_out.accept()
                self.log.log(f"Handling connection from {addr_from[0]}.")
                if addr_from[0] == addr_to[0]:
                    client = ServerClient(self, sock_from=client_from, sock_to=client_to, addr=addr_to)
                    self.clients.append(client)
                    client.run()
        except OSError:
            self.log.log("Sockets closed.")

    def client_send(self, client: ServerClient):
        try:
            for packet in client.packets:
                client.socket_to.send(packet)
            client.packets = []
        except OSError:
            client.close()
            return

    def client_receive(self, client: ServerClient):
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

    def get_clients(self):
        return self.clients.copy()

    def close(self):
        self.running = False
        for client in self.clients.copy():
            client.close()
        self.socket_in.close()
        self.socket_out.close()
        self.log.log("Server closed.")
        self.log.close()

    def input_check(self):
        while self.running:
            string = input("")
            if string.lower() == "exit":
                self.close()
                break

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
