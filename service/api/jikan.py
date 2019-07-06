import logging

import requests
from flask import jsonify

from config.config import Config

log = logging.getLogger(__name__)


class JikanApi:
    def __init__(self):
        self.config = Config()
        self.base_url = self.config.jikan_base_url

    def search(self, search_string):
        url = "{}/search/anime?q={}".format(self.base_url, search_string)
        log.debug("Sending get request to: %s", url)
        response = requests.get(url).json()

        result = []
        for anime in response["results"]:
            result += self._parse_anime(anime)
        return jsonify(anime=result)

    def get_anime(self, anime_id):
        url = "{}/search/anime/{}".format(self.base_url, anime_id)
        log.debug("Sending get request to: %s", url)
        response = requests.get(url).json()

        result = self._parse_anime(response)

        page = 1
        max_page = -1
        episodes = []
        while page != max_page:
            if max_page != -1:
                url = "{}/anime/{}/episodes/{}".format(self.base_url, anime_id, page)
                log.debug("Sending get request to: %s", url)
                response = requests.get(url).json()
            else:
                max_page = response["episodes_last_page"]

            page += 1
            episodes += response["episodes"]
        result["episodes"] = episodes

        return jsonify(episodes=episodes)

        return jsonify(anime=result)

    def _get_episodes(self, anime_id):
        page = 1
        max_page = -1
        episodes = []
        while page != max_page:
            url = "{}/anime/{}/episodes/{}".format(self.base_url, anime_id, page)
            log.debug("Sending get request to: %s", url)
            response = requests.get(url).json()
            max_page = response["episodes_last_page"]
            page += 1
            episodes += response["episodes"]
        return jsonify(episodes=episodes)

    def _parse_anime(self, anime_json, with_episodes=True):
        res = dict()
        res["anime_id"] = anime_json["id"]
        res["title"] = anime_json["title"]
        res["type"] = anime_json["type"]
        res["episode_count"] = anime_json["episodes"]
        res["start_date"] = anime_json["start_date"]
        res["end_date"] = anime_json["end_date"]
        res["description"] = anime_json["synopsis"]
        res["pictures_url"] = anime_json["image_url"]
