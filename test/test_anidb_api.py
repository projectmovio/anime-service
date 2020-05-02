import os
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
import requests

from anidb import AniDbApi, HTTPError

ENV = {
    "ANIDB_CLIENT": "TEST_ANIDB_CLIENT",
    "ANIDB_CLIENT_VERSION": "TEST_ANIDB_CLIENT_VERSION",
    "ANIDB_PROTOCOL_VERSION": "TEST_ANIDB_PROTOCOL_VERSION",
    "ANIDB_TITLES_BUCKET": "TEST_ANIDB_TITLES_BUCKET"
}
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

@pytest.fixture
def mocked_handler():
    import anidb

    anidb.s3_bucket = MagicMock()

    return anidb


@mock.patch.dict(os.environ, ENV)
@patch.object(requests, "get")
def test_get_anime(mocked_get):
    mocked_get.return_value.status_code = 200

    test_anime_path = os.path.join(CURRENT_DIR, "files", "test_anime.xml")
    with open(test_anime_path, "r") as f:
        xml_response = f.read().replace('\n', '')

    mocked_get.return_value.text = xml_response

    anidb_api = AniDbApi()
    ret = anidb_api.get_anime(123)

    assert "anime" in ret
    assert "anime_id" in ret["anime"]
    assert ret["anime"]["anime_id"] == "1"
    assert ret["anime"]["title"] == "Seikai no Monshou"


@mock.patch.dict(os.environ, ENV)
@patch.object(requests, "get")
def test_get_anime_error(mocked_get):
    mocked_get.return_value.status_code = 500

    anidb_api = AniDbApi()

    with pytest.raises(HTTPError) as e:
        anidb_api.get_anime(123)

    assert "Unexpected status code: 500" == str(e.value)
