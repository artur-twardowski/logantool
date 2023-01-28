from threading import Lock, Thread
import ConsoleUI.Backend.ANSI as CL
from time import sleep

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

class Screen:
    def __init__(self):
        self.width = None
        self.height = None

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
        screen_obj.create_widgets()

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

