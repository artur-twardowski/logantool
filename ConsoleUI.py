import ConsoleLowLevel as CL
from sys import stdout, stdin
from threading import Thread
from threading import Lock
from time import sleep
from random import randint

class _TextBoxCacheEntry:
    def __init__(self, line, **metadata):
        self.line = line
        self.line_number = metadata.get("line_number")
        self.source = metadata.get("source")

class TextBox:

    def __init__(self, position, dimensions, content):
        self.left, self.top = position
        self.width, self.height = dimensions
        self._client_width = self.width - 6
        self._content = content
        self.top_line = 3
        self.first_column = 0
        self.wrap_lines = True

        self._update_content_cache_full()

    def _append_to_content_cache(self, line, line_no, source):
        if self.wrap_lines:
            line_length = CL.strlen(line)
            line_offset = 0

            while line_length > 0:
                line_part = CL.substr(line, line_offset, self._client_width)
                self._content_cache.append(_TextBoxCacheEntry(line_part, line_number=line_no, source=source))
                line_length -= self._client_width
                line_offset += self._client_width
        else:
            self._content_cache.append(_TextBoxCacheEntry(line, line_number=line_no, source=source))

    def _update_content_cache_full(self):
        self._content_cache = []
        ix = 1
        for line in self._content:
            self._append_to_content_cache(line, ix, None)
            ix += 1

    def scroll_to_bottom(self):
        self.top_line = len(self._content_cache) - self.height
        if self.top_line < 0:
            self.top_line = 0

    def update(self):
        self._update_content_cache_full()

    def render(self):
        bg_color = 0
        fg_color = 15

        prev_line_no = 0
        for wnd_line_ix in range(0, self.height):
            line_ix = wnd_line_ix + self.top_line
            if line_ix < len(self._content_cache):
                line, line_len = CL.substr_ex(self._content_cache[line_ix].line, 0, self._client_width)
                line += " " * (self._client_width - line_len)

                line_no = self._content_cache[line_ix].line_number

                CL.set_text_bg(bg_color)

                if prev_line_no == line_no:
                    CL.write_at((self.left, self.top + wnd_line_ix), "      ")
                else:
                    CL.set_text_fg(1)
                    CL.write_at((self.left, self.top + wnd_line_ix), "%5d " % line_no)

                CL.set_text_fg(fg_color)
                CL.write(line)

                prev_line_no = line_no
            else:
                CL.write_at((self.left, self.top + wnd_line_ix), " " * self._client_width)


class Screen:
    def __init__(self):
        self.width = None
        self.height = None

class MainScreen(Screen):
    def __init__(self):
        super().__init__()

        self.window_content = [] 
        self._keys = ""

    def update(self):
        self.w_textbox = TextBox((0, 0), (self.width, int(self.height/2)), self.window_content)

    def draw(self, complete_redraw=True):
        row_hsplit = int(self.height/2)
        col_vsplit = self.width - 40
        # Upper window

        self.w_textbox.render()

        # Horizontal split
        CL.set_text_bg(8)
        CL.set_text_fg(15)
        CL.cursor_abs(0, row_hsplit)
        stdout.write("\u2550" * (self.width))

        # Vertical split
        CL.write_at((col_vsplit, row_hsplit), "\u2566")
        CL.write_at((0, row_hsplit), "\u2554")
        CL.write_at((self.width, row_hsplit), "\u2557")
        for row in range(row_hsplit + 1, self.height - 2):
            CL.set_text_bg(8)
            CL.set_text_fg(15)
            CL.write_at((0, row), "\u2551")
            CL.write_at((col_vsplit, row), "\u2551")
            CL.clear_eol()
            CL.write_at((self.width, row), "\u2551")

            CL.set_text_bg(0)
            CL.set_text_fg(1)
            CL.write_at((col_vsplit + 2, row), "[A]")
            CL.set_text_fg(15)
            CL.write_at((col_vsplit + 6, row)," " * 32)

        
        # Bottom line
        CL.set_text_bg(8)
        CL.set_text_fg(15)
        CL.cursor_abs(0, self.height - 2)
        stdout.write("\u2550" * (self.width))
        CL.write_at((0, self.height - 2), "\u255A")
        CL.write_at((self.width, self.height - 2), "\u255D")
        
        CL.set_text_bg(0)
        CL.set_text_fg(12)
        CL.write_at((0, self.height-1), "> %s" % self._keys)
        stdout.flush()

    def handle_key(self, key):
        KEYMAP = {}
        for k in range(33, 127):
            KEYMAP[k] = chr(k)
        KEYMAP[27] = "<ESC>"

        if ord(key) in KEYMAP:
            self._keys += KEYMAP[ord(key)]
        else:
            self._keys += "<%d>" % ord(key)

        if ord(key) == 127:
            self._keys = ""

        if key == 'j':
            self.w_textbox.top_line += 1
        elif key == 'k':
            self.w_textbox.top_line -= 1

    def notify_new_lines_in_log(self):
        self.w_textbox.update()
        self.w_textbox.scroll_to_bottom()

class RingBuffer:
    def __init__(self, size):
        self._contents = [None] * size
        self._size = size
        self._read_index = 0
        self._write_index = 0
        self._access_lock = Lock()

    def push(self, obj) -> bool:
        self._access_lock.acquire()
        if self._contents[self._write_index] is None:
            self._contents[self._write_index] = obj
            self._write_index += 1
            if self._write_index == self._size:
                self._write_index = 0
            self._access_lock.release()
            return True
        else:
            return False

    def pop(self):
        self._access_lock.acquire()
        result = self._contents[self._read_index] 

        if result is not None:
            self._contents[self._read_index] = None
            self._read_index += 1
            if self._read_index == self._size:
                self._read_index = 0

        self._access_lock.release()
        return result


class ScreenManager:
    def __init__(self):
        self._original_settings = CL.enable_raw_input()
        self.width, self.height = CL.get_terminal_dimensions()
        self.screens = {}
        self._key_buffer = RingBuffer(1024)
        CL.save_screen()
        CL.clear_screen()

        self._termination_requested = False

    def __del__(self):
        CL.restore_screen()
        CL.disable_raw_input(self._original_settings)

    def add_screen(self, screen_name, screen_obj: Screen):
        screen_obj.width = self.width
        screen_obj.height = self.height
        self.screens[screen_name] = screen_obj
        screen_obj.update()

    def set_active(self, screen_name: str):
        self._active_screen = screen_name

    def _key_events_worker(self):
        while not self._termination_requested:
            key = CL.readkey()

            self._key_buffer.push(key)

            if key == 'x':
                self._termination_requested = True


    def run(self):
        keyboard_thread = Thread(target=self._key_events_worker)
        keyboard_thread.start()
        while not self._termination_requested:
            active_screen = self.screens[self._active_screen]
            active_screen.draw()

            sleep(0.01)
            
            key = self._key_buffer.pop()
            if key is not None:
                active_screen.handle_key(key)

        keyboard_thread.join()

def fill_worker(main_screen: MainScreen):
    TOKENS = [chr(x) for x in range(32, 126)]
    for _ in range(0, 1000):
        count = randint(80, 350)
        content = ""
        for _2 in range(0, count):
            content += TOKENS[randint(0, len(TOKENS) - 1)]

        main_screen.window_content.append(content)
        if _ % 50 == 49:
            main_screen.notify_new_lines_in_log()
        sleep(0.01)

if __name__ == "__main__":
    mgr = ScreenManager()
    main = MainScreen()
    mgr.add_screen("main", main)
    mgr.set_active("main")
    
    filling_thread = Thread(target=fill_worker, args=(main,))
    filling_thread.start()
    mgr.run()

    filling_thread.join()
    

