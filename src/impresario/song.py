from copy import deepcopy
from pathlib import Path
from typing import ClassVar, List, Sequence, Tuple

import attr
import tablib
from pypinyin import lazy_pinyin

from impresario import theory

PINYIN_ADJUSTMENTS = {ord("祢"): "nǐ,mí"}


@attr.s(auto_attribs=True, slots=True)
class Song:

    name: str
    _key: str = None
    hymn_ref: int = None
    sheet_type: str = None

    @property
    def pinyin(self) -> List[str]:
        """Get the name's pinyin, with each letter capitalized, to order with songs
        with English titles.

        Examples:
            >>> Song("歌曲").pinyin
            ["Ge", "Qu"]
            >>> Song("歌曲 a song").pinyin
            ["Ge", "Qu", "A", "Song"]
        """
        return [pinyin.title() for pinyin in lazy_pinyin(self.name.split(" "))]

    @property
    def key(self) -> str:
        """Get the normalized key."""
        return theory.normalize(self._key)

    @classmethod
    def from_dict(cls, name, key, hymn_ref, sheet_type, **kwargs) -> "Song":
        return cls(name=name, key=key, hymn_ref=hymn_ref, sheet_type=sheet_type)


@attr.s(auto_attribs=True, slots=True)
class Songbook:
    """A collection of songs."""

    HEADERS: ClassVar[List[str]] = ["name", "key", "hymn_ref", "sheet_type"]
    _data: Sequence[Tuple[str, str, int, str]]
    _sort_by: str = None
    _dataset: tablib.Dataset = attr.ib(init=False)

    def __attrs_post_init__(self):
        self._dataset = tablib.Dataset(*self._data, headers=self.HEADERS)
        self.sort(by=self._sort_by)
        return True

    @staticmethod
    def _sort_by_name(row):
        name_pinyin = lazy_pinyin(row[0].split(" "))
        title = [name.title() for name in name_pinyin]
        return [lazy_pinyin(title), theory.key_order(row[1])]

    @staticmethod
    def _sort_by_key(row):
        name_pinyin = lazy_pinyin(row[0].split(" "))
        title = [name.title() for name in name_pinyin]
        return [lazy_pinyin(title), theory.key_order(row[1])][::-1]

    @property
    def songs(self) -> List[Song]:
        """Get the songs in the songbook."""
        songs_list = []
        for song in self._dataset.dict:
            songs_list.append(Song.from_dict(**song))
        return songs_list

    @property
    def csv(self) -> str:
        return self._dataset.csv

    @classmethod
    def from_file(cls, data_source) -> "Songbook":
        """Create a ``Songbook`` instance from a csv file."""
        dataset = tablib.Dataset().load(open(data_source, "r", encoding="utf-8").read())
        songs = []
        for row in dataset:
            songs.append(row)
        return cls(songs)

    @classmethod
    def from_sheets(cls, sheets_folder: str) -> "Songbook":
        """Create a ``Songbook`` instance from sheets on the disk."""
        sheets_folder = Path(sheets_folder)
        if not sheets_folder.exists():
            raise ValueError(f"{sheets_folder} is invalid.")

        data = []

        for file in sheets_folder.iterdir():
            name, ext = file.name.split(".")
            if name == "" or ext.lower() not in ["pdf", "jpg", "png", "gif"]:
                continue
            data.append((name, "", "", ext))

        return cls(data)

    def sort(self, by: str) -> bool:
        """Add a dynamic column to the data, and sort the column by ``key`` function."""
        if by is None:
            return False
        elif by == "name":
            key_func = self._sort_by_name
        elif by == "key":
            key_func = self._sort_by_key
        else:
            raise ValueError("Can only sort by names or keys.")
        self._dataset.append_col(key_func, "sort_col")
        self._dataset = self._dataset.sort("sort_col")
        del self._dataset["sort_col"]
        return True

    def export(self, target_file: str, sort_by: str) -> bool:
        target_file = Path(target_file)
        target_file.touch(exist_ok=True)
        self.sort(sort_by)
        target_file.write_text(self._dataset.csv, "utf-8")
        return True

    def merge(self, other: "Songbook", update=True, ignore_empty=True) -> "Songbook":
        """Synchronize this songbook with another songbook.

        If ``update`` is ``True``, then keep the name form ``self`` and
        updates the information from ``other``, if it is not null.
        """
        if not isinstance(other, Songbook):
            raise TypeError(f"Cannot merge a `Songbook` with a(n) {type(other)}.")
        if self._dataset.headers != self._dataset.headers:
            raise ValueError("Two songbooks' headers must match in order to merge.")

        new_book = deepcopy(self)  # Hack.

        # Do a line by line analysis.
        # If `update` is True, then go ahead and update the data from
        # the other Songbook. If `update` is False, continue.

        for i, other_row in enumerate(other._dataset.dict):
            if other_row["name"] in self._dataset["name"] and update:
                new_row_index = new_book._dataset["name"].index(other_row["name"])
                new_row: List[str, str, int, str] = list(
                    new_book._dataset[new_row_index]
                )
                if ignore_empty:
                    for j, (header, value) in enumerate(other_row.items()):
                        if value:
                            new_row[j] = value
                        else:
                            pass
                else:
                    new_row = other_row.values()
                new_book._dataset.insert(index=new_row_index, row=new_row)
                del new_book._dataset[new_row_index + 1]
            else:
                new_book._dataset.append(other._dataset[i])

        new_book._dataset.remove_duplicates()
        new_book.sort(by=new_book._sort_by)
        return new_book

    def show_missing(self, column: str) -> List[str]:
        names_with_missing_data = []
        for name, check in zip(self._dataset["name"], self._dataset[column]):
            if not check:
                names_with_missing_data.append(name)
        return names_with_missing_data


def sync_songbook(site_dir: str, sheet_music_dir: str) -> bool:
    site_data = Path(site_dir)
    songs_csv = site_data / "_data/songs.csv"
    songs_by_key_csv = site_data / "_data/songs_by_key.csv"
    sheet_music = Path(sheet_music_dir)

    songbook = Songbook.from_file(songs_csv)
    songbook_sheets = Songbook.from_sheets(sheet_music)
    merged_songbook = songbook.merge(songbook_sheets)
    merged_songbook.export(songs_csv, sort_by="name")
    merged_songbook.export(songs_by_key_csv, sort_by="key")

    return True


def show_missing_songs(site_dir: str, column: str) -> List[str]:
    songbook = Songbook.from_file(Path(site_dir) / "_data/songs.csv")
    return songbook.show_missing(column)


if __name__ == "__main__":
    SITE_DIR = "/Users/kip/projects/lego-songbook"
    SONGBOOK_DIR = "/Users/kip/Documents/LEGO/Lego Songbook"

    # sync_songbook(SITE_DIR, SONGBOOK_DIR)
    # songbook = Songbook.from_file(Path(SITE_DIR) / "_data/songs.csv")
    # print(songbook.show_missing("sheet_type"))
    # print(show_missing_songs(SITE_DIR, "key"))
