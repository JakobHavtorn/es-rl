import sys
import os
import time
import IPython


class ProgressBar(object):
    def __init__(self, bar_width=None, title='', initial_progress=0, end_value=None, done_symbol='#', wait_symbol='-', keep_after_done=True):
        title += ": " if title != '' else ''
        self.title = title
        self._c = 7  # Lenth of the "[] xxx%" part of printed string
        if bar_width is None:
            try:
                _, bar_width = os.popen('stty size', 'r').read().split()
            except Exception:
                bar_width = 10 + len(title) + self._c
        self._w = int(bar_width) - len(self.title) - self._c  # Subtract constant parts of string length
        assert self._w >= 0, 'Title too long, bar width too narrow or terminal window not wide enough'
        self._b = self._w + len(self.title) + self._c  # Number of left shifts to apply at end to reset to head of line
        self.end_value = end_value
        self.ds = done_symbol
        self.ws = wait_symbol
        self.initial_x = initial_progress
        self.keep_after_done = keep_after_done

    def start(self):
        """Creates a progress bar `width` chars long on the console
        and moves cursor back to beginning with BS character"""
        self.progress(self.initial_x)

    def progress(self, x):
        """Sets progress bar to a certain percentage x if `end_value`
        is `None`, otherwise, computes `x` as percentage of `end_value`."""
        assert x <= 1 or self.end_value is not None and self.end_value >= x
        if self.end_value is not None:
            x = x / self.end_value
        y = int(x * self._w)                      
        sys.stdout.write(self.title + "[" + self.ds * y + self.ws * (self._w - y) + "] {:3d}%".format(int(round(x * 100))) + chr(8) * self._b)
        sys.stdout.flush()

    def end(self):
        """End of progress bar.
        Write full bar, then move to next line except if `keep_after_done` is false
        in which case the bar is replaced by spaces and the cursor reset."""
        if self.keep_after_done:
            s = self.title + "[" + self.ds * self._w + "] {:3d}%".format(100) + "\n"
        else:
            s = ' ' * self._b  + chr(8) * self._b
        sys.stdout.write(s)
        sys.stdout.flush()


class PoolProgress(object):
    def __init__(self, pool, update_interval=3, **kwargs):
        """Monitors progress of jobs on a parallel pool
        
        Args:
            pool (multiprocessing.Pool): A pool of workers
            **kwargs (dict): Additional arguments to ProgressBar
            update_interval (int, optional): Defaults to 3. Interval in seconds
        """
        self.pb = ProgressBar(**kwargs)
        self.pool = pool
        self.update_interval = update_interval

    def track(self, job):
        """Track a job
        
        Args:
            job (multiprocessing.Pool.MapResult): The result object of the job to monitor
        """
        task = self.pool._cache[job._job]
        n_tasks = task._number_left*task._chunksize
        self.pb.end_value = n_tasks
        self.pb.start()
        while task._number_left>0:
            self.pb.progress(n_tasks - task._number_left*task._chunksize)
            time.sleep(self.update_interval)
        self.pb.end()


def startprogress(title):
    """Creates a progress bar 40 chars long on the console
    and moves cursor back to beginning with BS character"""
    global progress_x
    sys.stdout.write(title + ": [" + "-" * 40 + "]" + chr(8) * 41)
    sys.stdout.flush()
    progress_x = 0


def progress(x):
    """Sets progress bar to a certain percentage x.
    Progress is given as whole percentage, i.e. 50% done
    is given by x = 50"""
    global progress_x
    x = int(x * 40 // 100)                      
    sys.stdout.write("#" * x + "-" * (40 - x) + "]" + chr(8) * 41)
    sys.stdout.flush()
    progress_x = x


def endprogress():
    """End of progress bar.
    Write full bar, then move to next line"""
    sys.stdout.write("#" * 40 + "]\n")
    sys.stdout.flush()


def progressBar(value, endvalue, bar_length=20):
    """Write and update a progress bar.
    """
    percent = float(value) / endvalue
    arrow = '-' * int(round(percent * bar_length)-1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    sys.stdout.write("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
    sys.stdout.flush()

# Testing
if __name__ == '__main__':
    sleep = 0.05
    pb = ProgressBar(title='Test: 20s with 4s elapsed and some other stuff', initial_progress=4, end_value=100)
    pb.start()
    time.sleep(sleep)
    for i in range(5, 100):
        pb.progress(i)
        time.sleep(sleep)
    pb.end()

    pb = ProgressBar(title='Test: Removing bar after done', end_value=100, keep_after_done=False)
    pb.start()
    time.sleep(sleep)
    for i in range(100):
        pb.progress(i)
        time.sleep(sleep)
    pb.end()
    print("Here is some new information while we wait for a new bar to appear...")
    time.sleep(1)
    pb = ProgressBar(title='Test: Removing bar after done', end_value=100, keep_after_done=False)
    pb.start()
    time.sleep(sleep)
    for i in range(100):
        pb.progress(i)
        time.sleep(sleep)
    pb.end()
    print("Now we are done!")


    IPython.embed()
    