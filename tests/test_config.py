from impresario.config import Config
from pathlib import Path


def test_load_existing_config(tmpdir):
    p = tmpdir.join("config.toml")
    p.write(
        """[paths]
site = "/path/to/site"
sheets = "/path/to/sheet"
"""
    )

    config_data = Config.load(Path(p))
    assert config_data._dict == {
        "paths": {"site": "/path/to/site", "sheets": "/path/to/sheet"}
    }


def test_set_config(tmpdir):
    p = tmpdir.join("config.toml")
    config = Config(site="/path/to/site", sheets="/path/to/sheet")
    config.write(Path(p))
    assert p.read() == """[paths]
site = "/path/to/site"
sheets = "/path/to/sheet"
"""
