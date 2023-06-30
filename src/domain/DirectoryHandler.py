import os

from .Image import Image
from .Video import Video
from .MediaInterface import Media
from .MediaHandler import MediaProvider


class DirectoryHandler:
    """Read and write files

    Args:
        object (_type_): _description_
    """

    def __init__(self) -> None:
        pass

    def media_files(self, srcDirectory) -> list[Media]:
        self.filenames = os.listdir(srcDirectory)
        mediafiles = []

        for f in self.filenames:
            source = os.path.join(srcDirectory, f)
            if MediaProvider.isImage(source):
                mediafiles.append(Image(source))
            elif MediaProvider.isVideo(source):
                mediafiles.append(Video(source))

        return mediafiles

    def __str__(self) -> str:
        return "directory handler"
