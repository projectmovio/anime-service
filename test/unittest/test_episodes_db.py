from datetime import date
from unittest.mock import MagicMock
from dynamodb_json import json_util

import pytest

TEST_ANIME_ID = "d8451df1-d25a-4ee6-a11a-1505b870c233"

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
    assert ret == {"items": [{"ep_name": "ep_1"}], "total_pages": 3}


def test_get_episodes_with_offset(mocked_episodes_db):
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [json_util.dumps({"ep_name": "ep_1"})]},
        {"Items": [json_util.dumps({"ep_name": "ep_2"})]},
        {"Items": [json_util.dumps({"ep_name": "ep_3"})]},
    ]

    ret = mocked_episodes_db.get_episodes("123", limit=1, start=2)
    assert ret == {"items": [{"ep_name": "ep_2"}], "total_pages": 3}


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
    for p in mocked_episodes_db._episodes_generator(TEST_ANIME_ID, 1):
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
    for p in mocked_episodes_db._episodes_generator(TEST_ANIME_ID, 3):
        eps += p

    assert eps == [{"ep_name": "ep_1"}, {"ep_name": "ep_2"}, {"ep_name": "ep_3"}]


def test_get_episode(mocked_episodes_db):
    mocked_episodes_db.table.query.return_value = {
        "Items": [
            {"ep_name": "ep_1"}
        ],
        "Count": 1,
    }

    ret = mocked_episodes_db.get_episode(TEST_ANIME_ID, "TEST_EPISODE_ID")
    assert ret == {"ep_name": "ep_1", "id_links": {}}


def test_get_episode_with_previous_link(mocked_episodes_db):
    mocked_episodes_db.table.query.return_value = {
        "Items": [
            {
                "ep_name": "ep_1",
                "episode_number": 2
            }
        ],
        "Count": 1,
    }

    ret = mocked_episodes_db.get_episode(TEST_ANIME_ID, "TEST_EPISODE_ID")
    assert ret == {
        "ep_name": "ep_1",
        "episode_number": 2,
        "id_links": {"previous": "fe94c8c6-1b4a-56c2-ad8e-2d779562fbb0"}
    }


def test_get_episode_with_next_link(mocked_episodes_db):
    date_today_str = date.today().strftime("%Y-%m-%d")
    mocked_episodes_db.table.query.return_value = {
        "Items": [
            {
                "ep_name": "ep_1",
                "episode_number": 1,
                "air_date": date_today_str
            }
        ],
        "Count": 1,
    }

    ret = mocked_episodes_db.get_episode(TEST_ANIME_ID, "TEST_EPISODE_ID")
    assert ret == {
        "ep_name": "ep_1",
        "episode_number": 1,
        "air_date": date_today_str,
        "id_links": {"next": "ad200b86-369c-5215-9895-b56c53bfd743"}
    }


def test_get_episode_empty_items_response(mocked_episodes_db):
    mocked_episodes_db.table.query.return_value = {
        "Items": [],
        "Count": 1,
    }

    with pytest.raises(mocked_episodes_db.NotFoundError):
        mocked_episodes_db.get_episode(TEST_ANIME_ID, "TEST_EPISODE_ID")


def test_get_episode_no_items_field(mocked_episodes_db):
    mocked_episodes_db.table.query.return_value = {
        "Count": 1,
    }

    with pytest.raises(mocked_episodes_db.NotFoundError):
        mocked_episodes_db.get_episode(TEST_ANIME_ID, "TEST_EPISODE_ID")


def test_get_episode_count_not_one(mocked_episodes_db):
    mocked_episodes_db.table.query.return_value = {
        "Items": [
            {"ep_name": "ep_1"}
        ],
        "Count": 10,
    }

    with pytest.raises(mocked_episodes_db.InvalidAmountOfEpisodes):
        mocked_episodes_db.get_episode(TEST_ANIME_ID, "TEST_EPISODE_ID")
