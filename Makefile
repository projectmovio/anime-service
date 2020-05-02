.PHONY: test
test:
	pip install -U -r test/requirements.txt
	PYTHONPATH=./src/layers/api/python pytest --cov-report html --cov=mal --cov=anidb -vv