.PHONY: test
test:
	pip install -U -r test/requirements.txt
	PYTHONPATH=./src/layers/api/python:./src/layers/common/python:./src/layers/utils/python:./src/lambdas/:./src/layers/databases/python \
		pytest --cov-report html --cov=src -vv

.PHONY: format
format:
	pip install yapf isort
	find . -name '*.py' -exec yapf -i -vv {} \+
	isort -rc .