import datetime
import json
import os
from xml.etree import ElementTree

import boto3
from botocore.exceptions import ClientError

from anidb import AniDbApi

s3_bucket = None
bucket_name = os.getenv("ANIDB_TITLES_BUCKET")


def _get_s3_bucket():
    global s3_bucket
    if s3_bucket is None:
        s3_bucket = boto3.resource("s3").Bucket(bucket_name)
    return s3_bucket


def _download_xml(download_path):
    """Try downloading XML file from S3 bucket, if it doesn't exist get it from AniDbApi"""
    file_name = os.path.basename(download_path)

    xml_file = _download_file(file_name, download_path)

    if xml_file is None:
        print(f"Downloading new titles file: {file_name} to path: {download_path}")

        AniDbApi.download_titles(download_path)

        _get_s3_bucket().upload_file(download_path, file_name)


def _download_file(key, location):
    try:
        s3_file = _get_s3_bucket().download_file(key, location)
        return s3_file
    except ClientError as exc:
        if exc.response['Error']['Code'] == '404':
            return None
        raise


def _save_json_file(xml_path, json_path):
    titles = {}
    for anime in _anime_titles(xml_path):
        titles[anime["title"]] = anime["id"]

    with open(json_path, "w") as f:
        json.dump(titles, f, indent=4)

    file_name = os.path.basename(json_path)
    print(f"Uploading {json_path} to bucket object: {file_name}")
    _get_s3_bucket().upload_file(json_path, file_name)


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


def handle(event, context):
    now = datetime.datetime.now()
    date_today = now.strftime("%Y-%m-%d")

    xml_path = os.path.join("/", "tmp", f"{date_today}.xml")
    json_path = os.path.join("/", "tmp", f"{date_today}.json")

    _download_xml(xml_path)
    _save_json_file(xml_path, json_path)
