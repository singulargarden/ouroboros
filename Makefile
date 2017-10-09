schemas: ouroboros/schemas/*.py

init:
	pip install -r requirements.txt

test:
	python -m pytest tests

ouroboros/schemas/*.py: ./schemas/*.proto
	protoc -I=./schemas/  			\
	    --python_out=ouroboros/schemas/	\
	    ./schemas/*.proto


.PHONY: init test

