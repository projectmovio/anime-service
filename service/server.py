import logging
import os

from flask import Flask, request
from flask_caching import Cache

from service.api.anidb import AniDbApi
from service.utils.config import Config

log = logging.getLogger("service")
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("urllib3").setLevel("WARNING")

cache = Cache(config={
    "CACHE_TYPE": "filesystem",
    "CACHE_DIR": os.path.join(Config().cache_dir, "flask"),
    "CACHE_THRESHOLD": 1000000
})

app = Flask(__name__)
cache.init_app(app)

anidb_api = AniDbApi()


@cache.cached(timeout=60 * 60 * 24)
@app.route("/anime", methods=["get"])
def anime():
    log.debug("Headers: %s", request.headers)
    if "search" in request.args:
        search = request.args.get("search")
        return anidb_api.search(search)
    elif "id" in request.args:
        id = request.args.get("id")
        return anidb_api.get_anime(id)
    else:
        return anidb_api.get_all_anime()
