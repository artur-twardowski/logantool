from ConsoleUI.TextBox import TextBox
import ConsoleUI.Backend.ANSI as CL
from sys import stdout
from ConsoleUI.ScreenManager import Screen
from LogAggregate import LogAggregate

class MainScreen(Screen):
    def __init__(self):
        super().__init__()

        self.window_content = [] 
        self._keys = ""
        self._redraw_interface = True
        self._redraw_log_windows = True

    def create_widgets(self):
        self.w_textbox = TextBox((0, 0), (self.width, int(self.height/2)))

    def bind_log_aggregate(self, aggr: LogAggregate):
        self.w_textbox.set_content(aggr.get_unfiltered_stream())

    def draw(self, complete_redraw=True):
        row_hsplit = int(self.height/2)
        col_vsplit = self.width - 40
        # Upper window

        if self._redraw_interface:
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

            self._redraw_interface = False
        
        if self._redraw_log_windows:
            self.w_textbox.render()
            self._redraw_log_windows = False

            
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
            self._redraw_log_windows = True
        elif key == 'k':
            self.w_textbox.top_line -= 1
            self._redraw_log_windows = True

    def on_new_lines(self):
        self.w_textbox.update()
        self.w_textbox.scroll_to_bottom()

        self._redraw_log_windows = True


