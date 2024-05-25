from pythreadserver import client
import time

c= client.Client()


@c.on_receive
def handle(data):
    print(data.decode("utf-8"))


@c.on_disconnect
def handle_disc():
    c.connect("localhost")

c.connect("localhost")

while c.connected:
    text = input("Input: ")
    if text == "exit":
        c.close()
    else:
        c.send(text.encode("utf-8"))
        time.sleep(1)
