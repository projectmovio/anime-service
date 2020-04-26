import logging

import requests

from service.utils.config import get_config

log = logging.getLogger(__name__)


class MalApi:
    def __init__(self):
        self.config = get_config()

        self.default_headers = {
            "X-MAL-Client-ID": self.config["api"]["mal"]["client_id"]
        }
        self.base_url = self.config["api"]["mal"]["base_url"]

        log.debug("MAL base_url: {}".format(self.base_url))

    def search(self, search_str):
        url = f"{self.base_url}/search"
        url_params = {
            "q": search_str
        }
        ret = requests.get(url, params=url_params)
        return ret
