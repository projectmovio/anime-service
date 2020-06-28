from unittest.mock import MagicMock
import anidb
import pytest

download_func = anidb._download_file


@pytest.fixture(scope='function')
def mocked_anidb():
    anidb.s3_bucket = MagicMock()
    anidb._download_file = download_func

    return anidb


@pytest.fixture(scope='function')
def mocked_mal():
    import mal

    mal.MalApi = MagicMock()

    return mal


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
def mocked_post_anime():
    import api.post_anime

    api.post_anime.sqs_queue = MagicMock()

    return api.post_anime
