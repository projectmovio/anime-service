import filecmp
import gzip
import json
import os
import shutil
from unittest import mock
from unittest.mock import MagicMock

import pytest

from crons.titles_updater import handle

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_TITLES = os.path.join(CURRENT_DIR, "files", "titles.xml")


@pytest.fixture
def mocked_anidb():
    import anidb

    anidb.s3_bucket = MagicMock()

    return anidb


def download_file_mock(key, location):
    shutil.copy2(TEST_TITLES, location)
    return True


def test_handler(mocked_anidb):
    mocked_anidb.s3_bucket.download_file = download_file_mock
    mocked_anidb.s3_bucket.upload_file.return_value = True

    xml_path, json_path = handle(None, None)

    assert filecmp.cmp(xml_path, TEST_TITLES)

    exp_json_titles = {'CotS': 1, 'Crest of the Stars': 1, 'Hvězdný erb': 1, 'Seikai no Monshou': 1, 'SnM': 1,
                       '星界の紋章': 1, '星界之纹章': 1}
    with open(json_path) as fs:
        assert exp_json_titles == json.load(fs)


@mock.patch("requests.get")
def test_handler_no_s3_file(mocked_get, mocked_anidb):
    mocked_anidb.s3_bucket.download_file.return_value = False
    mocked_anidb.s3_bucket.upload_file.return_value = True

    # Create test gzip
    titles_gzip = os.path.join(CURRENT_DIR, "test_titles.gz")
    with gzip.open(titles_gzip, 'wb') as gz:
        with open(TEST_TITLES, "rb") as f:
            gz.write(f.read())

    mocked_get.return_value = titles_gzip

    xml_path, json_path = handle(None, None)

    assert filecmp.cmp(xml_path, TEST_TITLES)

    exp_json_titles = {'CotS': 1, 'Crest of the Stars': 1, 'Hvězdný erb': 1, 'Seikai no Monshou': 1, 'SnM': 1,
                       '星界の紋章': 1, '星界之纹章': 1}
    with open(json_path) as fs:
        assert exp_json_titles == json.load(fs)

    if os.path.isfile(titles_gzip):
        os.remove(titles_gzip)
