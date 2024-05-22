import pythreadserver
import time

client = pythreadserver.client.Client()


@client.on_receive
def handle(data):
    print(data.decode("utf-8"))


client.connect("localhost")

while client.connected:
    text = input("Input: ")
    if text == "exit":
        client.close()
    else:
        client.send(text.encode("utf-8"))
        time.sleep(1)
