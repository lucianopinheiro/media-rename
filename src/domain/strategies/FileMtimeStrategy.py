import datetime
import os

from .DateStrategy import DateResult, DateStrategy


class FileMtimeStrategy(DateStrategy):
    """Resolve the date from the file's last-modified time (``mtime``).

    Last-resort strategy for files whose name carries no recognizable
    timestamp. It uses the filesystem modification time, which is only reliable
    when timestamps were preserved through any copies/transfers.

    Disabled by default: pass ``enabled=True`` to activate it (a user-facing
    option to toggle this will be added later).
    """

    def __init__(self, enabled: bool = False) -> None:
        super().__init__(enabled=enabled)

    def resolve(self, media) -> "DateResult | None":
        source = os.path.join(media.path, media.original_name)
        try:
            mtime = os.stat(source).st_mtime
        except OSError:
            return None

        date = datetime.datetime.fromtimestamp(mtime)
        return DateResult(date, self.normalized_extension(media.original_name))
