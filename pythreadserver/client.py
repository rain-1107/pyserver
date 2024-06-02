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

        self._recv_listeners = []
        self._connection_listeners = []
        self._disconnect_listeners = []
        self.packets = []
        self.log = Log(output_to_console, log_path)
        self.socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.send_loop_thread = None
        self.recv_loop_thread = None
        self.connected = False
        self.runtime = time.time()

    def connect(self, ip):
        if ip == "localhost":
            ip = socket.gethostname()
        self.log.log("Connecting to server...")
        while True:
            try:
                self.socket.connect((ip, PORT))
                break
            except ConnectionRefusedError:
                self.log.log("Error: Connection refused")
                return 1
            except OSError:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.log.log("Connected to server.")
        self.connected = True
        self.log.log("Initialising handling threads...")
        self.send_loop_thread = threading.Thread(target=self.send_loop)
        self.send_loop_thread.start()
        self.recv_loop_thread = threading.Thread(target=self.recv_loop)
        self.recv_loop_thread.start()
        self.log.log("Done.")
        for func in self._connection_listeners:
            try:
                func()
            except Exception as err:
                self.log.log(f"{err}\nError occurred in event handler: {func}")
        return 0

    def send_loop(self):
        while self.connected:
            try:
                for packet in self.packets:
                    self.socket.send(packet)
                    self.packets = []
            except (ConnectionResetError, ConnectionAbortedError):
                self.close()
                break

    def recv_loop(self):
        while self.connected:
            try:
                data = self.socket.recv(BUFFER_SIZE)
                if data == b'':
                    self.close()
                    return
                for func in self._recv_listeners:
                    try:
                        func(data)
                    except Exception as err:
                        self.log.log(f"{err}\nError occurred in event handler: {func}")
            except (ConnectionResetError, ConnectionAbortedError):
                self.close()
                break

    def send(self, data: bytes):
        self.packets.append(data)

    def close(self):
        if not self.connected:
            return
        self.log.log("Closing connection...")
        self.connected = False
        self.socket.close()
        self.log.log("Connection closed.")
        for func in self._disconnect_listeners:
            try:
                func()
            except Exception as err:
                self.log.log(f"{err}\nError occurred in event handler: {func}")
        self.log.close()


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
        self._connection_listeners.remove(func)

    @property
    def on_connect(self):
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
 
    def remove_disconnection_listener(self, func):
        if func not in self._disconnect_listeners:
            return
        self._disconnect_listeners.remove(func)
  
