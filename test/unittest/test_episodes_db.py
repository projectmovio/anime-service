from unittest.mock import MagicMock
from dynamodb_json import json_util

import pytest


def test_get_episodes_not_found(mocked_episodes_db):
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": []}
    ]

    with pytest.raises(mocked_episodes_db.NotFoundError):
        mocked_episodes_db.get_episodes("123")


def test_get_episodes_with_limit(mocked_episodes_db):
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [json_util.dumps({"ep_name": "ep_1"})]},
        {"Items": [json_util.dumps({"ep_name": "ep_2"})]},
        {"Items": [json_util.dumps({"ep_name": "ep_3"})]},
    ]

    ret = mocked_episodes_db.get_episodes("123", limit=1)
    assert ret == {"items": [{"ep_name": "ep_1"}], "total": 3}


def test_get_episodes_with_offset(mocked_episodes_db):
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [json_util.dumps({"ep_name": "ep_1"})]},
        {"Items": [json_util.dumps({"ep_name": "ep_2"})]},
        {"Items": [json_util.dumps({"ep_name": "ep_3"})]},
    ]

    ret = mocked_episodes_db.get_episodes("123", limit=1, start=2)
    assert ret == {"items": [{"ep_name": "ep_2"}], "total": 3}


def test_get_episodes_with_to_large_offset(mocked_episodes_db):
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [json_util.dumps({"ep_name": "ep_1"})]},
        {"Items": [json_util.dumps({"ep_name": "ep_2"})]},
        {"Items": [json_util.dumps({"ep_name": "ep_3"})]},
    ]

    with pytest.raises(mocked_episodes_db.InvalidStartOffset):
        mocked_episodes_db.get_episodes("123", limit=1, start=4)


def test_get_episodes_with_to_small_offset(mocked_episodes_db):
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [json_util.dumps({"ep_name": "ep_1"})]},
        {"Items": [json_util.dumps({"ep_name": "ep_2"})]},
        {"Items": [json_util.dumps({"ep_name": "ep_3"})]},
    ]

    with pytest.raises(mocked_episodes_db.InvalidStartOffset):
        mocked_episodes_db.get_episodes("123", limit=1, start=0)


def test_episodes_generator(mocked_episodes_db):
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {
            "Items": [
                json_util.dumps({"ep_name": "ep_1"}),
                json_util.dumps({"ep_name": "ep_2"}),
                json_util.dumps({"ep_name": "ep_3"}),
            ]
        }
    ]

    eps = []
    for p in mocked_episodes_db._episodes_generator("TEST_ANIME_ID", 1):
        eps += p

    assert eps == [{"ep_name": "ep_1"}, {"ep_name": "ep_2"}, {"ep_name": "ep_3"}]


def test_episodes_generator_low_limit(mocked_episodes_db):
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [json_util.dumps({"ep_name": "ep_1"})]},
        {"Items": [json_util.dumps({"ep_name": "ep_2"})]},
        {"Items": [json_util.dumps({"ep_name": "ep_3"})]},
    ]

    eps = []
    for p in mocked_episodes_db._episodes_generator("TEST_ANIME_ID", 3):
        eps += p

    assert eps == [{"ep_name": "ep_1"}, {"ep_name": "ep_2"}, {"ep_name": "ep_3"}]
