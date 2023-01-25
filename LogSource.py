from time import sleep

class LogSource:
    def __init__(self, filename):
        self.file = fopen(filename, "r")

    def read(self):
        while True:
            line = self.file.read()

            if not line:
                sleep(0.1)
                continue

            yield line

    def __del__(self):
        self.file.close()

