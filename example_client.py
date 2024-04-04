import pyserver
import time
client = pyserver.client.Client("localhost")


@client.on_receive
def handle(data):
    print(data.decode("utf-8"))


client.run()

while client.connected:
    text = input("Input: ")
    client.send(text.encode("utf-8"))
