from sys import stdout, stdin
import tty
import termios


def _esc(sequences: list):
    for seq in sequences:
        stdout.write("\x1b[%s" % seq)


def enable_raw_input():
    fd = stdin.fileno()
    return termios.tcgetattr(fd)


def disable_raw_input(old_settings):
    fd = stdin.fileno()
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def readkey():
    tty.setraw(stdin.fileno())
    ch = stdin.read(1)
    return ch[0]


def clear_screen():
    _esc(["H", "2J"])


def clear_eol():
    _esc(["0K"])


def clear_line():
    _esc(["H", "0K"])


def cursor_abs(x, y):
    _esc(["%d;%dH" % (y+1, x+1)])


def cursor_rel(dx, dy):
    if dx > 0:
        _esc(["%dC" % dx])
    elif dx < 0:
        _esc(["%dD" % (-dx)])

    if dy > 0:
        _esc(["%dB" % dy])
    elif dy < 0:
        _esc(["%dA" % (-dy)])


def save_screen():
    _esc("?47h")


def restore_screen():
    _esc("?47l")


def get_terminal_dimensions():
    fmt_text = ""
    _esc(["s", "999;999H", "6n"])
    stdout.flush()
    while True:
        ch = readkey()
        if (ch >= '0' and ch <= '9') or ch == ';':
            fmt_text += ch
        if ch == "R": break
    _esc(["u"])
    lines_s, cols_s = fmt_text.split(';')

    return (int(cols_s), int(lines_s))


def set_text_fg(color):
    _esc(["38;5;%dm" % color])


def set_text_bg(color):
    _esc(["48;5;%dm" % color])


def write(s):
    stdout.write(s)


def write_at(position, s):
    cursor_abs(position[0], position[1])
    write(s)


def strlen(s: str):
    return len(s)


def substr_ex(s: str, offset: int, length):
    result = ""

    ix = 0
    displayable_chars_written = 0
    for ch in s:
        if ix >= offset and displayable_chars_written < length:
            result += ch
            displayable_chars_written += 1

        ix += 1

    return result, displayable_chars_written


def substr(s: str, offset: int, length):
    return substr_ex(s, offset, length)[0]
