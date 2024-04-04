class Log:
    def __init__(self, write_to_console=True, filename="pyserver/log/log.txt"):
        self.write_to_console = write_to_console
        self.file = open(filename, "w")

    def log(self, text):
        if self.write_to_console:
            print(text)
        self.file.write(text+"\n")
