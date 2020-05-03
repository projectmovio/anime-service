import os
import time

import anidb
import params_db
import anime_db


def handler(event, context):
    last_timestamp = params_db.get_last_post_anime_update()

    current_timestamp = int(time.time())
    if current_timestamp - last_timestamp <= 2:
        print("Previous update triggered less than 2 seconds ago")
        time.sleep(2)

    # batch size always 1, sleep and throttle could increase runtime close to lambda timeout
    # divide it in 1 update per lambda instead. This will also make the code cleaner.
    mal_id = event["Records"][0]["body"]


    params.set_last_post_anime_update(int(time.time()), mal_id)
