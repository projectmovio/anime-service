import logging
import os

from flask import Flask, request, Response, make_response, jsonify
from flask_caching import Cache

from service.api.anidb import AniDbApi
from config.config import Config

log = logging.getLogger("service")
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("urllib3").setLevel("WARNING")

flask_cache = os.path.join(Config().cache_dir, "flask")
os.makedirs(flask_cache, exist_ok=True)

cache = Cache(config={
    "CACHE_TYPE": "filesystem",
    "CACHE_DIR": flask_cache,
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
        return make_response(jsonify({"error": "'search' or 'id' query parameter required"}), 201)
