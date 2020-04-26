import logging

from utils.config import get_config

log = logging.getLogger(__name__)


class MalApi:
    def __init__(self):
        self.config = get_config()

        self.default_headers = {
            "X-MAL-Client-ID": self.config["api"]["mal"]["client_id"]
        }
        self.base_url = self.config["api"]["mal"]["client_id"]

        log.debug("MAL base_url: {}".format(self.base_url))


