import gzip
import logging
import os
import shutil
from urllib.parse import urlencode
from xml.etree import ElementTree

import requests
from fake_useragent import UserAgent

log = logging.getLogger(__name__)

CLIENT = os.getenv("ANIDB_CLIENT")
CLIENT_VERSION = os.getenv("ANIDB_CLIENT_VERSION")
PROTOCOL_VERSION = os.getenv("ANIDB_PROTOCOL_VERSION")


class AniDbApi:
    def __init__(self):

        base_url_params = {
            "client": CLIENT,
            "clientver": CLIENT_VERSION,
            "protover": PROTOCOL_VERSION,
        }

        api_url = "http://api.anidb.net:9001/httpapi"
        self.base_url = f"{api_url}?{urlencode(base_url_params)}"

        log.debug("AniDB base_url: {}".format(self.base_url))

        self.pictures_url = "http://img7.anidb.net/pics/anime/"
        self.nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}

    def get_anime(self, anime_id):
        url_params = {"request": "anime", "aid": anime_id}

        url = "{}&{}".format(self.base_url, urlencode(url_params))
        log.debug("Sending get request to: %s", url)
        response = requests.get(url)

        result = self._parse_anime(response.text)
        return {"anime": result}

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

    def _get_property(self, xml_element, property):
        prop = xml_element.find("./{}".format(property))
        if prop is not None:
            return prop.text
        return None

    @staticmethod
    def download_titles(file_path):
        r = requests.get("http://anidb.net/api/anime-titles.xml.gz", headers={"User-Agent": UserAgent().chrome})

        # Write titles zip to temporary file
        gzip_file = "titles.gz"
        with open(gzip_file, 'wb') as f:
            f.write(r.content)

        # Unzip file
        with gzip.open(gzip_file, 'rb') as f_in:
            with open(file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Remove gz file
        os.remove(gzip_file)
