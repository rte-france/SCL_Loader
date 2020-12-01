init:
    pip install -r requirements-dev.txt

test:
    py.test tests

.PHONY: init test