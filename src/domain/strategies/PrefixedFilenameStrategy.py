import datetime
import re

from .DateStrategy import DateResult, DateStrategy


class PrefixedFilenameStrategy(DateStrategy):
    """Resolve the date from a prefixed ``PREFIX_yyyymmdd_hhMMss`` filename.

    Examples:
        - ``IMG_20201210_182442.jpg``
        - ``VID_20201219_092426.3gp``
        - ``IMG_20201210_182442_001.jpg`` (trailing counter is ignored)
        - ``IMG_20190120_072900398.jpg`` (trailing milliseconds are ignored)

    Migrated from the ``new_name_imgvid_datetime`` prototype in ``temp/``.
    """

    def __init__(self, extensions: str) -> None:
        super().__init__()
        # After the 6-digit time, tolerate either an attached 3-digit
        # millisecond group or an ``_NNN`` counter/millisecond suffix.
        self._pattern = re.compile(
            r"[A-Za-z]{3}_(\d{8})_(\d{6})(?:\d{3}|_\d{3})?\.(" + extensions + r")$",
            re.IGNORECASE,
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
