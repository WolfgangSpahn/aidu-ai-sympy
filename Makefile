# Makefile for verb-gloss-wsd

UV=uv
FIND=find
MAKE=make
SRC=aidu.ai.sympy

APP=app/

.PHONY: help install clean wipe serve run smoke test curl web.build

help:                                     ## Show this help
	@grep -h "##" $(MAKEFILE_LIST) | grep -v grep | sed -e "s/\$$//" -e "s/##//"

# install targets

server.install:                                  ## Install python dependencies and set up environment
	@echo "Installing dependencies"
	@$(UV) sync

	@echo "Upgrading pip"
	@$(UV) run python -m ensurepip --upgrade

# Cleanup targets

server.clean:                             ## Clean temporary and cache files
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .venv
	$(FIND) . -type f -name '*~' -delete
	$(FIND) . -type f -name '*.pyc' -delete
	$(FIND) . -type d -name '__pycache__' -delete

wipe:                                     ## Delete all uv-related files for a fresh start
wipe: server.clean
	@echo "Removing uv.lock"
	rm -f uv.lock


# Application targets

server.run:	                               ## Run the web server for the application
	$(UV) run python -m serve.app

app.run:                                   ## Run the analysis application (default)
	@echo "Running the application"
	@echo "no main yet"

# Smoke test targets

smoke.client:                             ## Run a quick smoke test for the client
	$(UV) run python -m $(SRC).client


smoke:									  ## Run all smoke tests
	$(MAKE) smoke.client

# Testing targets
	
test:                                     ## Run all tests
	@echo "Running tests..."
	$(UV) run pytest

curl:	                                  ## Runs curl tests against the server
	@echo "Running curl tests..."
	test/curl_tests.sh


install: server.install web.install
	@echo "Installed server and web frontend"
