import datetime
import gzip
import json
import os
import shutil
from unittest import mock

import pytest
from botocore.exceptions import ClientError

from anidb import AniDbApi, HTTPError

ENV = {
    "ANIDB_CLIENT": "TEST_ANIDB_CLIENT",
    "ANIDB_CLIENT_VERSION": "TEST_ANIDB_CLIENT_VERSION",
    "ANIDB_PROTOCOL_VERSION": "TEST_ANIDB_PROTOCOL_VERSION",
    "ANIDB_TITLES_BUCKET": "TEST_ANIDB_TITLES_BUCKET"
}
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

now = datetime.datetime.now()
date_today = now.strftime("%Y-%m-%d")
date_yesterday = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")


def download_file_mock(key, location):
    if key == f"{date_today}.json":
        return False

    mocked_download_content = {
        "Seikai no Monshou": 1
    }
    with open("titles.json", "w") as f:
        json.dump(mocked_download_content, f)

    shutil.copy2("titles.json", location)
    return True


@mock.patch.dict(os.environ, ENV)
@mock.patch("requests.get")
def test_get_anime(mocked_get):
    mocked_get.return_value.status_code = 200

    test_anime_path = os.path.join(CURRENT_DIR, "files", "anime.xml")
    with open(test_anime_path, "r") as f:
        xml_response = f.read().replace("\n", "")

    mocked_get.return_value.text = xml_response

    anidb_api = AniDbApi()
    ret = anidb_api.get_anime(123)

    assert "anime" in ret
    assert "anidb_id" in ret["anime"]
    assert ret["anime"]["anidb_id"] == "11123"
    assert "episodes" in ret["anime"]

    found_exp_eps = 0
    for ep in ret["anime"]["episodes"]:
        if ep["episode_number"] == 10:
            found_exp_eps += 1
        if ep["episode_number"] == -2:
            found_exp_eps += 1
    assert found_exp_eps == 2


@mock.patch.dict(os.environ, ENV)
@mock.patch("requests.get")
def test_get_anime_error(mocked_get):
    mocked_get.return_value.status_code = 500

    anidb_api = AniDbApi()

    with pytest.raises(HTTPError) as e:
        anidb_api.get_anime(123)

    assert "Unexpected status code: 500" == str(e.value)


@mock.patch.dict(os.environ, ENV)
@mock.patch("requests.get")
@mock.patch("anidb._download_file")
def test_download_xml(mocked_download_file, mocked_get, mocked_anidb):
    mocked_get.return_value.status_code = 200
    mocked_download_file.return_value = None
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
    mocked_anidb.download_xml(out_file)
    with open(out_file, "r") as f:
        out_data = f.read()

    assert out_data == exp

    # cleanup
    os.remove(file_name)
    os.remove(out_file)


@mock.patch.dict(os.environ, ENV)
@mock.patch("requests.get")
@mock.patch("anidb._download_file")
def test_download_xml_wrong_status(mocked_download_file, mocked_get, mocked_anidb):
    mocked_get.return_value.status_code = 403
    mocked_download_file.return_value = None
    mocked_anidb.s3_bucket.upload_file.return_value = True

    with pytest.raises(mocked_anidb.HTTPError):
        mocked_anidb.download_xml("downloaded.xml")


@mock.patch.dict(os.environ, ENV)
def test_save_json_titles(mocked_anidb):
    mocked_anidb.upload_file = lambda *args: None
    titles_path = os.path.join(CURRENT_DIR, "files", "titles.xml")

    out_path = os.path.join(CURRENT_DIR, "test.json")
    mocked_anidb.save_json_titles(titles_path, out_path)

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


@mock.patch.dict(os.environ, ENV)
def test_download_file(mocked_anidb):
    mocked_anidb.s3_bucket.download_file.return_value = True
    open("test.json", "w").close()

    ret = mocked_anidb._download_file("TEST", "test.json")
    assert ret

    if os.path.isfile("test.json"):
        os.remove("test.json")


@mock.patch.dict(os.environ, ENV)
def test_download_file_not_found(mocked_anidb):
    mocked_anidb.s3_bucket.download_file.side_effect = ClientError({"Error": {"Code": "404"}}, "TEST_OPERATION")

    ret = mocked_anidb._download_file("TEST", "TEST")
    assert not ret


@mock.patch.dict(os.environ, ENV)
def test_download_file_error(mocked_anidb):
    mocked_anidb.s3_bucket.download_file.side_effect = ClientError({"Error": {"Code": "500"}}, "TEST_OPERATION")

    with pytest.raises(ClientError):
        mocked_anidb._download_file("TEST", "TEST")


@mock.patch.dict(os.environ, ENV)
def test_get_json_titles_yesterday_file(mocked_anidb):
    mocked_anidb.s3_bucket.download_file = download_file_mock

    mocked_anidb.get_json_titles(CURRENT_DIR)

    # Cleanup
    if os.path.isfile(os.path.join(CURRENT_DIR, f"{date_yesterday}.json")):
        os.remove(os.path.join(CURRENT_DIR, f"{date_yesterday}.json"))


@mock.patch.dict(os.environ, ENV)
def test_get_json_titles_no_file(mocked_anidb):
    mocked_anidb.s3_bucket.download_file.return_value = False

    with pytest.raises(mocked_anidb.TitlesNotFound):
        mocked_anidb.get_json_titles(CURRENT_DIR)
