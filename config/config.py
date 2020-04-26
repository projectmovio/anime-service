import json
import logging
import os

log = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class Config(object):
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config.json")
        self._read_config()

    def _read_config(self):
        if os.path.isfile(self.config_path):
            log.debug("Reading config from: {}".format(self.config_path))
            with open(self.config_path) as config_file:
                cfg = json.load(config_file)
                self.base_url = cfg["api"]["anidb"]["base_url"]
                self.pictures_url = cfg["api"]["anidb"]["pictures_url"]
                self.cache_dir = cfg["api"]["anidb"]["cache_dir"]
                self.client_name = cfg["api"]["anidb"]["client_name"]
                self.client_version = cfg["api"]["anidb"]["client_version"]
                self.client_protocol_version = cfg["api"]["anidb"]["client_protocol_version"]
        else:
            log.debug("Reading config from env vars")
            self.base_url = os.getenv("ANIDB_BASE_URL", "http://api.anidb.net:9001/httpapi")
            self.pictures_url = os.getenv("ANIDB_PICTURES_URL", "http://img7.anidb.net/pics/anime/")
            self.cache_dir = os.getenv("ANIDB_CACHE_DIR", os.path.abspath(os.path.join(CURRENT_DIR, "..", "cache")))
            self.client_name = os.getenv("ANIDB_CLIENT_NAME")
            self.client_version = os.getenv("ANIDB_CLIENT_VERSION")
            self.client_protocol_version = os.getenv("ANIDB_CLIENT_PROTOCOL_VERSION")
