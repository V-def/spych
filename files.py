# -*- coding: utf-8 -*-
"""
Files and directory tools
"""
import os
import config
import re


class Directory:
    """basic Directory class which helps to play with directories"""

    def __init__(self, arg=None, name='', path='', find=True, create=True):
        """
        Construct a :class:`Directory <Directory>`.

        :param arg:
            main argument which can be Directory, File, str or None
        :param str name:
            name of the file
        :param str path:
            name of the path
        :param bool find:
            automatically searches the file
        """
        self.name = name
        self.path = path

        if type(arg) is Directory:
            self.from_class(arg)
        elif type(arg) is File:
            self.name = arg.path
        elif type(arg) is str:
            self.name = arg
        elif arg is None:
            pass
        else:
            raise TypeError(f'argument {arg} is a {type(arg).__name__}, expected Directory, File, str or None')

        if not self.path:
            self.path_from_name()

        self.path = self.path.replace('/', '\\') if self.path else '.'

        if find:
            self.find()

        if create:
            self.create()

        self.path = os.path.abspath(self.path)

    def find(self):
        """finds the directory in the sub folders if the file doesn't exists"""
        if not self:
            directory = self.name
            for root, dirnames, filenames in os.walk('.'):
                if directory in dirnames:
                    self.path = '\\'.join(os.path.split(root)).replace('/', '\\')

    def create(self):
        """create the directory if it doesn't exists"""
        if not self:
            os.mkdir(str(self))
            print(f'Successfully created directory "{self.name}" in {self.path}')

    def from_class(self, obj):
        """create a copy of the object"""
        for attribute in obj.__dict__:
            self.__dict__[attribute] = obj.__dict__[attribute]

    def path_from_name(self):
        """update path from name information"""
        temp = self.name.replace('/', '\\').split('\\')
        self.path = '\\'.join(temp[:-1])
        self.name = temp[-1]

    def __str__(self):
        """return the full path
        absolute path directing to the directory"""
        return f'{self.path}\\{self.name}'

    def __bool__(self):
        """the directory exists"""
        try:
            return self.name in os.listdir(self.path)
        except FileNotFoundError:
            return False

    def __repr__(self):
        return f'Directory({self}, exists={bool(self)})'


class File:
    """basic File class which helps to play with files"""

    def __init__(self, arg=None,
                 name: str='', path: str='', extension: str='', find: bool=True):
        """
        Construct a :class:`File <File>`.

        :param arg:
            main argument which can be File, str or None
        :param str name:
            name of the file
        :param str path:
            name of the path
        :param str extension:
            name of the extension with the dot
        :param bool find:
            automatically searches the file
        """

        self.name = name
        self.path = path
        self.extension = extension

        if type(arg) is File:
            self.from_class(arg)
        elif type(arg) is str:
            self.name = arg
        elif arg is None:
            pass
        else:
            raise TypeError(f'argument {arg} is a {type(arg).__name__}, expected File, None or str')

        if not self.path:
            self.path_from_name()

        if not self.extension:
            self.add_extension()

        self.path = self.path.replace('/', '\\') if self.path else '.'

        if find:
            self.find()

        self.path = os.path.abspath(self.path)

    def find(self):
        """finds the file in the sub folders if the file doesn't exists"""
        if not self:
            print(f'File {self} not found')
            file = self.name + self.extension
            for root, dirnames, filenames in os.walk('.'):
                if file in filenames:
                    self.path = '/'.join(os.path.split(root)).replace('/', '\\')
                    print(f'Using {self} instead')
                    return True
            return False

    def from_class(self, obj):
        """create a copy of the object"""
        for attribute in obj.__dict__:
            self.__dict__[attribute] = obj.__dict__[attribute]

    def path_from_name(self):
        """update path from name information"""
        temp = self.name.replace('/', '\\').split('\\')
        self.path = '\\'.join(temp[:-1])
        self.name = temp[-1]

    def add_extension(self):
        """add extension attribute"""
        temp = self.name.split('.')
        self.extension = '.' + temp[-1] if len(temp) > 1 else ''
        self.name = '.'.join(temp[:-1]) if len(temp) > 1 else temp[0]

    def __str__(self):
        """return the full path
        absolute path directing to the file"""
        return f'{self.path}\\{self.name}{self.extension}'

    def __bool__(self):
        """the file exists"""
        try:
            return self.name + self.extension in os.listdir(self.path)
        except FileNotFoundError:
            return False

    def __repr__(self):
        return f'File({self}, exists={bool(self)})'


class SafeName:
    """basic SafeName class which allows to have a string that can be used as directory or filenames"""

    def __init__(self, name: str):
        """
        :param str name:
            name of the file
        """
        self.real_name = None
        self._name = None
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        """convert the value to a safe name"""
        self.real_name = value
        max_length = 255
        ntfs_characters = [chr(i) for i in range(0, 31)]
        characters = [r'"', r"\#", r"\$", r"\%", r"'", r"\*", r"\,", r"\.", r"\/", r"\:",
                      r'"', r"\;", r"\<", r"\>", r"\?", r"\\", r"\^", r"\|", r"\~", r"\\\\"]
        pattern = "|".join(ntfs_characters + characters)
        regex = re.compile(pattern, re.UNICODE)
        value = regex.sub("", value)
        self._name = value[:max_length].rsplit(" ", 0)[0]

    def __bool__(self):
        """is there a name ?"""
        return bool(self.name)

    def __str__(self):
        """safe name"""
        return self.name


def create_video_directory(path: str=''):
    """create the video directory"""
    Directory(arg=f'{path}{config.VID_DIR_NAME}', find=False, create=True)


def video_directory(directory_name, find=True, create=True) -> Directory:
    """create and returns a directory object of a directory in the video directory"""
    return Directory(arg=f'{config.VID_DIR_NAME}\\{directory_name}', find=find, create=create)


def subtitle_directory(directory_name, find=True, create=True) -> Directory:
    """create and returns a directory object of a directory in the subtitles directory"""
    return Directory(arg=f'{directory_name}\\{config.VID_DIR_NAME}', find=find, create=create)


def search(path: str='.', name=None, extension_type: str='video', raise_error: bool=True) -> File:
    """
    searches a file in path based on the type of extension and the name
    :param str path:
        path of the directory you want to search in
    :param name:
        name of the file or None
    :param str extension_type:
        "video" or "subtitles"
    :param raise_error:
        raise an FileNotFoundError if the file is not found
    :return: File found
    """
    path = path if path else '.'
    extensions = {'video': config.VID_EXT, 'subtitles': config.SUB_EXT}

    if extension_type in extensions:
        for root, dirnames, filenames in os.walk(path):
            for extension in extensions[extension_type]:
                for filename in filenames:
                    if filename.endswith(extension):
                        if not name or filename.startswith(name):
                            return File(path=root, name=filename)

    else:
        raise Exception(
            f'unknown extension_type "{extension_type}", availible extensions are : {", ".join(extensions)}')

    if raise_error:
        raise FileNotFoundError(f"file {name} with an {extension_type} extension_type not found in {path}")
