from LogSource import LogSource
from threading import Thread
from time import sleep

class LogAggregate:
    def __init__(self, view):
        self._sources = {}
        self.view = view

        self._all_lines = []

    def get_unfiltered_stream(self):
        return self._all_lines

    def add_source(self, name, source: LogSource):
        self._sources[name] = source

    def poll(self):
        new_logs = False

        for source_name, source in self._sources.items():
            while True:
                line = source.read()
                if not line: break
                new_logs = True
                self._all_lines.append(line)

        if new_logs:
            self.view.on_new_lines()

class LogAggregateThread:
    def __init__(self, aggr: LogAggregate):
        self._aggr = aggr
        self._running = False
        self._paused = False
        self._thread = Thread(target=self._worker)

    def _worker(self):
        while self._running:
            if not self._paused:
                self._aggr.poll()
            sleep(0.1)

    def start(self):
        self._running = True
        self._thread.start()

    def stop(self):
        self._running = False

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def join(self):
        self._thread.join()
