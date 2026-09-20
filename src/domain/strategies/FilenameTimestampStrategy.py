import datetime
import re

from .DateStrategy import DateResult, DateStrategy


class FilenameTimestampStrategy(DateStrategy):
    """Resolve the date from a ``yyyymmdd_hhMMss`` filename.

    Examples:
        - ``20211228_100341.jpg``
        - ``20221010_103718.mp4``
        - ``20190120_072900398.png`` (trailing 3-digit milliseconds, ignored)

    The accepted extensions are supplied by the media subclass, so the same
    handler serves both images and videos.
    """

    def __init__(self, extensions: str) -> None:
        super().__init__()
        # ``extensions`` is a regex alternation fragment, e.g. "jp[e]?g" or
        # "mp[e]?g|mp4|3gp". An optional 3-digit millisecond group after the
        # time is accepted (and ignored, since names are second-resolution).
        self._pattern = re.compile(
            r"(\d{8})_(\d{6})(?:\d{3})?\.(" + extensions + r")$", re.IGNORECASE
        )

    def resolve(self, media) -> "DateResult | None":
        match = self._pattern.match(media.original_name)
        if match is None:
            return None

        date_part, time_part, extension = match.groups()
        date = datetime.datetime(
            int(date_part[0:4]),
            int(date_part[4:6]),
            int(date_part[6:8]),
            int(time_part[0:2]),
            int(time_part[2:4]),
            int(time_part[4:6]),
        )
        return DateResult(date, extension.lower())
