from ConsoleUI.ScreenManager import ScreenManager
from ConsoleUI.MainScreen import MainScreen
from LogAggregate import LogAggregate, LogAggregateThread
from LogSource import LogSource
from getopt import gnu_getopt
from sys import argv
from signal import SIGWINCH

class Config:
    def __init__(self):
        self.log_files = []

def parse_args(args: list):
    config = Config()

    options, args = gnu_getopt(args, "u", [])

    for arg in args:
        config.log_files.append(arg)

    return config

def main(config: Config):
    mgr = ScreenManager()
    main_screen = MainScreen()
    mgr.add_screen("main", main_screen)

    aggregate = LogAggregate(main_screen)
    aggregate_thread = LogAggregateThread(aggregate)
    main_screen.bind_log_aggregate(aggregate)

    for f in config.log_files:
        source = LogSource(f)
        aggregate.add_source(f, source)

    aggregate_thread.start()

    mgr.set_active("main")

    mgr.run()

    aggregate_thread.stop()
    aggregate_thread.join()


if __name__ == "__main__":
    config = parse_args(argv[1:])
    main(config)
