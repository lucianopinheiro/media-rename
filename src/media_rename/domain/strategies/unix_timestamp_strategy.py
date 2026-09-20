import datetime
import re

from .date_strategy import DateResult, DateStrategy


class UnixTimestampStrategy(DateStrategy):
    """Resolve the date from a Unix-timestamp filename.

    Handles both classic 10-digit second timestamps and 13-digit millisecond
    timestamps produced by some devices:
        - ``1665394638.jpg``      (seconds)
        - ``1665394638123.jpg``   (milliseconds)

    The whole stem must be digits, so this never collides with the
    ``yyyymmdd_hhMMss`` or prefixed patterns (which contain underscores). The
    resulting date is also range-checked to reject implausible values.
    """

    # Only accept a stem that is entirely digits, followed by an accepted
    # extension. 10 digits => seconds, 13 digits => milliseconds.
    def __init__(self, extensions: str) -> None:
        super().__init__()
        self._pattern = re.compile(
            r"(\d{10}|\d{13})\.(" + extensions + r")$", re.IGNORECASE
        )

    # Sanity window so a random long number isn't mistaken for a timestamp.
    _MIN_YEAR = 1990
    _MAX_YEAR = 2100

    def resolve(self, media) -> "DateResult | None":
        match = self._pattern.match(media.original_name)
        if match is None:
            return None

        digits, extension = match.groups()
        epoch = int(digits)
        # 13-digit values are milliseconds since the epoch. Use integer
        # division to drop the sub-second remainder so the resulting datetime
        # is second-resolution, consistent with the other strategies.
        if len(digits) == 13:
            epoch = epoch // 1000

        try:
            # Unix timestamps are UTC-based; interpret them as UTC. Drop the
            # tzinfo so the result is a naive datetime, consistent with the
            # sibling strategies and the strftime formatting in ``new_name``.
            date = datetime.datetime.fromtimestamp(epoch, tz=datetime.UTC).replace(
                tzinfo=None
            )
        except (OverflowError, OSError, ValueError):
            return None

        if not (self._MIN_YEAR <= date.year <= self._MAX_YEAR):
            return None

        return DateResult(date, extension.lower())
