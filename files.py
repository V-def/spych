"""everything os related"""
import os


class File:
    """basic File class which helps to play with files"""

    def __init__(self, arg, name='', path='', extension=''):
        self.name = name
        self.path = path
        self.extension = extension

        if type(arg) is File:
            self.from_file(arg)
        elif type(arg) is str:
            self.name = arg
        else:
            raise Exception()

        if not self.path:
            self.path_from_name()

        if not self.extension:
            self.add_extension()

        self.path = self.path if self.path else '.'

        if not self:
            file = File(self)
            file.path = 'videos'
            if file:
                self.from_file(file)

    def from_file(self, file):
        """replace it's attributes with the file one's"""
        for attribute in file.__dict__:
            self.__dict__[attribute] = file.__dict__[attribute]

    def path_from_name(self):
        """update path from name information"""
        temp = self.name.split('/')
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
        return self.name + self.extension in os.listdir(self.path)

    def __repr__(self):
        return f'{self.file}\nExists = {bool(self)}'


class Setup:
    """setup the environment for the main class"""
    def __init__(self, directory):
        self.directory = directory

    def create_directory(self):
        """create necessary directory"""
        for path in f'videos/{self.directory}', f'videos/{self.directory}/subtitles':
            self.create_folder(path)

    @staticmethod
    def create_folder(path):
        """create folder from path without raising errors if folder already exists"""
        try:
            os.mkdir(path)
            return True
        except FileExistsError:
            return False
