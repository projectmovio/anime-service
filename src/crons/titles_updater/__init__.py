import datetime
import os

from anidb import download_xml, save_json_titles


def handle(event, context):
    now = datetime.datetime.now()
    date_today = now.strftime("%Y-%m-%d")

    xml_path = os.path.join("/", "tmp", f"{date_today}.xml")
    json_path = os.path.join("/", "tmp", f"{date_today}.json")

    download_xml(xml_path)
    save_json_titles(xml_path, json_path)
