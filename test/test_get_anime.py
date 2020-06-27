from unittest.mock import MagicMock

import pytest

from api.get_anime import handle


@pytest.fixture
def mocked_anime_db():
    import anime_db

    anime_db.table = MagicMock()

    return anime_db


def test_handler(mocked_anime_db):
    exp_item = {
        "id": "123",
        "title": "naruto",
    }
    mocked_anime_db.table.query.return_value = {
        "Items": [
            exp_item
        ]
    }
    event = {
        "pathParameters": {
            "anime_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": exp_item
    }
    assert res == exp


def test_handler_not_found(mocked_anime_db):
    mocked_anime_db.table.query.side_effect = mocked_anime_db.NotFoundError
    event = {
        "pathParameters": {
            "anime_id": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 404,
    }
    assert res == exp
