import threading
import socket
import time
from .constants import *
from .textlog import Log


class ServerClient:
    def __init__(self, parent, socket, addr):
        self.server = parent
        self.addr = addr
        self.socket = socket
        self.connected = True
        self.packets = []
        self.send_loop_thread = None
        self.recv_loop_thread = None

    def run(self):
        self.send_loop_thread = threading.Thread(target=self.send_loop)
        self.send_loop_thread.start()
        self.recv_loop_thread = threading.Thread(target=self.recv_loop)
        self.recv_loop_thread.start()

    def send_loop(self):
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
            self.socket.close()
            self.server.log.log(f"Connection from {self.addr[0]} closed.")
        for func in self.server._disconnect_listeners:
            try:
                func(self)
            except:
                self.server.log.log(f"Error occurred during event handler: {func}")


    def send(self, data):
        self.packets.append(data)


class Server:
    def __init__(self, **kwargs):
        output_to_console = True
        log_path = ""
        self.port = PORT
        if "console" in kwargs:
            output_to_console = kwargs["console"]
        if "log_path" in kwargs:
            log_path = kwargs["log_path"]
        if "port" in kwargs:
            self.port = kwargs["port"]
        self.running = True
        self.runtime = time.time()
        self.clients = []
        self.threads = []
        self._recv_listeners = []
        self._connection_listeners = []
        self._disconnect_listeners = []
        self.log = Log(output_to_console, log_path)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = ""
        self.log.log("Binding sockets to ports...")
        self.socket.bind((host, PORT))
        self.log.log("Done.")

    def run(self):
        threading.Thread(target=self.input_check).start()
        self.log.log(f"Listening to connections...")
        try:
            self.socket.listen()
            while self.running:
                client, addr = self.socket.accept()
                self.log.log(f"Handling connection from {addr[0]}.")
                client = ServerClient(self, socket=client, addr=addr)
                self.clients.append(client)
                for func in self._connection_listeners:
                    try:
                        func(client)
                    except: 
                        self.log.log(f"Error occured in event handler: {func}")
                client.run()
        except OSError:
            self.log.log("Sockets closed.")

    def client_send(self, client: ServerClient):
        try:
            for packet in client.packets:
                client.socket.send(packet)
            client.packets = []
        except OSError:
            client.close()
            return

    def client_receive(self, client: ServerClient):
        try:
            data = client.socket.recv(BUFFER_SIZE)
        except OSError:
            client.close()
            return
        if data == b'':
            client.close()
            return
        for func in self._recv_listeners:
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
        self.socket.close()
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
            if func not in self._recv_listeners:
                self._recv_listeners.append(func)
            return func
        return wrapper

    def remove_recv_listener(self, func):
        if func not in self._recv_listeners:
            return
        self._recv_listeners.remove(func)

    @property
    def on_connection(self):
        def wrapper(func):
            if func not in self._connection_listeners:
                self._connection_listeners.append(func)
            return func
        return wrapper

    def remove_connection_listener(self, func):
        if func not in self._connection_listeners:
            return
        self._connection_listeners.remove(func)

    @property
    def on_disconnect(self):
        def wrapper(func):
            if func not in self._disconnect_listeners:
                self._disconnect_listeners.append(func)
            return func
        return wrapper

    def remove_disconnect_listener(self, func):
        if func not in self._disconnect_listeners:
            return
        self._disconnect_listeners.remove(func)
