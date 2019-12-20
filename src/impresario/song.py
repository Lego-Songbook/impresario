from collections import defaultdict
from pathlib import Path
from typing import List, Sequence

import attr
import tablib
from pypinyin import lazy_pinyin, load_single_dict, style

from . import theory

PINYIN_ADJUSTMENTS = {ord("祢"): "nǐ,mí"}

SITE_DIR = "/Users/kip/projects/lego-songbook"


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

    _data: tablib.Dataset
    _sort_by: str = "name"

    def __attrs_post_init__(self):
        if self._sort_by == "name":
            key = self._sort_by_name
        elif self._sort_by == "key":
            key = self._sort_by_key
        else:
            raise ValueError("Can only sort by names or keys.")
        self._data.append_col(key, "sort_col")
        self._data = self._data.sort("sort_col")
        del self._data["sort_col"]
        return True

    @classmethod
    def from_file(cls, data_source) -> "Songbook":
        """Create a ``Songbook`` instance from a csv file."""
        return cls(
            tablib.Dataset().load(open(data_source, "r", encoding="utf-8").read())
        )

    @classmethod
    def from_sheets(cls, sheets_folder: str) -> "Songbook":
        """Create a ``Songbook`` instance from sheets on the disk."""
        sheets_folder = Path(sheets_folder)
        if not sheets_folder.exists():
            raise ValueError(f"{sheets_folder} is invalid.")

        headers = ["name", "sheet_type"]
        data = tablib.Dataset(headers=headers)

        for file in sheets_folder.iterdir():
            name, ext = file.name.split(".")
            if name == "" or ext.lower() not in ["pdf", "jpg", "png", "gif"]:
                continue
            data.append((name, ext))

        return cls(data)

    @staticmethod
    def _sort_by_name(row):
        name_pinyin = lazy_pinyin(row[0].split(" "))
        title = [name.title() for name in name_pinyin]
        return [lazy_pinyin(title), theory.key_order(row[1])]

    @staticmethod
    def _sort_by_key(row):
        return [lazy_pinyin(row[0].split(" ")), theory.key_order(row[1])][::-1]

    def sort(self, by: str) -> bool:
        """Add a dynamic column to the data, and sort the column by ``key`` function."""
        if by == "name":
            key = self._sort_by_name
        elif by == "key":
            key = self._sort_by_key
        else:
            raise ValueError("Can only sort by names or keys.")
        self._data.append_col(key, "sort_col")
        self._data = self._data.sort("sort_col")
        del self._data["sort_col"]
        return True

    def dump_songs(self, target_file: str) -> bool:
        target_file = Path(target_file)
        target_file.touch(exist_ok=True)
        target_file.write_text(self._data.csv, "utf-8")
        return True


# def sort_by_name(row):
#     name_pinyin = lazy_pinyin(row[0])
#     title = [name.title() for name in name_pinyin]
#     return [lazy_pinyin(title), theory.key_order(row[1])]
#
#
# def sort_by_key(row):
#     return [lazy_pinyin(row[0].split(" ")), theory.key_order(row[1])][::-1]
#
#
# def load_songs(data_source: str) -> tablib.Dataset:
#     return tablib.Dataset().load(open(data_source, "r", encoding="utf-8").read())
#
#
# def sort_songs(songs: tablib.Dataset, key) -> tablib.Dataset:
#     songs.append_col(key, "pinyin")
#     songs = songs.sort("pinyin")
#     del songs["pinyin"]
#     return songs


# def dump_songs(songs: tablib.Dataset, target_file: str) -> bool:
#     with open(target_file, "w", encoding="utf-8") as file:
#         file.write(songs.export("csv"))
#     return True


# def get_local_songs(path: str) -> dict:
#     local_songs = {}
#     path = Path(path)
#     for file in path.iterdir():
#         name, ext = file.name.split(".")
#         if name == "":
#             continue
#         local_songs[name] = ext
#     return local_songs


def add_sheet_ext(row):
    local_songs = get_local_songs("/Users/kip/Documents/LEGO/Lego Songbook")
    return local_songs.get(row[0], "")


def change_sheet_to_ext(songs: tablib.Dataset, path: str) -> tablib.Dataset:
    local_songs = get_local_songs(path)
    songs.append_col(add_sheet_ext, "sheet_type")
    del songs["sheet_type"]
    return songs


def sync_local_songs(songs: tablib.Dataset, path: str) -> tablib.Dataset:
    local_songs = get_local_songs(path)
    for local_song, ext in local_songs.items():
        if local_song not in songs["name"]:
            songs.append([local_song, "", "--", ext])
    return songs


if __name__ == "__main__":
    SONGS_CSV = Path(SITE_DIR) / "_data/songs.csv"
    SONGS_BY_KEY_CSV = Path(SITE_DIR) / "_data/songs_by_key.csv"
    SONGBOOK_DIR = "/Users/kip/Documents/LEGO/Lego Songbook"
    # dump_songs(sort_songs_by_pinyin(load_songs(SONGS_CSV)), SONGS_BY_KEY_CSV)
    # print(key_order(key_conversion("G#m")))
    # print(get_local_songs("/Users/kip/Documents/LEGO/Lego Songbook"))
    # print(change_sheet_to_ext(load_songs(SONGS_CSV), SONGBOOK_DIR))
    # dump_songs(sort_songs(sync_local_songs(load_songs(SONGS_CSV), SONGBOOK_DIR),
    #                       sort_by_name),
    #            SONGS_CSV)
    # dump_songs(sort_songs(load_songs(SONGS_CSV), sort_by_key), SONGS_BY_KEY_CSV)
    pass
