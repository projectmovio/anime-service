import os
from unittest.mock import MagicMock
import pytest

os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture(scope='function')
def mocked_anidb():
    import anidb

    anidb.s3_bucket = MagicMock()

    return anidb



@pytest.fixture(scope='function')
def mocked_anime_db():
    import anime_db

    anime_db.table = MagicMock()

    return anime_db


@pytest.fixture(scope='function')
def mocked_episodes_db():
    import episodes_db

    episodes_db.table = MagicMock()

    return episodes_db


@pytest.fixture(scope='function')
def mocked_anime():
    import api.anime

    api.anime.sqs_queue = MagicMock()

    return api.anime


@pytest.fixture(scope='function')
def mocked_params_db():
    import params_db

    params_db.table = MagicMock()

    return params_db
