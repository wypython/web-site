.DEFAULT_GOAL := run

VENV=./env
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

run: $(VENV)
	$(PYTHON) wy.py

$(VENV):
	virtualenv -p python2.7 $@
	$(PIP) install -r requirements.txt

clean:
	rm -rf $(VENV)

.PHONY: clean run
