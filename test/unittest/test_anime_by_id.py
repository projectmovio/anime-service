import json

import pytest

from api.anime_by_id import handle
from dynamodb_json import json_util


def test_handler(mocked_anime_db):
    exp_item = {
        "id": "123",
        "title": "naruto",
    }
    mocked_anime_db.table.get_item.return_value = {"Item": exp_item}
    event = {
        "pathParameters": {
            "id": "123"
        }
    }

    res = handle(event, None)

    exp = {'body': '{"id": "123", "title": "naruto"}', 'statusCode': 200}
    assert res == exp


def test_handler_not_found(mocked_anime_db):
    mocked_anime_db.table.get_item.side_effect = mocked_anime_db.NotFoundError
    event = {
        "pathParameters": {
            "ids": "123"
        }
    }

    res = handle(event, None)

    exp = {'statusCode': 404}
    assert res == exp
