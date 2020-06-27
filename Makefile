.PHONY: test
test:
	pip install -U -r test/requirements.txt
	PYTHONPATH=./src/layers/api/python:./src/layers/common/python:./src/layers/utils/python:./src/:./src/layers/databases/python pytest \
		--cov-report html \
		--cov=mal \
		--cov=anidb \
		--cov=anime_db \
		--cov=episodes_db \
		--cov=params_db \
		--cov=logger \
		--cov=sqs_handlers \
		-vv

.PHONY: format
format:
	pip install yapf isort
	find . -name '*.py' -exec yapf -i -vv {} \+
	isort -rc .