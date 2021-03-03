"""everything os related"""
import os


class File:
    """basic File class which helps to play with files"""

    def __init__(self, arg, name='', path='', extension='', find=True):
        self.name = name
        self.path = path
        self.extension = extension

        if type(arg) is File:
            self.from_file(arg)
        elif type(arg) is str:
            self.name = arg
        else:
            raise TypeError(f'argument {arg} is a {type(arg)}, expected File or str')

        if not self.path:
            self.path_from_name()

        if not self.extension:
            self.add_extension()

        self.path = self.path.replace('\\', '/') if self.path else '.'

        if find:
            self.find()

    def find(self):
        if not self:
            print(f'File {self} not found')
            file = self.name + self.extension
            for root, dirnames, filenames in os.walk('.'):
                if file in filenames:
                    self.path = '/'.join(os.path.split(root)).replace('\\', '/')
                    print(f'Using {self} instead')
                    return True
            return False

    def from_file(self, file):
        """replace it's attributes with the file one's"""
        for attribute in file.__dict__:
            self.__dict__[attribute] = file.__dict__[attribute]

    def path_from_name(self):
        """update path from name information"""
        temp = self.name.replace('\\', '/').split('/')
        self.path = '/'.join(temp[:-1])
        self.name = temp[-1]

    def add_extension(self):
        """add extension attribute"""
        temp = self.name.split('.')
        self.extension = '.' + temp[-1] if len(temp) > 1 else ''
        self.name = '.'.join(temp[:-1]) if len(temp) > 1 else temp[0]

    def __str__(self):
        return f'{self.path}/{self.name}{self.extension}'

    def __bool__(self):
        try:
            return self.name + self.extension in os.listdir(self.path)
        except FileNotFoundError:
            return False

    def __repr__(self):
        return f'File({self}, exists={bool(self)}'


class Setup:
    """setup the environment for the main class"""
    def __init__(self, directory):
        self.directory = directory

    @property
    def path(self):
        return f'videos/{self.directory}'

    def create_directory(self, video_directory='videos'):
        """create necessary directory"""

        paths = video_directory, f'{video_directory}/{self.directory}', f'{video_directory}/{self.directory}/subtitles'

        for path in paths:
            self.create_folder(path)

    @staticmethod
    def create_folder(path):
        """create folder from path without raising errors if folder already exists"""
        try:
            os.mkdir(path)
            return True
        except FileExistsError:
            return False

    @staticmethod
    def search(path, name, extension='subtitles', raise_error=True):
        matches = []
        extensions = {'subtitles': ('.vtt', '.srt'), 'video': ('.mp4', '.avi')}
        for file in os.listdir(path):
            if name in file:
                if file.endswith(extensions[extension]):
                    matches.append(File(f'{path}/{file}'))

        if raise_error and not matches:
            raise FileNotFoundError(f"file {name} with an {extension} extension not found in {path}")

        return matches
