import datetime
import logging
import os
import re
from urllib.parse import urlencode
from xml.etree import ElementTree

import requests
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
            "protover": self.config["client_protocol_version"],
        }

        self.base_url = "{}?{}".format(self.config["base_url"], urlencode(base_url_params))
        self.pictures_url = self.config["pictures_url"]

        log.debug("AniDB base_url: {}".format(self.base_url))

        self.nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}

    def search(self, search_string):
        result = []

        for anime in self._find_anime_ids(search_string):
            result.append(anime["title"])

        return jsonify(anime=result)

    def get_all_anime(self):
        result = list(map(lambda anime: anime["title"], self._find_anime_ids("")))

        return jsonify(anime=result)

    def get_anime(self, anime_id):
        url_params = {
            "request": "anime",
            "aid": anime_id
        }

        url = "{}&{}".format(self.base_url, urlencode(url_params))
        log.debug("Sending get request to: %s", url)
        response = requests.get(url)

        result = self._parse_anime(response.text)
        return jsonify(anime=result)

    def _parse_anime(self, anime_xml):
        res = {}
        anime = ElementTree.fromstring(anime_xml)

        res["anime_id"] = anime.attrib.get("id")
        res["title"] = anime.find("./titles/title[@type='main']").text
        res["type"] = self._get_property(anime, "type")
        res["episode_count"] = self._get_property(anime, "episodecount")
        res["start_date"] = self._get_property(anime, "startdate")
        res["end_date"] = self._get_property(anime, "enddate")
        res["description"] = self._get_property(anime, "description")
        res["pictures_url"] = "{}/{}".format(self.pictures_url, self._get_property(anime, "picture"))

        res["episodes"] = []
        for episode in anime.find("episodes"):

            epno = episode.find("./epno[@type='1']", namespaces=self.nsmap)
            if epno is None:
                # Skip all endings, openings "episodes"
                continue

            ep = {
                "id": episode.attrib.get("id"),
                "episode_number": epno.text,
                "length": self._get_property(episode, "length"),
                "air_date": self._get_property(episode, "airdate")
            }
            ep["title"] = episode.find("./title[@xml:lang='en']", namespaces=self.nsmap)
            if ep["title"] is not None:
                ep["title"] = ep["title"].text

            res["episodes"].append(ep)

        return res

    def _find_anime_ids(self, search_string):
        now = datetime.datetime.now()

        res = []

        element_tree = ElementTree.parse(
            os.path.join(CURRENT_DIR, "..", "..", "cache", "titles",
                         "{}.xml".format(now.strftime("%Y-%m-%d")))).getroot()
        for anime in element_tree:
            anime_id = anime.attrib.get("aid")
            title = anime.find("./title[@type='main']", namespaces=self.nsmap)
            if re.match(r'{}'.format(search_string), title.text, re.IGNORECASE):
                res.append({"anime_id": anime_id, "title": title.text})

        return res

    def _get_property(self, xml_element, property):
        prop = xml_element.find("./{}".format(property))
        if prop is not None:
            return prop.text
        return None

