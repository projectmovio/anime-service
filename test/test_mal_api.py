import os
from unittest import mock
from unittest.mock import patch

import requests

from mal import MalApi

ENV = {
    "MAL_CLIENT_ID": "TEST_MAL_CLIENT_ID"
}


@mock.patch.dict(os.environ, ENV)
@patch.object(requests, "get")
def test_search(req_mock):
    exp = {
        "anime": [
            {
                "id": 20,
                "title": "Naruto",
                "main_picture": {
                    "medium": "https:\/\/api-cdn.myanimelist.net\/images\/anime\/13\/17405.jpg",
                    "large": "https:\/\/api-cdn.myanimelist.net\/images\/anime\/13\/17405l.jpg"
                },
            }
        ]
    }

    req_mock.return_value.status_code = 200
    req_mock.return_value.json.return_value = {
        "data": [
            {
                "node": exp["anime"][0]
            }
        ]
    }

    mal_api = MalApi()
    ret = mal_api.search("Naruto")
    assert ret == exp
