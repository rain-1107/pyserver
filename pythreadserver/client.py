import socket
import threading
import time
from .textlog import Log
from .constants import *


class Client:
    def __init__(self, **kwargs):
        output_to_console = True
        log_path = ""
        if "console" in kwargs:
            output_to_console = kwargs["console"]
        if "log_path" in kwargs:
            log_path = kwargs["log_path"]

        self.__listeners = []
        self.packets = []
        self.log = Log(output_to_console, log_path)
        self.socket_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.send_loop_thread = None
        self.recv_loop_thread = None
        self.connected = False

        self.runtime = time.time()

    def connect(self, ip):
        if ip == "localhost":
            ip = socket.gethostname()
        self.log.log("Connecting to server...")
        try:
            self.socket_in.connect((ip, PORT_S_TO_C))
            self.socket_out.connect((ip, PORT_C_TO_S))
        except ConnectionRefusedError:
            self.log.log("Error: Connection refused")
            return 1
        self.log.log("Connected to server.")
        self.connected = True
        self.log.log("Initialising handling threads...")
        self.send_loop_thread = threading.Thread(target=self.send_loop)
        self.send_loop_thread.start()
        self.recv_loop_thread = threading.Thread(target=self.recv_loop)
        self.recv_loop_thread.start()
        self.log.log("Done.")
        return 0

    def send_loop(self):
        while self.connected:
            try:
                self.send_server()
            except (ConnectionResetError, socket.SO_ERROR):
                self.connected = False
                break

    def recv_loop(self):
        while self.connected:
            try:
                self.recv_server()
            except (ConnectionResetError, ConnectionAbortedError):
                self.close()
                break

    def send_server(self):
        for packet in self.packets:
            self.socket_out.send(packet)
        self.packets = []

    def recv_server(self):
        data = self.socket_in.recv(BUFFER_SIZE)
        if data == b'':
            self.close()
            return
        for func in self.__listeners:
            try:
                func(data)
            except:
                self.log.log(f"Error occurred in event handler: {func}")

    def send(self, data: bytes):
        self.packets.append(data)

    def close(self):
        if not self.connected:
            return
        self.log.log("Closing connection...")
        self.connected = False
        self.socket_in.close()
        self.socket_out.close()
        self.log.log("Connection closed.")
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
