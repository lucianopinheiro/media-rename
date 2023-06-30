from pymediainfo import MediaInfo
import imghdr
import os


class MediaProvider:

    def __init__(self) -> None:
        pass

    def isImage(filename):
        """Determine if the file is an image

        Args:
            filename (str): filename
        """

        if (os.path.isdir(filename)):
            return False

        return imghdr.what(filename) != None

    def isVideo(filename):
        """Determine if the file is a video

        Args:
            filename (str): filename
        """

        if (os.path.isdir(filename)):
            return False

        fileInfo = MediaInfo.parse(filename)
        for track in fileInfo.tracks:
            if track.track_type == "Video":
                return True


# apt install python3-pymediainfo mediainfo
