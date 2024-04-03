import threading
import socket

import pyserver.server
import pyserver.client
import pyserver.data

# The amount of data that can be transferred
PACKET_SIZE: int = 512

# ...
PORT_C_TO_S: int = 30000
PORT_S_TO_x: int = 40000
