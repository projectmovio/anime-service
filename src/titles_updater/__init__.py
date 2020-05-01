import datetime
import os
from xml.etree import ElementTree

import boto3
from botocore.exceptions import ClientError

from anidb import AniDbApi

s3_client = None
s3_bucket = None
bucket_name = os.getenv("ANIDB_TITLES_BUCKET")


def _get_s3_bucket():
    global s3_bucket
    if s3_bucket is None:
        s3_bucket = boto3.resource("s3").Bucket(bucket_name)
    return s3_bucket


def _get_s3_client():
    global s3_client
    if s3_client is None:
        s3_client = boto3.client("s3")
    return s3_client


def _object_exists(key):
    try:
        _get_s3_client().head_object(Bucket=bucket_name, Key=key)
    except ClientError as exc:
        if exc.response['Error']['Code'] == '404':
            return False
        raise
    return True


def _parse_xml(file_path):
    element_tree = ElementTree.parse(file_path).getroot()
    for anime in element_tree:
        anime_id = anime.attrib.get("aid")
        titles = anime.findall("./title", namespaces={"xml": "http://www.w3.org/XML/1998/namespace"})



def handle(event, context):
    now = datetime.datetime.now()
    date_today = now.strftime("%Y-%m-%d")
    date_yesterday = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    current_filename = f"{date_today}.json"

    if not _object_exists(current_filename):
        download_path = os.path.join("/", "tmp", current_filename)
        print(f"Downloading new titles file: {current_filename} to path: {download_path}")

        AniDbApi.download_titles(download_path)

    # Clean up all old titles more than 2 days old
    for title in os.listdir(titles_path):
        if title != "{}.xml".format(date_today) and title != "{}.xml".format(date_yesterday):
            print("Removing old titles file: {}", title)
            os.remove(os.path.join(titles_path, title))
