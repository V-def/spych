"""logs"""


class Logger(object):
    """logs"""

    def __init__(self):
        self.path = "logs"
        self.name = "logs"
        self.extension = ".txt"

        self.reset()

    @property
    def file(self):
        """return the location of the log file"""
        return f'{self.path}/{self.name}{self.extension}'

    def reset(self):
        """resets the log file"""
        open(self.file, 'w').write('')

    def save_log(self, msg):
        """add a log to the file"""
        with open(self.file, 'a') as data:
            data.write(f'{msg}\n')

    @staticmethod
    def log(self, msg):
        """print the log"""
        print(msg)


class YoutubeDownloaderLogger(Logger):
    """specific logs from youtube dl"""
    def __init__(self):
        Logger.__init__(self)
        self.name = "ydl_logs"

    def debug(self, msg):
        self.log(msg)
        self.save_log(f'[debug] {self.save_log(msg)}')

    def warning(self, msg):
        self.save_log(f'[warning] {self.save_log(msg)}')

    def error(self, msg):
        self.save_log(f'[error] {self.save_log(msg)}')
