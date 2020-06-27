from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mocked_anime_db():
    import api.post_anime
    import anime_db

    api.post_anime.sqs_queue = MagicMock()
    anime_db.table = MagicMock()

    return api.post_anime, anime_db


def test_handler(mocked_anime_db):
    mocked_post_anime, anime_db = mocked_anime_db

    anime_db.table.query.side_effect = anime_db.NotFoundError
    event = {
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    res = mocked_post_anime.handle(event, None)

    exp = {
        "statusCode": 202,
    }
    assert res == exp

