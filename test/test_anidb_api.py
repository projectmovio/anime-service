import gzip
import json
import os
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
import requests

from anidb import AniDbApi, HTTPError, download_xml, save_json_titles

ENV = {
    "ANIDB_CLIENT": "TEST_ANIDB_CLIENT",
    "ANIDB_CLIENT_VERSION": "TEST_ANIDB_CLIENT_VERSION",
    "ANIDB_PROTOCOL_VERSION": "TEST_ANIDB_PROTOCOL_VERSION",
    "ANIDB_TITLES_BUCKET": "TEST_ANIDB_TITLES_BUCKET"
}
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def mocked_anidb():
    import anidb

    anidb.s3_bucket = MagicMock()

    return anidb


@mock.patch.dict(os.environ, ENV)
@patch.object(requests, "get")
def test_get_anime(mocked_get):
    mocked_get.return_value.status_code = 200

    test_anime_path = os.path.join(CURRENT_DIR, "files", "anime.xml")
    with open(test_anime_path, "r") as f:
        xml_response = f.read().replace("\n", "")

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


@mock.patch.dict(os.environ, ENV)
@patch.object(requests, "get")
def test_download_xml(mocked_get, mocked_anidb):
    mocked_get.return_value.status_code = 200
    mocked_anidb._download_file = lambda *args: None
    mocked_anidb.s3_bucket.upload_file.return_value = True

    # create gzipped titles
    file_name = "test_titles.gz"
    titles_path = os.path.join(CURRENT_DIR, "files", "titles.xml")

    with open(titles_path, "r") as f:
        exp = f.read()
    with open(titles_path, "rb") as f_in, gzip.open(file_name, "wb") as f_out:
        f_out.writelines(f_in)
    with open(file_name, "br") as f:
        mocked_get.return_value.content = f.read()

    out_file = "downloaded.xml"
    download_xml(out_file)
    with open(out_file, "r") as f:
        out_data = f.read()

    assert out_data == exp

    # cleanup
    os.remove(file_name)
    os.remove(out_file)


@mock.patch.dict(os.environ, ENV)
def test_save_json_titles(mocked_anidb):
    mocked_anidb.upload_file = lambda *args: None
    titles_path = os.path.join(CURRENT_DIR, "files", "titles.xml")

    out_path = os.path.join(CURRENT_DIR, "test.json")
    save_json_titles(titles_path, out_path)

    with open(out_path, "r") as f:
        json_data = json.load(f)

    exp = {
        "CotS": 1,
        "Crest of the Stars": 1,
        "Hvězdný erb": 1,
        "Seikai no Monshou": 1,
        "SnM": 1,
        "星界の紋章": 1,
        "星界之纹章": 1
    }

    assert json_data == exp

    # cleanup
    os.remove(out_path)
