import datetime
import logging
import os
import re
import xml.etree.ElementTree
from urllib.parse import urlencode

from flask import jsonify

from service.utils.config import Config

log = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class AniDbApi:
    def __init__(self):
        self.config = Config().cfg["api"]["anidb"]

        base_url_params = {
            "client": self.config["client"],
            "clientver": self.config["client_version"],
            "protver": self.config["client_protocol_version"],
        }

        self.base_url = "{}?{}".format(self.config["base_url"], urlencode(base_url_params))

        log.debug("AniDB base_url: {}".format(self.base_url))

    def search(self, search_string):
        result = []

        for anime in self._find_anime_id(search_string):
            result.append(anime["title"])

        return jsonify(anime=result)

    def get_anime(self):
        result = []

        for anime in self._find_anime_id(""):
            result.append(anime["title"])

        return jsonify(anime=result)

    def _find_anime_id(self, search_string):
        now = datetime.datetime.now()
        nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
        res = []

        element_tree = xml.etree.ElementTree.parse(
            os.path.join(CURRENT_DIR, "..", "..", "cache", "titles",
                         "{}.xml".format(now.strftime("%Y-%m-%d")))).getroot()
        for anime in element_tree:
            anime_id = anime.attrib.get("aid")
            title = anime.find("./title[@type='main']", namespaces=nsmap)
            if re.match(r'{}'.format(search_string), title.text, re.IGNORECASE):
                res.append({"anime_id": anime_id, "title": title.text})

        return res
