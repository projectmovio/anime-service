import json
import logging
import os

log = logging.getLogger(__name__)


class Config(object):
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config.json")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_url = "http://api.anidb.net:9001/httpapi"
        self.pictures_url = "http://img7.anidb.net/pics/anime/"
        self.cache_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "cache"))
        self.client_name = ""
        self.client_version = ""
        self.client_protocol_version = ""
        self._read_config()

    def _read_config(self):
        if os.path.isfile(self.config_path):
            log.debug("Reading config from: {}".format(self.config_path))
            with open(self.config_path) as config_file:
                cfg = json.load(config_file)
                if "base_url" in cfg["api"]["anidb"]:
                    self.base_url = cfg["api"]["anidb"]["base_url"]
                if "pictures_url" in cfg["api"]["anidb"]:
                    self.pictures_url = cfg["api"]["anidb"]["pictures_url"]
                if "cache_dir" in cfg["api"]["anidb"]:
                    self.cache_dir = cfg["api"]["anidb"]["cache_dir"]
                self.client_name = cfg["api"]["anidb"]["client_name"]
                self.client_version = cfg["api"]["anidb"]["client_version"]
                self.client_protocol_version = cfg["api"]["anidb"]["client_protocol_version"]
        else:
            log.debug("Reading config from env vars")
            if os.getenv("ANIME_SERVICE_BASE_URL") is not None:
                self.base_url = os.getenv("ANIME_SERVICE_BASE_URL")
            if os.getenv("ANIME_SERVICE_PICTURES_URL") is not None:
                self.pictures_url = os.getenv("ANIME_SERVICE_PICTURES_URL")
            if os.getenv("ANIME_SERVICE_CACHE_DIR") is not None:
                self.cache_dir = os.getenv("ANIME_SERVICE_CACHE_DIR")
            self.client_name = os.getenv("ANIME_SERVICE_CLIENT_NAME")
            self.client_version = os.getenv("ANIME_SERVICE_CLIENT_VERSION")
            self.client_protocol_version = os.getenv("ANIME_SERVICE_CLIENT_PROTOCOL_VERSION")

