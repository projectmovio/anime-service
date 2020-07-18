import json
import os
import shutil
import time
from unittest import mock

from sqs_handlers.post_anime import handle

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
ANIME_XML = os.path.join(CURRENT_DIR, "files", "anime.xml")

TEST_MAL_ID = "123"
TEST_MAL_RESPONSE = {
    "id": TEST_MAL_ID,
    "title": "Seikai no Monshou",
    "main_picture": {
        "medium": "https://api-cdn.myanimelist.net/images/anime/13/17405.jpg",
        "large": "https://api-cdn.myanimelist.net/images/anime/13/17405l.jpg"
    }
}
UPDATED_PARAM = ""


def download_file_mock(key, location):
    mocked_json_titles = {
        "Seikai no Monshou": 1
    }
    with open("titles.json", "w") as f:
        json.dump(mocked_json_titles, f)

    shutil.copy2("titles.json", location)
    return True


def download_file_mock_empty(key, location):
    mocked_json_titles = {}
    with open("titles.json", "w") as f:
        json.dump(mocked_json_titles, f)

    shutil.copy2("titles.json", location)
    return True


def update_item_params_mock(*a, **k):
    global UPDATED_PARAM
    UPDATED_PARAM = k["ExpressionAttributeValues"]


@mock.patch("requests.get")
def test_handle(mocked_get, mocked_params_db, mocked_anime_db, mocked_anidb, mocked_episodes_db):
    mocked_params_db.table.get_item.return_value = {
        "Item": {
            "last_run": int(time.time()) - 10
        }
    }
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    # MAL request mock
    mocked_get.return_value.status_code = 200
    mocked_get.return_value.json = lambda *a, **k: TEST_MAL_RESPONSE.copy()
    mocked_anidb.s3_bucket.download_file = download_file_mock
    # ANIDB request mock
    with open(ANIME_XML) as fs:
        mocked_get.return_value.text = fs.read()

    mocked_params_db.table.update_item = update_item_params_mock

    event = {
        "Records": [
            {
                "body": TEST_MAL_ID
            }
        ]
    }
    handle(event, None)

    assert ":last_run" in UPDATED_PARAM
    assert ":anime_id" in UPDATED_PARAM

    if os.path.isfile("titles.json"):
        os.remove("titles.json")


@mock.patch("requests.get")
def test_handle_to_early(mocked_get, mocked_params_db, mocked_anime_db, mocked_anidb, mocked_episodes_db):
    mocked_params_db.table.get_item.return_value = {
        "Item": {
            "last_run": int(time.time()) + 2
        }
    }
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    # MAL request mock
    mocked_get.return_value.status_code = 200
    mocked_get.return_value.json = lambda *a, **k: TEST_MAL_RESPONSE.copy()
    mocked_anidb.s3_bucket.download_file = download_file_mock
    # ANIDB request mock
    with open(ANIME_XML) as fs:
        mocked_get.return_value.text = fs.read()

    mocked_params_db.table.update_item = update_item_params_mock

    event = {
        "Records": [
            {
                "body": TEST_MAL_ID
            }
        ]
    }
    handle(event, None)

    assert ":last_run" in UPDATED_PARAM
    assert ":anime_id" in UPDATED_PARAM

    if os.path.isfile("titles.json"):
        os.remove("titles.json")


def test_handle_already_exist_skipped(mocked_params_db, mocked_anime_db, mocked_anidb, mocked_episodes_db):
    mocked_params_db.table.get_item.return_value = {
        "Item": {
            "last_run": int(time.time()) - 10
        }
    }
    mocked_anime_db.table.get_item.return_value = {
        "Item": TEST_MAL_RESPONSE
    }

    event = {
        "Records": [
            {
                "body": TEST_MAL_ID
            }
        ]
    }
    handle(event, None)


@mock.patch("requests.get")
def test_handle_no_anidb_match(mocked_get, mocked_params_db, mocked_anime_db, mocked_anidb, mocked_episodes_db):
    mocked_params_db.table.get_item.return_value = {
        "Item": {
            "last_run": int(time.time()) - 10
        }
    }
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    # MAL request mock
    mocked_get.return_value.status_code = 200
    mocked_get.return_value.json = lambda *a, **k: TEST_MAL_RESPONSE.copy()
    mocked_anidb.s3_bucket.download_file = download_file_mock_empty
    # ANIDB request mock
    with open(ANIME_XML) as fs:
        mocked_get.return_value.text = fs.read()

    mocked_params_db.table.update_item = update_item_params_mock

    event = {
        "Records": [
            {
                "body": TEST_MAL_ID
            }
        ]
    }
    handle(event, None)

    assert ":last_run" in UPDATED_PARAM
    assert ":anime_id" in UPDATED_PARAM

    if os.path.isfile("titles.json"):
        os.remove("titles.json")
