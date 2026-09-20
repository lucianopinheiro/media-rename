import datetime
import re

from .DateStrategy import DateResult, DateStrategy


class StandardNameStrategy(DateStrategy):
    """Recognize a file already in the standardized output format.

    Matches ``YYYY-MM-DD HH.MM.SS.<ext>`` with an optional ``_N`` collision
    suffix (e.g. ``2022-08-11 23.12.02_1.jpg``). This makes renaming idempotent:
    an already-correct file resolves to its own name and is left untouched.
    """

    def __init__(self, extensions: str) -> None:
        super().__init__()
        self._pattern = re.compile(
            r"(\d{4})-(\d{2})-(\d{2}) (\d{2})\.(\d{2})\.(\d{2})(?:_\d+)?\.("
            + extensions
            + r")$",
            re.IGNORECASE,
        )

    def resolve(self, media) -> "DateResult | None":
        match = self._pattern.match(media.original_name)
        if match is None:
            return None

        year, month, day, hour, minute, second, extension = match.groups()
        try:
            date = datetime.datetime(
                int(year),
                int(month),
                int(day),
                int(hour),
                int(minute),
                int(second),
            )
        except ValueError:
            return None

        return DateResult(date, extension.lower())
