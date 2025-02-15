import cProfile
import pstats


_active_profilers = {}


def start(title=''):
    if title not in _active_profilers:
        _active_profilers[title] = Profiler()
    if not _active_profilers[title].is_running:
        _active_profilers[title].toggle()


def stop(title=''):
    if title in _active_profilers:
        if _active_profilers[title].is_running:
            _active_profilers[title].toggle()
        del _active_profilers[title]


class Profiler:

    def __init__(self):
        self.is_running = False
        self.pr = cProfile.Profile(builtins=False)

    def toggle(self):
        self.is_running = not self.is_running

        if not self.is_running:
            self.pr.disable()

            ps = pstats.Stats(self.pr)
            ps.strip_dirs()
            ps.sort_stats('cumulative')
            ps.print_stats(35)

        else:
            print("Started profiling...")
            self.pr.clear()
            self.pr.enable()

