import os

from .Image import Image
from .MediaHandler import MediaProvider
from .MediaInterface import Media
from .Video import Video


class DirectoryHandler:
    """Read and write files

    Args:
        object (_type_): _description_
    """

    def __init__(self) -> None:
        pass

    def media_files(self, src_directory, enable_mtime: bool = False) -> list[Media]:
        self.filenames = sorted(os.listdir(src_directory))
        mediafiles = []

        for f in self.filenames:
            source = os.path.join(src_directory, f)
            if MediaProvider.is_image(source):
                mediafiles.append(Image(source, enable_mtime=enable_mtime))
            elif MediaProvider.is_video(source):
                mediafiles.append(Video(source, enable_mtime=enable_mtime))

        return mediafiles

    def __str__(self) -> str:
        return "directory handler"
