import json
import logging
import os

log = logging.getLogger(__name__)


class Config(object):
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config.json")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.anidb_base_url = "http://api.anidb.net:9001/httpapi"
        self.anidb_pictures_url = "http://img7.anidb.net/pics/anime/"
        self.anidb_cache_dir = os.path.abspath(os.path.join(current_dir, "..", "cache"))
        self.anidb_client_name = ""
        self.anidb_client_version = ""
        self.anidb_client_protocol_version = ""
        self.jikan_base_url = "https://api.jikan.moe/v3"
        self._read_config()

    def _read_config(self):
        if os.path.isfile(self.config_path):
            log.debug("Reading config from: {}".format(self.config_path))
            with open(self.config_path) as config_file:
                cfg = json.load(config_file)
                if "base_url" in cfg["api"]["anidb"]:
                    self.anidb_base_url = cfg["api"]["anidb"]["base_url"]
                if "pictures_url" in cfg["api"]["anidb"]:
                    self.anidb_pictures_url = cfg["api"]["anidb"]["pictures_url"]
                if "cache_dir" in cfg["api"]["anidb"]:
                    self.anidb_cache_dir = cfg["api"]["anidb"]["cache_dir"]
                self.anidb_client_name = cfg["api"]["anidb"]["client_name"]
                self.anidb_client_version = cfg["api"]["anidb"]["client_version"]
                self.anidb_client_protocol_version = cfg["api"]["anidb"]["client_protocol_version"]
        else:
            log.debug("Reading config from env vars")
            if os.getenv("ANIME_SERVICE_ANIDB_BASE_URL") is not None:
                self.anidb_base_url = os.getenv("ANIME_SERVICE_BASE_URL")
            if os.getenv("ANIME_SERVICE_ANIDB_PICTURES_URL") is not None:
                self.anidb_pictures_url = os.getenv("ANIME_SERVICE_PICTURES_URL")
            if os.getenv("ANIME_SERVICE_ANIDB_CACHE_DIR") is not None:
                self.anidb_cache_dir = os.getenv("ANIME_SERVICE_ANIDB_CACHE_DIR")
            self.anidb_client_name = os.getenv("ANIME_SERVICE_ANIDB_CLIENT_NAME")
            self.anidb_client_version = os.getenv("ANIME_SERVICE_ANIDB_CLIENT_VERSION")
            self.anidb_client_protocol_version = os.getenv("ANIME_SERVICE_ANIDB_CLIENT_PROTOCOL_VERSION")
            self.jikan_base_url = os.getenv("ANIME_SERVICE_JIKAN_BASE_URL")


