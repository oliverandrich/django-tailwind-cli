from typing import Any

import pytest
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def mocked_calls(request: Any, mocker: MockerFixture):
    marker = request.node.get_closest_marker("mock_network_and_subprocess")
    if marker:
        mocker.resetall()
        mocker.patch("multiprocessing.Process.start")
        mocker.patch("multiprocessing.Process.join")
        mocker.patch("subprocess.run")
        mocker.patch("urllib.request.urlopen")
        mocker.patch("shutil.copyfileobj")
