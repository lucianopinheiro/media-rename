# media-rename

Rename media (image or video) to fit a standard, sortable name based on the
capture date/time:

```
YYYY-MM-DD HH.MM.SS.<ext>
```

The capture date is resolved through a Chain of Responsibility of strategies,
tried in order until one succeeds:

1. **EXIF** metadata (images only) — `DateTimeOriginal` / `DateTimeDigitized` / `DateTime`.
2. **Filename timestamp** — e.g. `20221010_103718.jpg`.
3. **Prefixed filename** — e.g. `IMG_20201210_182442.jpg`, `VID_20201219_092426.3gp`.
4. **Unix timestamp filename** — e.g. `1665394638.jpg` (seconds) or `1665394638123.jpg` (milliseconds). Interpreted as UTC.

## Requirements

- **Python 3.12 or newer.**

## Setup

The project runs from a virtual environment.

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows (PowerShell)

# Install dependencies
pip install -r requirements.txt
```

### Optional: video metadata detection

Richer video detection uses `pymediainfo`, which relies on the native
`libmediainfo` library:

```bash
sudo apt install mediainfo          # Debian / Ubuntu
pip install pymediainfo
```

Without it, the app falls back to detecting videos by file extension.

### Development tooling

Linting and formatting use [ruff](https://docs.astral.sh/ruff/) (configured in
`pyproject.toml`, targeting Python 3.12):

```bash
pip install -e ".[dev]"     # installs ruff + pytest
ruff check src/             # lint
ruff check --fix src/       # lint and auto-fix
```

Tests use [pytest](https://docs.pytest.org/) and live in `tests/`:

```bash
pytest                      # run the suite
```

## Run

With the virtual environment activated, run the package from the project root:

```bash
python -m media_rename [src] [options]
```

Or install it (`pip install -e .`) to get the `media-rename` command, which
works from any directory:

```bash
media-rename [src] [options]
```

Files are renamed **in place** (in the same directory).

- `src` — optional directory containing the media files to rename. Relative
  paths are resolved against the app's location. Defaults to
  `../work-directory`.

  ```bash
  python -m media_rename ~/Pictures/camera-roll
  ```

### Options

- `--dry-run` — preview only, prints `old ---> new` without touching any files.

  ```bash
  python -m media_rename --dry-run
  ```

- `--enable-modified` — as a last resort, use the file's modified time (mtime)
  for files whose name carries no recognizable timestamp. Disabled by default,
  since mtime is only reliable when it was preserved through copies/transfers.

  ```bash
  python -m media_rename --enable-modified
  ```

### Behavior

- **Already named:** files already in the standard format are reported
  `ok (unchanged)` and left alone, so re-runs are idempotent.
- **No date found:** files no strategy can resolve are reported
  `skip (no date)` and left alone.
- **Name collision (auto-suffix):** when two files resolve to the same name,
  the first keeps the clean name and the rest get a numeric suffix
  (`..._1`, `..._2`, ...). Nothing is overwritten.
