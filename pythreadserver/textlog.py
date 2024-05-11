class Log:
    def __init__(self, write_to_console=True, filename="pyserver/log/log.txt"):
        self.write_to_console = write_to_console
        self.text = ""
        self.filename = filename

    def log(self, text):
        if self.write_to_console:
            print(text)
        self.text += text + "\n"

    def close(self):
        try:
            file = open(self.filename, "w")
            file.write(self.text)
            file.close()
        except OSError:
            self.log("Error saving log file")
        self.text = ""