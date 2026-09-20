import argparse
import os
import re

from .domain.directory_handler import DirectoryHandler

# Default source directory, relative to this file. The package lives at
# ``src/media_rename/``, so two levels up reaches the project root where
# ``work-directory`` sits. Override with the positional ``src`` CLI argument.
DEFAULT_SRC_DIRECTORY = "../../work-directory"

# APP


class App:
    def __init__(self, src):
        # Relative paths are resolved against this file's directory so the
        # default (and any relative CLI value) behaves the same regardless of
        # the current working directory. Absolute paths are used as-is.
        script_directory = os.path.dirname(os.path.abspath(__file__))
        self.src = os.path.join(script_directory, src)
        self.files = []

    def rename(self, dry_run: bool = False, enable_mtime: bool = False) -> None:
        files = self.directory_handler.media_files(self.src, enable_mtime=enable_mtime)

        for file in files:
            new_name = file.new_name()

            # No strategy could resolve a date for this file.
            if not new_name:
                print(f"{file}  [no date]")
                continue

            # Already correctly named (possibly with a collision suffix):
            # nothing to do. This keeps re-runs idempotent.
            if self._is_already_named(new_name, file.original_name):
                print(f"{file}  [unchanged]")
                continue

            source = file.source_path()
            final_name = self._resolve_collision(file.path, new_name, source)
            destination = os.path.join(file.path, final_name)

            if dry_run:
                print(f"{file}  --->  {final_name}")
                continue

            os.rename(source, destination)
            print(f"{file}  --->  {final_name}")

    def _is_already_named(self, new_name: str, current_name: str) -> bool:
        """True if ``current_name`` is ``new_name`` or a ``_N`` suffixed variant.

        A file already in the standard format resolves to the un-suffixed
        ``new_name``; treating its suffixed form as "already named" prevents
        re-runs from endlessly bumping the collision counter.
        """
        if current_name == new_name:
            return True

        stem, ext = os.path.splitext(new_name)
        cur_stem, cur_ext = os.path.splitext(current_name)
        if cur_ext != ext:
            return False
        # Matches "<stem>_<digits>".
        return bool(re.fullmatch(re.escape(stem) + r"_\d+", cur_stem))

    def _resolve_collision(self, directory: str, new_name: str, source: str) -> str:
        """Return a free filename in ``directory``, adding a numeric suffix on
        collision.

        The file's own ``source`` path is ignored so a file never collides with
        itself. On collision, tries ``name_1.ext``, ``name_2.ext``, ... until a
        free slot is found.
        """
        candidate = os.path.join(directory, new_name)
        if not os.path.exists(candidate) or os.path.samefile(candidate, source):
            return new_name

        stem, ext = os.path.splitext(new_name)
        counter = 1
        while True:
            suffixed = f"{stem}_{counter}{ext}"
            candidate = os.path.join(directory, suffixed)
            if not os.path.exists(candidate):
                return suffixed
            counter += 1

    def set_directory_provider(self, provider):
        self.directory_handler = provider


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Rename media files to a standard, date-based name."
    )
    parser.add_argument(
        "src",
        nargs="?",
        default=DEFAULT_SRC_DIRECTORY,
        help=(
            "Directory containing the media files to rename. Relative paths "
            "are resolved against the app's location. "
            f"Defaults to {DEFAULT_SRC_DIRECTORY!r}."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the renames without touching any files.",
    )
    parser.add_argument(
        "--enable-modified",
        action="store_true",
        help=(
            "Fall back to the file's modified time (mtime) when the name "
            "carries no recognizable timestamp. Disabled by default."
        ),
    )
    args = parser.parse_args(argv)

    app = App(args.src)
    app.set_directory_provider(DirectoryHandler())
    app.rename(dry_run=args.dry_run, enable_mtime=args.enable_modified)
