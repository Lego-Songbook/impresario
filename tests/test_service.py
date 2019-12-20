from datetime import date

import pytest
from impresario.service import Service

SERVICE_YAML = """- date: 2019-09-22
  lead_singer: 领唱
  vocals: 
      - 伴唱
  instrumentation:
      - instrument: 键盘
        player: 键盘手
  songs:
      - 歌曲1
      - 歌曲2
      - 歌曲3
"""


@pytest.mark.xfail
def test_service_from_yaml():
    services = Service.from_yaml(source_document=SERVICE_YAML)
    assert len(services) == 1
    assert services[0].date == date(2019, 9, 22)
