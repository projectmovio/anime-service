.PHONY: test
test:
	pip install -U -r test/unittest/requirements.txt
	pip install -U -r src/layers/api/requirements.txt
	pip install -U -r src/layers/databases/requirements.txt
	pip install -U -r src/layers/utils/requirements.txt
	PYTHONPATH=./src/layers/api/python:./src/layers/common/python:./src/layers/utils/python:./src/lambdas/:./src/layers/databases/python \
		pytest test/unittest --cov-report html --cov=src -vv

.PHONY: format
format:
	pip install yapf isort
	find . -name '*.py' -exec yapf -i -vv {} \+
	isort -rc .

.PHONY: apitest
apitest:
	PYTHONPATH=test pytest test/apitest -vv

.PHONE: generate-hashes
generate-hashes:
	pip install pip-tools
	pip-compile --generate-hashes src/layers/api/requirements.in --output-file src/layers/api/requirements.txt
	pip-compile --generate-hashes src/layers/databases/requirements.in --output-file src/layers/databases/requirements.txt
	pip-compile --generate-hashes src/layers/utils/requirements.in --output-file src/layers/utils/requirements.txt
	pip-compile --generate-hashes deploy/requirements.in --output-file deploy/requirements.txt
