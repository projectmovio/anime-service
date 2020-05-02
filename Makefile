.PHONY: test
test:
	pip install -U -r test/requirements.txt
	PYTHONPATH=./src/layers/api/python pytest --cov-report html --cov=mal --cov=anidb -vv

.PHONY: format
format:
	pip install yapf isort
	find . -name '*.py' -exec yapf -i -vv {} \+
	isort -rc .