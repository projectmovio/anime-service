import os
import time
from difflib import SequenceMatcher

import anidb
import params_db
import anime_db
import episodes_db
import mal
import logger

log = logger.get_logger("sqs_hanlders.anime")


def handle(event, context):
    last_timestamp = params_db.get_last_post_anime_update()

    current_timestamp = int(time.time())
    if current_timestamp - last_timestamp <= 2:
        log.debug("Previous update triggered less than 2 seconds ago")
        time.sleep(2)

    # batch size always 1, sleep and throttle could increase runtime close to lambda timeout
    # split it up in 1 update per lambda instead. This will also make the code cleaner.
    mal_id = int(event["Records"][0]["body"])

    try:
        anime_db.get_anime_by_mal_id(mal_id)
    except anime_db.NotFoundError:
        pass
    else:
        log.debug(f"Anime with mal_id: {mal_id} already present, ignore update")
        return

    mal_api = mal.MalApi()
    anime_data = mal_api.get_anime(mal_id)

    titles = mal.get_all_titles(anime_data)
    anidb_id = _get_anidb_id(titles)
    episodes = None
    if anidb_id:
        log.debug(f"Found matching anidb_id: {anidb_id} for mal_id: {mal_id}")
        anidb_api = anidb.AniDbApi()
        anidb_data = anidb_api.get_anime(anidb_id)["anime"]

        # episodes will be stored in another database
        episodes = anidb_data.pop("episodes")

        anime_data = {**anime_data, **anidb_data}

    anime_id = anime_db.new_anime(anime_data)

    if episodes:
        episodes_db.put_episodes(anime_id, episodes)

    params_db.set_last_post_anime_update(int(time.time()), anime_id)


def _get_anidb_id(all_titles):
    download_folder = os.path.join("/", "tmp")
    anidb_titles = anidb.get_json_titles(download_folder)

    for title in all_titles:
        for anidb_title in anidb_titles:
            compare_ratio = SequenceMatcher(None, title, anidb_title).ratio()
            if compare_ratio > 0.9:
                return anidb_titles[anidb_title]
            elif compare_ratio > 0.6:
                log.info(f"Found 60% match for mal title: {title}. Anidb title: {anidb_title}")

    log.warning(f"Could not find anidb_id for titles: {all_titles}")
    return None
