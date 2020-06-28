import datetime
import os

from anidb import download_xml, save_json_titles
import logger

log = logger.get_logger("titles_updater")


def handle(event, context):
    log.debug("Starting handler")
    now = datetime.datetime.now()
    date_today = now.strftime("%Y-%m-%d")

    xml_path = os.path.join("/", "tmp", f"{date_today}.xml")
    json_path = os.path.join("/", "tmp", f"{date_today}.json")

    download_xml(xml_path)
    save_json_titles(xml_path, json_path)

    return xml_path, json_path
