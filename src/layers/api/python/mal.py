import logging
import os
import uuid
from enum import Enum
from typing import NamedTuple, TypedDict, Dict, List

import requests

log = logging.getLogger(__name__)

CLIENT_ID = os.getenv("MAL_CLIENT_ID")


class Error(Exception):
    pass


class HTTPError(Error):
    pass


class NotFoundError(Error):
    pass


class MainPicture(TypedDict):
    medium: str
    large: str


class BaseAnime(TypedDict):
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

class RelatedAnime(TypedDict):
    node: BaseAnime
    relation_type: RelationType

class AlternativeTitles(TypedDict):
    synonyms: List[str]


class BroadCast(TypedDict):
    day_of_week: str
    start_time: str


class MediaType(Enum):
    TV = "tv"
    Movie = "movie"
    OVA = "ova"
    ONA = "ona"
    Special = "special"


class Anime(BaseAnime):
    related_anime: List[RelatedAnime]
    alternative_titles: AlternativeTitles
    media_type: MediaType
    start_date: str
    end_date: str
    average_episode_duration: int
    synopsis: str
    broadcast: BroadCast
    num_episodes: int


class MalApi:
    def __init__(self):
        self.default_headers = {
            "X-Mal-Client-Id": CLIENT_ID,
        }
        self.base_url = "https://api.myanimelist.net/v2"

        log.debug("MAL base_url: {}".format(self.base_url))

    def search(self, search_str: str):
        url = f"{self.base_url}/anime"
        url_params = {"q": search_str}

        ret = requests.get(url, params=url_params, headers=self.default_headers)
        if ret.status_code != 200:
            raise HTTPError(f"Unexpected status code: {ret.status_code}")

        res = {"anime": []}
        for a in ret.json()["data"]:
            res["anime"].append(a["node"])
        return res

    def get_anime(self, anime_id: uuid.UUID) -> Anime:
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

        anime = ret.json()
        anime["all_titles"] = self._get_all_titles(anime)

        # Change id into mal_id, this way this dict can be easy transformed into db item
        anime["mal_id"] = anime.pop("id")

        return {"anime": anime}

    def _get_all_titles(self, anime):
        titles = [anime["title"]]

        for title_key in anime["alternative_titles"]:
            t_list = anime["alternative_titles"][title_key]

            if not isinstance(t_list, list):
                t_list = [t_list]

            for t in t_list:
                if t not in titles:
                    titles.append(t)
        return titles
