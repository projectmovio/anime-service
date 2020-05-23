import datetime
import gzip
import json
import logging
import os
import shutil
import uuid
from urllib.parse import urlencode
from xml.etree import ElementTree

import boto3
import requests
from botocore.exceptions import ClientError
from fake_useragent import UserAgent

log = logging.getLogger(__name__)

CLIENT = os.getenv("ANIDB_CLIENT")
CLIENT_VERSION = os.getenv("ANIDB_CLIENT_VERSION")
PROTOCOL_VERSION = os.getenv("ANIDB_PROTOCOL_VERSION")
BUCKET_NAME = os.getenv("ANIDB_TITLES_BUCKET")

s3_bucket = None


class Error(Exception):
    pass


class HTTPError(Error):
    pass


class TitlesNotFound(Error):
    pass


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

    def get_anime(self, anime_id: uuid.UUID):
        url_params = {"request": "anime", "aid": anime_id}

        url = "{}&{}".format(self.base_url, urlencode(url_params))
        log.debug("Sending get request to: %s", url)
        ret = requests.get(url)

        if ret.status_code != 200:
            raise HTTPError(f"Unexpected status code: {ret.status_code}")

        result = self._parse_anime(ret.text)
        return {"anime": result}

    def _parse_anime(self, anime_xml):
        res = {}
        anime = ElementTree.fromstring(anime_xml)

        res["anidb_id"] = anime.attrib.get("id")
        res["media_type"] = self._get_property(anime, "type")
        res["num_episodes"] = self._get_property(anime, "episodecount")
        res["start_date"] = self._get_property(anime, "startdate")
        res["end_date"] = self._get_property(anime, "enddate")
        res["synopsis"] = self._get_property(anime, "description")

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

    def _get_property(self, xml_element, prop):
        prop = xml_element.find("./{}".format(prop))
        if prop is not None:
            return prop.text
        return None


def _get_s3_bucket():
    global s3_bucket
    if s3_bucket is None:
        s3_bucket = boto3.resource("s3").Bucket(BUCKET_NAME)
    return s3_bucket


def _download_titles(file_path):
    """Download anime titles in GZ format, unzip and save to the specified file_path"""
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


def _anime_titles(file_path):
    element_tree = ElementTree.parse(file_path).getroot()
    for anime in element_tree:
        anime_id = anime.attrib.get("aid")
        titles = anime.findall("./title", namespaces={"xml": "http://www.w3.org/XML/1998/namespace"})

        for title in titles:
            yield {
                "id": int(anime_id),
                "title": title.text,
            }


def download_xml(download_path):
    """Try downloading XML file from S3 bucket, if it doesn't exist get it from AniDbApi"""
    file_name = os.path.basename(download_path)

    xml_file = _download_file(file_name, download_path)

    if xml_file is None:
        print(f"Downloading new titles file: {file_name} to path: {download_path}")

        _download_titles(download_path)

        _get_s3_bucket().upload_file(download_path, file_name)


def _download_file(key, location):
    try:
        s3_file = _get_s3_bucket().download_file(key, location)
        return s3_file
    except ClientError as exc:
        if exc.response['Error']['Code'] == '404':
            return None
        raise


def save_json_titles(xml_path, json_path):
    titles = {}
    for anime in _anime_titles(xml_path):
        titles[anime["title"]] = anime["id"]

    with open(json_path, "w") as f:
        json.dump(titles, f, indent=4)

    file_name = os.path.basename(json_path)
    print(f"Uploading {json_path} to bucket object: {file_name}")
    _get_s3_bucket().upload_file(json_path, file_name)


def get_json_titles(download_folder):
    now = datetime.datetime.now()
    date_today = now.strftime("%Y-%m-%d")
    date_yesterday = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    today_file = f"{date_today}.json"
    file_path = os.path.join(download_folder, today_file)
    titles_file = _download_file(today_file, file_path)

    if titles_file is None:
        yesterday_file = f"{date_yesterday}.json"
        file_path = os.path.join(download_folder, yesterday_file)
        titles_file = _download_file(yesterday_file, file_path)

    if titles_file is None:
        raise TitlesNotFound(f"No titles found for dates: {date_today}, {date_yesterday}")

    with open(file_path, "r") as f:
        titles = json.load(f)

    return titles
