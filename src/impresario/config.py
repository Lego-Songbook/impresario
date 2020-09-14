from pathlib import Path
from typing import ClassVar

from appdirs import AppDirs
import toml
import attr


def get_config_file() -> Path:
    config_dir = AppDirs("impresario").user_config_dir
    config_file = Path(config_dir) / "config.toml"
    return config_file


@attr.s(auto_attribs=True)
class Config:
    """The configurations of the app.

    Loading all configurations:
        >>> configs = Config.load()

    """

    site: str
    sheets: str

    @property
    def _dict(self):
        return {
            "paths":
                {
                    "site": self.site,
                    "sheets": self.sheets,
                }
        }

    @classmethod
    def default_config_file(cls) -> Path:
        config_dir = AppDirs("impresario").user_config_dir
        config_file = Path(config_dir) / "config.toml"
        return config_file

    @classmethod
    def load(cls, file=None) -> "Config":
        """Load the configs."""
        file = file or cls.default_config_file()
        configs = toml.load(file)
        return cls(site=configs["paths"]["site"], sheets=configs[
            "paths"]["sheets"])

    def write(self, file=None):
        """Write the configs to a file."""
        config_file = file or self.default_config_file()
        if not config_file.exists():
            config_file.touch()
        with config_file.open("w") as file:
            toml.dump(self._dict, file)
        return True

    def check(self) -> bool:
        if self.site and self.sheets:
            return True
        else:
            return False
