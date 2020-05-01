import datetime
import gzip
import os
import shutil
import time

import requests
from fake_useragent import UserAgent

from service.utils.config import Config

titles_path = os.path.join(Config().cache_dir, "titles")
os.makedirs(titles_path, exist_ok=True)

sleep_time = 100

while True:
    now = datetime.datetime.now()
    date_today = now.strftime("%Y-%m-%d")
    date_yesterday = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    current_filename = os.path.join(titles_path, "{}.xml".format(date_today))

    if not os.path.isfile(current_filename):
        print("Downloading new titles file")
        r = requests.get("http://anidb.net/api/anime-titles.xml.gz", headers={"User-Agent": UserAgent().chrome})

        gzip_file = "{}.gz".format(current_filename)
        with open(gzip_file, 'wb') as f:
            f.write(r.content)

        # Unzip file
        with gzip.open(gzip_file, 'rb') as f_in:
            with open(current_filename, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(gzip_file)

        print("Downloaded titles: {}".format(os.path.abspath(current_filename)))

    # Clean up all old titles more than 2 days old
    for title in os.listdir(titles_path):
        if title != "{}.xml".format(date_today) and title != "{}.xml".format(date_yesterday):
            print("Removing old titles file: {}", title)
            os.remove(os.path.join(titles_path, title))

    time.sleep(sleep_time)
