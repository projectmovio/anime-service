import datetime
import os

import requests

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(CURRENT_DIR, "..", "cache")
titles_path = os.path.join(CACHE_DIR, "titles")
os.makedirs(titles_path, exist_ok=True)

now = datetime.datetime.now()
current_filename = os.path.join(CACHE_DIR, "titles", "{}.xml".format(now.strftime("%Y-%m-%d")))

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

# A normal xml file not even gunzipped!
print("Current titles: {}".format(os.path.abspath(current_filename)))
