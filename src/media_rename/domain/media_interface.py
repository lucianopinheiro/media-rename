import os

from .strategies.date_strategy import DateResult, DateStrategy


class Media:
    def __init__(self, filename) -> None:
        self.type = ""  # video,image
        self.path = os.path.dirname(filename)
        self.original_name = os.path.basename(filename)
        # The resolution chain is assembled by concrete subclasses.
        self._chain: DateStrategy | None = None

    def find_datetime(self) -> "DateResult | None":
        """Resolve the capture date/time for this file.

        Runs the strategy chain and returns its :class:`DateResult`, or ``None``
        when no strategy could resolve a date. Concrete subclasses assemble the
        chain in ``__init__``; the base class has none and resolves nothing.
        """
        if self._chain is None:
            return None
        return self._chain.handle(self)

    def new_name(self) -> "str | None":
        """Return the standardized filename, or ``None`` when no date is found."""
        result = self.find_datetime()
        if result is None:
            return None
        return result.date.strftime("%Y-%m-%d %H.%M.%S." + result.extension)

    def source_path(self) -> str:
        """Absolute/relative path to the current file on disk."""
        return os.path.join(self.path, self.original_name)
