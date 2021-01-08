import os

import requests
import logger

log = logger.get_logger(__name__)

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

    def get_anime(self, anime_id):
        url = f"{self.base_url}/anime/{anime_id}"
        fields = [
            "related_anime", "alternative_titles", "media_type", "start_date", "end_date", "average_episode_duration",
            "synopsis", "broadcast", "num_episodes", "broadcast"
        ]
        url_params = {"fields": ",".join(fields)}
        ret = requests.get(url, params=url_params, headers=self.default_headers)
        if ret.status_code == 404:
            raise NotFoundError(f"Anime with ID: {anime_id} not found")
        elif ret.status_code != 200:
            raise HTTPError(f"Unexpected status code: {ret.status_code}")

        res = ret.json()
        res["mal_id"] = res.pop("id")

        if "broadcast" in res and "day_of_the_week" in res["broadcast"]:
            # need a top level broadcast_day for dynamodb sort key
            res["broadcast_day"] = res["broadcast"]["day_of_the_week"]
        return res


def get_all_titles(anime):
    titles = [anime["title"]]

    alt_titles = anime.get("alternative_titles")
    if alt_titles is not None:
        if "synonyms" in alt_titles:
            titles += alt_titles.pop("synonyms")
        for t in alt_titles:
            if t not in titles:
                titles.append(alt_titles[t])

    return titles
