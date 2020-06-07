import datetime
import logging
import os

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

import requests

log = logging.getLogger(__name__)

CLIENT_ID = os.getenv("MAL_CLIENT_ID")


class Error(Exception):
    pass


class HTTPError(Error):
    pass


class NotFoundError(Error):
    pass


@dataclass
class MainPicture:
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


@dataclass
class RelatedAnime:
    node: BaseAnime
    relation_type: RelationType


@dataclass
class BroadCast:
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
    alternative_titles: Optional[dict] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    related_anime: Optional[List[RelatedAnime]] = list
    broadcast: Optional[BroadCast] = None

    def __post_init__(self):
        if self.start_date is not None:
            self.start_date = datetime.datetime.strptime(self.start_date, "%Y-%m-%d")

        if self.end_date is not None:
            self.start_date = datetime.datetime.strptime(self.start_date, "%Y-%m-%d")

    @property
    def all_titles(self):
        titles = [self.title]

        if self.alternative_titles is not None:
            if "synonyms" in self.alternative_titles:
                titles += self.alternative_titles.pop("synonyms")
            for t in self.alternative_titles:
                if t not in titles:
                    titles.append(self.alternative_titles[t])

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
