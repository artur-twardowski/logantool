import ConsoleUI.Backend.ANSI as CL


class _TextBoxCacheEntry:
    def __init__(self, line, **metadata):
        self.line = line
        self.line_number = metadata.get("line_number")
        self.source = metadata.get("source")


class TextBox:
    def __init__(self, position, dimensions):
        self.left, self.top = position
        self.width, self.height = dimensions
        self._client_width = self.width - 6
        self._content = []
        self.top_line = 0
        self.first_column = 0
        self.wrap_lines = True

    def set_content(self, content):
        self._content = content
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
                CL.write_at((self.left, self.top + wnd_line_ix), " " * self.width)

