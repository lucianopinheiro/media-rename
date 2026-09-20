import datetime


class DateResult:
    """Value object returned by a handler when it successfully resolves a date."""

    def __init__(self, date: datetime.datetime, extension: str) -> None:
        self.date = date
        self.extension = extension


class DateStrategy:
    """Base handler for the Chain of Responsibility.

    Each concrete handler tries to resolve a capture date/time for a media
    file. If it cannot, it forwards the request to the next handler in the
    chain.
    """

    def __init__(self, enabled: bool = True) -> None:
        self._next: DateStrategy | None = None
        # A disabled handler is skipped: it never runs its own ``resolve`` and
        # simply forwards to the next handler in the chain.
        self.enabled = enabled

    def set_next(self, handler: "DateStrategy") -> "DateStrategy":
        """Link the next handler and return it so links can be chained fluently."""
        self._next = handler
        return handler

    def handle(self, media) -> "DateResult | None":
        """Try to resolve the date for ``media``.

        Concrete handlers override :meth:`resolve`. When they return ``None``
        (or the handler is disabled) the request is passed along to the next
        handler.
        """
        if self.enabled:
            result = self.resolve(media)
            if result is not None:
                return result
        if self._next is not None:
            return self._next.handle(media)
        return None

    def resolve(self, media) -> "DateResult | None":
        """Abstract hook implemented by concrete handlers."""
        raise NotImplementedError

    @staticmethod
    def normalized_extension(filename: str) -> str:
        """Return the lowercase extension without the leading dot."""
        _, _, ext = filename.rpartition(".")
        return ext.lower()
