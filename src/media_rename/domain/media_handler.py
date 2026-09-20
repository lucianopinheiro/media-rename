import os

try:
    from PIL import Image as PILImage
except ImportError:  # pragma: no cover
    PILImage = None

try:
    from pymediainfo import MediaInfo
except ImportError:  # pragma: no cover
    MediaInfo = None


class MediaProvider:
    VIDEO_EXTENSIONS = (".mpg", ".mpeg", ".mp4", ".3gp", ".mov", ".avi", ".mkv")

    @staticmethod
    def is_image(filename):
        """Determine if the file is an image

        Args:
            filename (str): filename
        """

        if os.path.isdir(filename):
            return False

        # Preferred: let Pillow try to decode the file as an image.
        if PILImage is not None:
            try:
                with PILImage.open(filename) as img:
                    img.verify()
                return True
            except Exception:
                return False

        # Fallback when Pillow is unavailable: rely on the extension.
        return filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))

    @staticmethod
    def is_video(filename):
        """Determine if the file is a video

        Args:
            filename (str): filename
        """

        if os.path.isdir(filename):
            return False

        # Preferred: inspect container tracks with pymediainfo.
        if MediaInfo is not None:
            try:
                file_info = MediaInfo.parse(filename)
                for track in file_info.tracks:
                    if track.track_type == "Video":
                        return True
                return False
            except Exception:
                pass

        # Fallback when pymediainfo is unavailable: rely on the extension.
        return filename.lower().endswith(MediaProvider.VIDEO_EXTENSIONS)


# Optional native deps for richer detection:
#   apt install python3-pymediainfo mediainfo
#   pip install Pillow
