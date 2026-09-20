import datetime
import os

from .DateStrategy import DateResult, DateStrategy

try:
    from PIL import Image as PILImage
    from PIL.ExifTags import IFD
except ImportError:  # pragma: no cover - Pillow is a runtime dependency
    PILImage = None
    IFD = None


class ExifDateStrategy(DateStrategy):
    """Resolve the capture date from a photo's EXIF metadata.

    Reads the EXIF timestamp tags in order of preference:
    ``DateTimeOriginal`` (0x9003), ``DateTimeDigitized`` (0x9004) and finally
    the base ``DateTime`` (0x0132). EXIF stores these as ``"YYYY:MM:DD HH:MM:SS"``.
    """

    # EXIF tag ids for the datetime fields.
    _DATETIME = 0x0132          # DateTime (IFD0)
    _DATETIME_ORIGINAL = 0x9003  # DateTimeOriginal (Exif IFD)
    _DATETIME_DIGITIZED = 0x9004  # DateTimeDigitized (Exif IFD)

    _EXIF_FORMAT = "%Y:%m:%d %H:%M:%S"

    def resolve(self, media) -> "DateResult | None":
        if PILImage is None:
            return None

        source = os.path.join(media.path, media.original_name)
        raw = self._read_datetime(source)
        if not raw:
            return None

        try:
            date = datetime.datetime.strptime(raw.strip(), self._EXIF_FORMAT)
        except ValueError:
            return None

        return DateResult(date, self.normalized_extension(media.original_name))

    def _read_datetime(self, source: str) -> "str | None":
        try:
            with PILImage.open(source) as img:
                exif = img.getexif()
        except (OSError, ValueError):
            return None

        if not exif:
            return None

        # DateTimeOriginal / DateTimeDigitized live in the Exif sub-IFD.
        exif_ifd = {}
        if IFD is not None:
            try:
                exif_ifd = exif.get_ifd(IFD.Exif)
            except (KeyError, ValueError):
                exif_ifd = {}

        for tag in (self._DATETIME_ORIGINAL, self._DATETIME_DIGITIZED):
            value = exif_ifd.get(tag)
            if value:
                return value

        value = exif.get(self._DATETIME)
        if value:
            return value

        return None
