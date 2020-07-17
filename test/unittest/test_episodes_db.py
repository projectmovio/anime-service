from unittest.mock import MagicMock

import pytest


def test_get_episodes_not_found(mocked_episodes_db):
    mocked_episodes_db.table.query.return_value = {
        "Items": []
    }

    with pytest.raises(mocked_episodes_db.NotFoundError):
        mocked_episodes_db.get_episodes("123")


def test_episodes_generator(mocked_episodes_db):
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [{"ep_1"}, {"ep_2"}, {"ep_3"}]}
    ]

    eps = []
    for p in mocked_episodes_db._episodes_generator("TEST_ANIME_ID", 1):
        eps += p

    assert eps == [{"ep_1"}, {"ep_2"}, {"ep_3"}]


def test_episodes_generator_low_limit(mocked_episodes_db):
    m = MagicMock()
    mocked_episodes_db.client.get_paginator.return_value = m
    m.paginate.return_value = [
        {"Items": [{"ep_1"}]},
        {"Items": [{"ep_2"}]},
        {"Items": [{"ep_3"}]},
    ]

    eps = []
    for p in mocked_episodes_db._episodes_generator("TEST_ANIME_ID", 3):
        eps += p

    assert eps == [{"ep_1"}, {"ep_2"}, {"ep_3"}]
