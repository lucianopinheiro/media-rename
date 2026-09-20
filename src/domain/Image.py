from .MediaInterface import Media
from .strategies import (
    ExifDateStrategy,
    FileMtimeStrategy,
    FilenameTimestampStrategy,
    PrefixedFilenameStrategy,
    StandardNameStrategy,
    UnixTimestampStrategy,
)


class Image(Media):
    # Accepted image extensions as a regex alternation fragment.
    EXTENSIONS = r"jp[e]?g|png|gif"

    def __init__(self, filename, enable_mtime: bool = False):
        super().__init__(filename)
        self.type = "image"
        self._chain = self._build_chain(enable_mtime)

    def __str__(self) -> str:
        return "image: " + self.original_name

    def _build_chain(self, enable_mtime: bool = False):
        """Assemble the Chain of Responsibility for resolving the date.

        Order of precedence: the standardized output name (so already-renamed
        files are recognized), then EXIF metadata, then a plain
        ``yyyymmdd_hhMMss`` filename, then a prefixed ``IMG_yyyymmdd_hhMMss``
        filename, then a Unix timestamp filename. The file-mtime fallback is
        wired in last but disabled by default.
        """
        chain = StandardNameStrategy(self.EXTENSIONS)
        chain.set_next(ExifDateStrategy()).set_next(
            FilenameTimestampStrategy(self.EXTENSIONS)
        ).set_next(PrefixedFilenameStrategy(self.EXTENSIONS)).set_next(
            UnixTimestampStrategy(self.EXTENSIONS)
        ).set_next(FileMtimeStrategy(enabled=enable_mtime))
        return chain

    def find_datetime(self) -> None:
        result = self._chain.handle(self)
        if result is not None:
            self.date = result.date
            self.extension = result.extension
            self.found = True
