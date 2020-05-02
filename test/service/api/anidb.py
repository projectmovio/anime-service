import unittest

from python.anidb import AniDbApi


class TestAniDb(unittest.TestCase):
    def setUp(self):
        self.anidb = AniDbApi()

    def test_find_anime_id(self):
        self.anidb._find_anime_ids("naruto")

    def test_find_anime_id_all(self):
        self.anidb._find_anime_ids("")

    def test_parse_anime(self):
        self.anidb._parse_anime(open('test_anime.xml').read())
