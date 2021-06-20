import json
from unittest.mock import MagicMock

import pytest

from api.anime_episodes import handle, UnsupportedMethod


def test_unsupported_method(mocked_anime_db):
    event = {
        "requestContext": {
            "http": {
                "method": "AA"
            }
        },
        "pathParameters": {
            "id": "123"
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    with pytest.raises(UnsupportedMethod):
        handle(event, None)


class TestPostEpisode:
    post_event = {
        "pathParameters": {
            "id": "123"
        },
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "body": '{ "api_name": "anidb", "api_id": "456"}'
    }

    def test_success(self, mocked_episodes_db, mocked_anime):
        mocked_episodes_db.table.query.return_value = {
            "Items": [
                {
                    "anidb_id": "456"
                }
            ],
            "Count": 1
        }
        mocked_anime.sqs_queue.send_message.return_value = True

        res = handle(self.post_event, None)

        exp = {
            "body": json.dumps({"anidb_id": "456"}),
            "statusCode": 200
        }
        assert res == exp

    def test_not_found(self, mocked_episodes_db, mocked_anime):
        mocked_episodes_db.table.query.side_effect = mocked_episodes_db.NotFoundError
        mocked_anime.sqs_queue.send_message.return_value = True

        res = handle(self.post_event, None)

        exp = {
            "statusCode": 404
        }
        assert res == exp

    def test_no_body(self, mocked_anime_db):
        mocked_anime_db.table.query.return_value = {
            "Items": [
                {
                    "mal_id": "123"
                }
            ]
        }
        event = {
            "requestContext": {
                "http": {
                    "method": "POST"
                }
            },
            "pathParameters": {
                "id": "123"
            },
            "body": {}
        }

        res = handle(event, None)

        exp = {
            "statusCode": 400,
            "body": "Invalid post body"
        }
        assert res == exp

    def test_invalid_api_name(self, mocked_anime_db):
        mocked_anime_db.table.query.return_value = {
            "Items": [
                {
                    "mal_id": 123
                }
            ]
        }
        event = {
            "requestContext": {
                "http": {
                    "method": "POST"
                }
            },
            "pathParameters": {
                "id": "123"
            },
            "body": '{ "api_name": "bad_name", "api_id": "123"}'
        }
        res = handle(event, None)

        exp = {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Invalid post schema",
                "error": "\'bad_name\' is not one of [\'anidb\']",
            })
        }
        assert res == exp


class TestGetEpisodes:
    event = {
        "pathParameters": {
            "id": "123"
        },
        "queryStringParameters": {},
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }

    def test_success(self, mocked_episodes_db):
        exp_eps = [
            {
                "id": "1",
                "title": "ep1",
            },
            {
                "id": "2",
                "title": "ep2",
            }
        ]
        m = MagicMock()
        mocked_episodes_db.client.get_paginator.return_value = m
        m.paginate.return_value = [
            {"Items": exp_eps}
        ]

        res = handle(self.event, None)

        exp = {
            "statusCode": 200,
            "body": json.dumps({"items": exp_eps, "total_pages": 1})
        }
        assert res == exp

    def test_not_found(self, mocked_episodes_db):
        m = MagicMock()
        mocked_episodes_db.client.get_paginator.return_value = m
        m.paginate.return_value = [
            {"Items": []}
        ]

        res = handle(self.event, None)

        exp = {
            "statusCode": 404,
        }
        assert res == exp

    def test_with_limit(self, mocked_episodes_db):
        exp_eps = [
            {
                "id": "1",
                "title": "ep1",
            },
            {
                "id": "2",
                "title": "ep2",
            }
        ]
        m = MagicMock()
        mocked_episodes_db.client.get_paginator.return_value = m
        m.paginate.return_value = [
            {"Items": [exp_eps[0]]},
            {"Items": [exp_eps[1]]}
        ]

        event = self.event.copy()
        event["queryStringParameters"] = {
            "limit": 1
        }

        res = handle(event, None)

        exp = {
            "statusCode": 200,
            "body": json.dumps({"items": [exp_eps[0]], "total_pages": 2})
        }
        assert res == exp

    def test_start(self, mocked_episodes_db):
        exp_eps = [
            {
                "id": "1",
                "title": "ep1",
            },
            {
                "id": "2",
                "title": "ep2",
            }
        ]
        m = MagicMock()
        mocked_episodes_db.client.get_paginator.return_value = m
        m.paginate.return_value = [
            {"Items": [exp_eps[0]]},
            {"Items": [exp_eps[1]]}
        ]

        event = self.event.copy()
        event["queryStringParameters"] = {
            "start": 2
        }

        res = handle(event, None)

        exp = {
            "statusCode": 200,
            "body": json.dumps({"items": [exp_eps[1]], "total_pages": 2})
        }
        assert res == exp

    def test_limit_and_start(self, mocked_episodes_db):
        exp_eps = [
            {
                "id": "1",
                "title": "ep1",
            },
            {
                "id": "2",
                "title": "ep2",
            }
        ]
        m = MagicMock()
        mocked_episodes_db.client.get_paginator.return_value = m
        m.paginate.return_value = [
            {"Items": [exp_eps[0]]},
            {"Items": [exp_eps[1]]}
        ]

        event = self.event.copy()
        event["queryStringParameters"] = {
            "limit": 1,
            "start": 2
        }

        res = handle(event, None)

        exp = {
            "statusCode": 200,
            "body": json.dumps({"items": [exp_eps[1]], "total_pages": 2})
        }
        assert res == exp

    def test_invalid_limit_type(self, mocked_episodes_db):
        exp_eps = [
            {
                "id": "1",
                "title": "ep1",
            },
            {
                "id": "2",
                "title": "ep2",
            }
        ]
        m = MagicMock()
        mocked_episodes_db.client.get_paginator.return_value = m
        m.paginate.return_value = [
            {"Items": [exp_eps[0]]},
            {"Items": [exp_eps[1]]}
        ]

        event = self.event.copy()
        event["queryStringParameters"] = {
            "limit": "abc",
            "start": 2
        }

        res = handle(event, None)

        exp = {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid limit type"})
        }
        assert res == exp

    def test_invalid_start_type(self, mocked_episodes_db):
        exp_eps = [
            {
                "id": "1",
                "title": "ep1",
            },
            {
                "id": "2",
                "title": "ep2",
            }
        ]
        m = MagicMock()
        mocked_episodes_db.client.get_paginator.return_value = m
        m.paginate.return_value = [
            {"Items": [exp_eps[0]]},
            {"Items": [exp_eps[1]]}
        ]

        event = self.event.copy()
        event["queryStringParameters"] = {
            "limit": 1,
            "start": "abc"
        }

        res = handle(event, None)

        exp = {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid start type"})
        }
        assert res == exp

    def test_invalid_offset(self, mocked_episodes_db):
        exp_eps = [
            {
                "id": "1",
                "title": "ep1",
            },
            {
                "id": "2",
                "title": "ep2",
            }
        ]
        m = MagicMock()
        mocked_episodes_db.client.get_paginator.return_value = m
        m.paginate.return_value = [
            {"Items": [exp_eps[0]]},
            {"Items": [exp_eps[1]]}
        ]

        event = self.event.copy()
        event["queryStringParameters"] = {
            "limit": 1,
            "start": 0
        }

        res = handle(event, None)

        exp = {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid offset"})
        }
        assert res == exp


class TestGetEpisodeByApiId:
    event = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
            "api_id": "123",
            "api_name": "anidb",
        },
        "pathParameters": {
            "id": "123"
        },
    }

    def test_success(self, mocked_episodes_db):
        mocked_episodes_db.table.query.return_value = {
            "Items": [
                {
                    "anidb_id": "456"
                }
            ],
            "Count": 1
        }

        res = handle(self.event, None)

        exp = {
            "body": json.dumps({"anidb_id": "456"}),
            "statusCode": 200
        }
        assert res == exp

    def test_not_found(self, mocked_episodes_db):
        mocked_episodes_db.table.query.side_effect = mocked_episodes_db.NotFoundError

        res = handle(self.event, None)

        exp = {
            "statusCode": 404,
        }
        assert res == exp

    def test_invalid_api_name(self):
        event = self.event.copy()
        event["queryStringParameters"]["api_name"] = "invalid"

        res = handle(self.event, None)

        exp = {"body": '{"error": "Unsupported query param"}',
               "statusCode": 400}
        assert res == exp
