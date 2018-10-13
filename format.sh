#!/bin/bash

pip install yapf yamllint isort
find . -name '*.py' -exec yapf -i -vv {} \+
find . -name '*.yaml' -exec yamllint {} \+
isort -rc .
