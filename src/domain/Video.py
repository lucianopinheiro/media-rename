from .MediaInterface import Media
from .strategies import (
    FileMtimeStrategy,
    FilenameTimestampStrategy,
    PrefixedFilenameStrategy,
    StandardNameStrategy,
    UnixTimestampStrategy,
)


class Video(Media):
    # Accepted video extensions as a regex alternation fragment.
    EXTENSIONS = r"mp[e]?g|mp4|3gp"

    def __init__(self, filename, enable_mtime: bool = False):
        super().__init__(filename)
        self.type = "video"
        self._chain = self._build_chain(enable_mtime)

    def __str__(self) -> str:
        return "video: " + self.original_name

    def _build_chain(self, enable_mtime: bool = False):
        """Assemble the Chain of Responsibility for resolving the date.

        Videos have no EXIF, so the chain relies on filename patterns: first the
        standardized output name (so already-renamed files are recognized), then
        a plain ``yyyymmdd_hhMMss`` name, then a prefixed ``VID_yyyymmdd_hhMMss``
        name, then a Unix timestamp name. The file-mtime fallback is wired in
        last but disabled by default.
        """
        chain = StandardNameStrategy(self.EXTENSIONS)
        chain.set_next(FilenameTimestampStrategy(self.EXTENSIONS)).set_next(
            PrefixedFilenameStrategy(self.EXTENSIONS)
        ).set_next(UnixTimestampStrategy(self.EXTENSIONS)).set_next(
            FileMtimeStrategy(enabled=enable_mtime)
        )
        return chain

    def find_datetime(self) -> None:
        result = self._chain.handle(self)
        if result is not None:
            self.date = result.date
            self.extension = result.extension
            self.found = True
