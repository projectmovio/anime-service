import datetime
import os
import time

import requests

from config.config import Config

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
        r = requests.get("http://anidb.net/api/anime-titles.xml.gz", stream=True)

        total_size = int(r.headers.get('content-length', 0))
        count = 0
        with open(current_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    count += 1
                    if count % 100 == 0:
                        print("Progress in percentage: {}".format((1024 * count) / float(total_size)))

        print("Progress in percentage: 1")
    else:
        print("Title file for today already exists")

    print("Current titles: {}".format(os.path.abspath(current_filename)))

    # Clean up all old titles more than 2 days old
    for title in os.listdir(titles_path):
        if title != "{}.xml".format(date_today) and title != "{}.xml".format(date_yesterday):
            print("Removing old titles file: {}", title)
            os.remove(os.path.join(titles_path, title))

    print("Sleeping %s seconds" % sleep_time)
    time.sleep(sleep_time)
