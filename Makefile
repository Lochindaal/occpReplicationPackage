VENV_BIN ?= python -m venv
VENV_DIR ?= .venv
PIP_CMD ?= pip3

ifeq ($(OS), Windows_NT)
	VENV_ACTIVATE = $(VENV_DIR)/Scripts/activate
else
	VENV_ACTIVATE = $(VENV_DIR)/bin/activate
endif

VENV_RUN = . $(VENV_ACTIVATE)

$(VENV_ACTIVATE): setup.py setup.cfg
	test -d $(VENV_DIR) || $(VENV_BIN) $(VENV_DIR)
	$(VENV_RUN); $(PIP_CMD) install --upgrade pip setuptools wheel plux
	touch $(VENV_ACTIVATE)

## Create a virtual environment
venv: $(VENV_ACTIVATE)

install: venv install-mona
	$(VENV_RUN); $(PIP_CMD) install $(PIP_OPTS) -e ".[runtime,test]"

format:
	($(VENV_RUN); python -m black .)

lint:
	($(VENV_RUN); python -m pflake8 --show-source)

# Install subproject A
install-mona: venv
	$(VENV_RUN); cd mona; $(PIP_CMD) install $(PIP_OPTS) -e ".[runtime,test]"

# Clean up build artifacts
clean: 
	rm -rf $(VENV_DIR)
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "dist" -exec rm -r {} +

.PHONY: venv install-mona install clean
