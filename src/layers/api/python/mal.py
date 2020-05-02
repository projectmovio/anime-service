import logging
import os

import requests

log = logging.getLogger(__name__)

CLIENT_ID = os.getenv("MAL_CLIENT_ID")


class Error(Exception):
    pass


class HTTPError(Error):
    pass


class NotFoundError(Error):
    pass


class MalApi:
    def __init__(self):
        self.default_headers = {
            "X-Mal-Client-Id": CLIENT_ID,
        }
        self.base_url = "https://api.myanimelist.net/v2"

        log.debug("MAL base_url: {}".format(self.base_url))

    def search(self, search_str):
        url = f"{self.base_url}/anime"
        url_params = {"q": search_str}

        ret = requests.get(url, params=url_params, headers=self.default_headers)
        if ret.status_code != 200:
            raise HTTPError(f"Unexpected status code: {ret.status_code}")

        res = {"anime": []}
        for a in ret.json()["data"]:
            res["anime"].append(a["node"])
        return res

    def get_anime(self, anime_id):
        url = f"{self.base_url}/anime/{anime_id}"
        fields = [
            "related_anime"
            "alternative_titles", "media_type", "num_episodes", "status", "start_date", "end_date",
            "average_episode_duration", "synopsis", "mean", "rank", "popularity", "num_list_users", "num_favorites",
            "num_scoring_users", "start_season", "broadcast", "my_list_status{start_date,finish_date}", "nsfw",
            "created_at", "updated_at"
        ]
        url_params = {"fields": ",".join(fields)}
        ret = requests.get(url, params=url_params, headers=self.default_headers)
        if ret.status_code == 404:
            raise NotFoundError()
        elif ret.status_code != 200:
            raise HTTPError(f"Unexpected status code: {ret.status_code}")
        return {"anime": ret.json()}
