import unittest

from service.api.anidb import AniDbApi


class TestAniDb(unittest.TestCase):
    def setUp(self):
        self.anidb = AniDbApi()

    def test_find_anime_id(self):
        self.anidb._find_anime_id("naruto")

    def test_find_anime_id_all(self):
        self.anidb._find_anime_id("")
