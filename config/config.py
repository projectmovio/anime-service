import json
import logging
import os

log = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class Config(object):
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config.json")
        self.cfg = self._read_config()

    def _read_config(self):
        if os.path.isfile(self.config_path):
            log.debug("Reading config from: {}".format(self.config_path))
            with open(self.config_path) as config_file:
                return json.load(config_file)

        log.debug("Reading config from env vars")
        cache_dir = os.getenv("ANIDB_CACHE_DIR", os.path.abspath(os.path.join(CURRENT_DIR, "..", "cache")))
        return {
            "api": {
                "anidb": {
                    "base_url": os.getenv("ANIDB_BASE_URL", "http://api.anidb.net:9001/httpapi"),
                    "pictures_url": os.getenv("ANIDB_PICTURES_URL", "http://img7.anidb.net/pics/anime/"),
                    "cache_dir": os.getenv("ANIDB_CACHE_DIR", cache_dir),
                    "client_name": os.getenv("ANIDB_CLIENT_NAME"),
                    "client_version": os.getenv("ANIDB_CLIENT_VERSION"),
                    "client_protocol_version": os.getenv("ANIDB_CLIENT_PROTOCOL_VERSION")
                }
            }
        }
