# Requirements

* python3.7
* pip install -r requirements.txt

# Start server

* `python titles-updater/titles_updater.py`
* `python run_flask.py`
* API base URL: `http://localhost:8085/`

# API docs

For api docs go to http://localhost:5000/apidocs

# Formatting

* bash format.sh

# Running in docker

* docker build -t anime-service:latest .
* docker run -p 8085:8085 -d -t anime-service:latest

