import logging
import os

from flask import Flask, request
from flask_caching import Cache

from service.api.mal import MalApi
from service.api.anidb import AniDbApi
from service.utils.config import get_config

log = logging.getLogger("service")
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("urllib3").setLevel("WARNING")

cfg = get_config()
flask_cache = os.path.join(cfg["api"]["anidb"]["cache_dir"], "flask")
os.makedirs(flask_cache, exist_ok=True)

cache = Cache(config={
    "CACHE_TYPE": "filesystem",
    "CACHE_DIR": flask_cache,
    "CACHE_THRESHOLD": 1000000
})

app = Flask(__name__)
cache.init_app(app)

#anidb_api = AniDbApi()
mal_api = MalApi()


@cache.cached(timeout=60 * 60 * 24)
@app.route("/anime", methods=["GET"])
def anime():
    log.debug("Headers: %s", request.headers)
    if "search" in request.args:
        search = request.args.get("search")
        return mal_api.search(search)
    # elif "id" in request.args:
    #     id = request.args.get("id")
    #     return anidb_api.get_anime(id)
