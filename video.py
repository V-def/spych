"""video"""


class Video:
    """video class"""

    def __init__(self, file):
        if not file:
            raise FileNotFoundError(f'File {file} not found')
        self.file = file
