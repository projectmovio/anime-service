import datetime
import logging
import os

from dataclasses import dataclass
from enum import Enum
from typing import List, NamedTuple, Optional

import requests

log = logging.getLogger(__name__)

CLIENT_ID = os.getenv("MAL_CLIENT_ID")


class Error(Exception):
    pass


class HTTPError(Error):
    pass


class NotFoundError(Error):
    pass


class MainPicture(NamedTuple):
    medium: str
    large: str


@dataclass
class BaseAnime:
    id: int
    title: str
    main_picture: MainPicture


class RelationType(Enum):
    SideStory = "side_story"
    Summary = "summary"
    AlternativeVersion = "alternative_version"
    Character = "character"
    Other = "other"
    Sequel = "sequel"
    Prequel = "prequel"


class RelatedAnime(NamedTuple):
    node: BaseAnime
    relation_type: RelationType


class AlternativeTitles(NamedTuple):
    synonyms: List[str]


class BroadCast(NamedTuple):
    day_of_week: str
    start_time: str


class MediaType(Enum):
    TV = "tv"
    Movie = "movie"
    OVA = "ova"
    ONA = "ona"
    Special = "special"


@dataclass
class Anime(BaseAnime):
    media_type: MediaType
    average_episode_duration: int
    synopsis: str
    num_episodes: int
    alternative_titles: Optional[AlternativeTitles] = None
    start_date: Optional[datetime.date] = ""
    end_date: Optional[str] = ""
    related_anime: Optional[List[RelatedAnime]] = list
    broadcast: Optional[BroadCast] = None

    @property
    def all_titles(self):
        titles = [self.title]

        for title_key in self.alternative_titles:
            t_list = self.alternative_titles[title_key]

            if not isinstance(t_list, list):
                t_list = [t_list]

            for t in t_list:
                if t not in titles:
                    titles.append(t)
        return titles


class MalApi:
    def __init__(self):
        self.default_headers = {
            "X-Mal-Client-Id": CLIENT_ID,
        }
        self.base_url = "https://api.myanimelist.net/v2"

        log.debug("MAL base_url: {}".format(self.base_url))

    def search(self, search_str: str) -> List[Anime]:
        url = f"{self.base_url}/anime"
        url_params = {"q": search_str}

        ret = requests.get(url, params=url_params, headers=self.default_headers)
        if ret.status_code != 200:
            raise HTTPError(f"Unexpected status code: {ret.status_code}")

        res = []
        for a in ret.json()["data"]:
            res.append(a["node"])
        return res

    def get_anime(self, anime_id: int) -> Anime:
        url = f"{self.base_url}/anime/{anime_id}"
        fields = [
            "related_anime", "alternative_titles", "media_type", "start_date", "end_date", "average_episode_duration",
            "synopsis", "broadcast", "num_episodes"
        ]
        url_params = {"fields": ",".join(fields)}
        ret = requests.get(url, params=url_params, headers=self.default_headers)
        if ret.status_code == 404:
            raise NotFoundError(f"Anime with ID: {anime_id} not found")
        elif ret.status_code != 200:
            raise HTTPError(f"Unexpected status code: {ret.status_code}")

        anime = Anime(**ret.json())

        return anime
