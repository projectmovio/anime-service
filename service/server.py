import logging
import os

from flask import Flask, request
from flask_caching import Cache

from service.api.anidb import AniDbApi

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

log = logging.getLogger("service")
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("urllib3").setLevel("WARNING")

cache = Cache(config={
    "CACHE_TYPE": "filesystem",
    "CACHE_DIR": os.path.join(CURRENT_DIR, "..", "cache", "flask"),
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
    else:
        return anidb_api.get_anime()
