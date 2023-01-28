from time import sleep

class LogSource:
    def __init__(self, filename):
        self.file = open(filename, "r")

    def read(self):
        while True:
            line = self.file.readline()
            line_sanitized = ""
            for ch in line:
                if ch >= ' ':
                    line_sanitized += ch
                elif ch == '\t':
                    line_sanitized += " "
                    while len(line_sanitized) % 4 != 0:
                        line_sanitized += " "
                elif ch == '\n':
                    pass
                else:
                    line_sanitized += "<%d>" % ord(ch)

            return line_sanitized

    def __del__(self):
        self.file.close()

