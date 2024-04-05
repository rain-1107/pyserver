import socket
import threading
import time
from .textlog import Log
from .constants import *


class Client:
    def __init__(self, ip, output_to_console=False):
        self.ip = ip
        if self.ip == "" or self.ip == "localhost":
            self.ip = socket.gethostname()
        self.runtime = time.time()
        self.__listeners = []
        self.packets = []
        self.tick_rate = DEFAULT_TICK_RATE
        self.log = Log(output_to_console, "pyserver/log/clientlog.txt")
        self.socket_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.send_loop_thread = None
        self.recv_loop_thread = None
        self.connected = False

    def connect(self):
        self.log.log("Connecting to server...")
        try:
            self.socket_in.connect((self.ip, PORT_S_TO_C))
            self.socket_out.connect((self.ip, PORT_C_TO_S))
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
            loop_time = time.time()
            try:
                self.send_server()
            except (ConnectionResetError, socket.SO_ERROR):
                self.connected = False
                break
            dt = time.time() - loop_time
            if (1/self.tick_rate) - dt > 0:
                time.sleep((1 / self.tick_rate) - dt)

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
