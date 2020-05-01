import logging

import requests
from flask import jsonify, Response

from service.utils.config import get_config

log = logging.getLogger(__name__)


class Error(Exception):
    pass


class HTTPError(Error):
    pass


class MalApi:
    def __init__(self):
        self.config = get_config()

        self.default_headers = {
            "X-Mal-Client-Id": self.config["api"]["mal"]["client_id"],
        }
        self.base_url = self.config["api"]["mal"]["base_url"]

        log.debug("MAL base_url: {}".format(self.base_url))

    def search(self, search_str):
        url = f"{self.base_url}/anime"
        url_params = {
            "q": search_str
        }

        ret = requests.get(url, params=url_params, headers=self.default_headers)
        if ret.status_code != 200:
            raise HTTPError()
        return jsonify(anime=ret.json()["data"])

    def get_anime(self, anime_id):
        url = f"{self.base_url}/anime/{anime_id}"
        fields = [
            "related_anime"
            "alternative_titles",
            "media_type",
            "num_episodes",
            "status",
            "start_date",
            "end_date",
            "average_episode_duration",
            "synopsis",
            "mean",
            "rank",
            "popularity",
            "num_list_users",
            "num_favorites",
            "num_scoring_users",
            "start_season",
            "broadcast",
            "my_list_status{start_date,finish_date}",
            "nsfw",
            "created_at",
            "updated_at"
        ]
        url_params = {
            "fields": ",".join(fields)
        }
        ret = requests.get(url, params=url_params, headers=self.default_headers)
        if ret.status_code == 404:
            return Response(status=404)
        elif ret.status_code != 200:
            raise HTTPError()
        return jsonify(anime=ret.json())

