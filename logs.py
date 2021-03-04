"""logs"""


class Logger(object):
    """logs"""

    def __init__(self):
        self.path = "logs"
        self.name = "name"
        self.extension = ".txt"

        if type(self) != Logger:
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

    def log(self, msg, save=True):
        """print the log"""
        print(msg)
        self.save_log(msg)


class YoutubeDownloaderLogger(Logger):
    """specific logs from youtube dl"""
    def __init__(self):
        Logger.__init__(self)
        self.name = "ydl"

    def debug(self, msg):
        self.log(msg)

    def warning(self, msg):
        self.log(msg)

    def error(self, msg):
        self.log(msg)
