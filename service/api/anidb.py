import datetime
import logging
import os
import re
from urllib.parse import urlencode
from xml.etree import ElementTree

import requests
from flask import jsonify

from service.utils.config import get_config

log = logging.getLogger(__name__)


class AniDbApi:
    def __init__(self):
        self.config = get_config()

        base_url_params = {
            "client": self.config["api"]["anidb"]["client_name"],
            "clientver": self.config["api"]["anidb"]["client_version"],
            "protover": self.config["api"]["anidb"]["client_protocol_version"],
        }

        self.base_url = "{}?{}".format(self.config.base_url, urlencode(base_url_params))
        self.pictures_url = self.config.pictures_url

        log.debug("AniDB base_url: {}".format(self.base_url))

        self.nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
        self.current_titles_name = ""
        self.anime_titles = {}

    def search(self, search_string):
        found_anime = []
        max_results = 100
        for anime_id in self._find_anime_ids(search_string):
            if len(found_anime) == max_results:
                break

            anime = {"anime_id": anime_id, "pictures_url": "{}/{}.jpg".format(self.pictures_url, anime_id)}
            found_anime.append(anime)

        return jsonify(anime=found_anime)

    def get_anime(self, anime_id):
        url_params = {"request": "anime", "aid": anime_id}

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

            title = episode.find("./title[@xml:lang='en']", namespaces=self.nsmap)
            if title is not None:
                title = title.text

            ep = {
                "id": episode.attrib.get("id"),
                "episode_number": epno.text,
                "length": self._get_property(episode, "length"),
                "air_date": self._get_property(episode, "airdate"),
                "title": title
            }

            res["episodes"].append(ep)

        return res

    def _find_anime_ids(self, search_string):
        now = datetime.datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        titles_name = "{}.xml".format(today_date)
        titles_file = os.path.join(self.config.cache_dir, "titles", titles_name)
        if not os.path.isfile(titles_file):
            log.warning("Titles file: [%s] doesn't exist, try fallback to yesterday", titles_file)
            yesterday_date = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            titles_name = "{}.xml".format(yesterday_date)
            titles_file = os.path.join(self.config.cache_dir, "titles", titles_name)

            if not os.path.isfile(titles_file):
                raise RuntimeError("No titles file for today: [%s] or yesterday: [%s]", today_date, yesterday_date)

        res = []

        if self.current_titles_name != titles_name:
            log.debug("Reading titles from new XML file: [%s.xml]", titles_name)
            self.anime_titles = {}
            self.current_titles_name = titles_name

            element_tree = ElementTree.parse(titles_file).getroot()
            for anime in element_tree:
                anime_id = anime.attrib.get("aid")
                titles = anime.findall("./title", namespaces=self.nsmap)
                for title in titles:
                    if anime_id not in self.anime_titles:
                        self.anime_titles[anime_id] = []
                    self.anime_titles[anime_id].append(title.text)

        for anime_id in self.anime_titles:
            for title in self.anime_titles[anime_id]:
                if re.match(r'{}'.format(search_string), title, re.IGNORECASE):
                    res.append(anime_id)

        return res

    def _get_property(self, xml_element, property):
        prop = xml_element.find("./{}".format(property))
        if prop is not None:
            return prop.text
        return None
