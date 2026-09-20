"""Tests for the App orchestration: idempotency, collisions, and renaming."""

import datetime
import os

from media_rename.app import App
from media_rename.domain.media_interface import Media


class FakeMedia(Media):
    """A Media whose date is set directly, bypassing the strategy chain."""

    def __init__(self, filename, date, extension):
        super().__init__(filename)
        self.type = "image"
        self.date = date
        self.extension = extension
        self.found = date is not None

    def find_datetime(self):  # pragma: no cover - date is preset
        pass

    def __str__(self):
        return f"image: {self.original_name}"


class FakeProvider:
    """Directory provider that yields a preset list of media objects."""

    def __init__(self, files):
        self._files = files

    def media_files(self, src_directory, enable_mtime: bool = False):
        return self._files


DATE = datetime.datetime(2022, 10, 10, 10, 37, 18)
STD_NAME = "2022-10-10 10.37.18.jpg"


# --------------------------------------------------------------------------- #
# _is_already_named
# --------------------------------------------------------------------------- #


def test_is_already_named_exact_match():
    app = App("ignored")
    assert app._is_already_named(STD_NAME, STD_NAME) is True


def test_is_already_named_with_collision_suffix():
    app = App("ignored")
    assert app._is_already_named(STD_NAME, "2022-10-10 10.37.18_3.jpg") is True


def test_is_already_named_different_name():
    app = App("ignored")
    assert app._is_already_named(STD_NAME, "20221010_103718.jpg") is False


def test_is_already_named_different_extension():
    app = App("ignored")
    assert app._is_already_named(STD_NAME, "2022-10-10 10.37.18.png") is False


# --------------------------------------------------------------------------- #
# _resolve_collision
# --------------------------------------------------------------------------- #


def test_resolve_collision_no_conflict(tmp_path):
    app = App("ignored")
    source = tmp_path / "20221010_103718.jpg"
    source.write_text("")
    result = app._resolve_collision(str(tmp_path), STD_NAME, str(source))
    assert result == STD_NAME


def test_resolve_collision_ignores_self(tmp_path):
    # A file already sitting at the target name must not collide with itself.
    app = App("ignored")
    source = tmp_path / STD_NAME
    source.write_text("")
    result = app._resolve_collision(str(tmp_path), STD_NAME, str(source))
    assert result == STD_NAME


def test_resolve_collision_adds_suffix(tmp_path):
    app = App("ignored")
    # An unrelated file already occupies the target name.
    (tmp_path / STD_NAME).write_text("")
    source = tmp_path / "20221010_103718.jpg"
    source.write_text("")

    result = app._resolve_collision(str(tmp_path), STD_NAME, str(source))
    assert result == "2022-10-10 10.37.18_1.jpg"


def test_resolve_collision_bumps_counter(tmp_path):
    app = App("ignored")
    (tmp_path / STD_NAME).write_text("")
    (tmp_path / "2022-10-10 10.37.18_1.jpg").write_text("")
    source = tmp_path / "20221010_103718.jpg"
    source.write_text("")

    result = app._resolve_collision(str(tmp_path), STD_NAME, str(source))
    assert result == "2022-10-10 10.37.18_2.jpg"


# --------------------------------------------------------------------------- #
# rename — end to end
# --------------------------------------------------------------------------- #


def test_rename_renames_file_on_disk(tmp_path):
    original = tmp_path / "20221010_103718.jpg"
    original.write_text("data")

    app = App("ignored")
    app.set_directory_provider(
        FakeProvider([FakeMedia(str(original), DATE, "jpg")])
    )
    app.rename()

    assert not original.exists()
    assert (tmp_path / STD_NAME).read_text() == "data"


def test_rename_dry_run_leaves_files_untouched(tmp_path):
    original = tmp_path / "20221010_103718.jpg"
    original.write_text("data")

    app = App("ignored")
    app.set_directory_provider(
        FakeProvider([FakeMedia(str(original), DATE, "jpg")])
    )
    app.rename(dry_run=True)

    assert original.exists()
    assert not (tmp_path / STD_NAME).exists()


def test_rename_skips_file_without_date(tmp_path):
    original = tmp_path / "vacation.jpg"
    original.write_text("data")

    app = App("ignored")
    app.set_directory_provider(
        FakeProvider([FakeMedia(str(original), None, "jpg")])
    )
    app.rename()

    # Left untouched because no date could be resolved.
    assert original.exists()


def test_rename_is_idempotent_on_already_named(tmp_path):
    already = tmp_path / STD_NAME
    already.write_text("data")

    app = App("ignored")
    app.set_directory_provider(
        FakeProvider([FakeMedia(str(already), DATE, "jpg")])
    )
    app.rename()

    # Still there under the same name, nothing bumped.
    assert already.exists()
    assert not (tmp_path / "2022-10-10 10.37.18_1.jpg").exists()


def test_rename_resolves_collision_between_two_files(tmp_path):
    first = tmp_path / "20221010_103718.jpg"
    second = tmp_path / "IMG_20221010_103718.jpg"
    first.write_text("first")
    second.write_text("second")

    app = App("ignored")
    app.set_directory_provider(
        FakeProvider(
            [
                FakeMedia(str(first), DATE, "jpg"),
                FakeMedia(str(second), DATE, "jpg"),
            ]
        )
    )
    app.rename()

    names = sorted(os.listdir(tmp_path))
    assert names == [STD_NAME, "2022-10-10 10.37.18_1.jpg"]
