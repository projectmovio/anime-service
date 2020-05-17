import os
import time

import anidb
import params_db
import anime_db
import mal


def handler(event, context):
    last_timestamp = params_db.get_last_post_anime_update()

    current_timestamp = int(time.time())
    if current_timestamp - last_timestamp <= 2:
        print("Previous update triggered less than 2 seconds ago")
        time.sleep(2)

    # batch size always 1, sleep and throttle could increase runtime close to lambda timeout
    # split it up in 1 update per lambda instead. This will also make the code cleaner.
    mal_id = event["Records"][0]["body"]

    try:
        anime_db.get_anime(mal_id)
    except anime_db.NotFoundError:
        pass
    else:
        print(f"Anime with mal_id: {mal_id} already present, ignore update")
        return



    download_folder = os.path.join("/", "tmp")
    anidb_titles = anidb.get_json_titles(download_folder)



    params_db.set_last_post_anime_update(int(time.time()), mal_id)
