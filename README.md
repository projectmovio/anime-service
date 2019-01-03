# Requirements

* python3.7
* pip install -r requirements.txt

# Start server

* `python titles-updater/titles_updater.py`
* `python run_flask.py`
* API base URL: `http://localhost:8085/`

# Formatting

* bash format.sh

# Running in docker

## titles-updater
* `docker build -t titles-updater:latest -f titles-updater/Dockerfile titles-updater`
* `docker run -v "<ABS_PATH_TO_TITLES>":"/cache/titles" -it titles-updater:latest`

## anime-servi ce
* `docker build -t anime-service:latest .`
* `docker run -p 8085:8085 -d -t anime-service:latest`

