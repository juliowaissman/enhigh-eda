#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = enhigh-eda
PYTHON_VERSION = 3.13
PYTHON_INTERPRETER = python3.13
VENV_ACTIVATE = source .venv/bin/activate
VENV_DEACTIVATE = deactivate

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python Dependencies
.PHONY: requirements
requirements:
	$(VENV_ACTIVATE); $(PYTHON_INTERPRETER) -m pip install -U pip && \
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt


## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf data/interm/
	$(VENV_ACTIVATE); dvc add data/interim/
	git add -A
	git commit -m "Limpiando archivos precompilados y dator intermedios"
	git push

## Lint using flake8 and black (use `make format` to do formatting)
.PHONY: lint
lint:
	flake8 enhigh_eda
	isort --check --diff --profile black enhigh_eda
	black --check --config pyproject.toml enhigh_eda

## Format source code with black
.PHONY: format
format:
	black --config pyproject.toml enhigh_eda


## Inicializa el entrono e instala las librerías
.PHONY: init
init:
	$(PYTHON_INTERPRETER) -m venv .venv
	make requirements
	$(VENV_ACTIVATE); dvc init --subdir
	@echo "Para activar el entorno virtual, ejecuta: \nsource .venv/bin/activate"
	
## elimina el entorno virtual y los archivos creados
.PHONY: close
close:
	make clean
	$(VENV_DEACTIVATE)
	rm -rf .venv
	rm -rf data
	rm -rf .dvc

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

## elimina el entorno virtual y los archivos creados
.PHONY: ingesta
ingesta:
	#$(VENV_ACTIVATE); \
	#$(PYTHON_INTERPRETER) enhigh_eda/ingesta/carga_enhigh.py --año 2024 && \
	#$(PYTHON_INTERPRETER) enhigh_eda/ingesta/carga_enhigh.py --año 2022 #&& \
	# $(PYTHON_INTERPRETER) enhigh_eda/ingesta/carga_enhigh.py --año 2020 && \
	# $(PYTHON_INTERPRETER) enhigh_eda/ingesta/carga_enhigh.py --año 2018 && \
	# $(PYTHON_INTERPRETER) enhigh_eda/ingesta/carga_enhigh.py --año 2016 
	$(VENV_ACTIVATE); dvc add data/raw/
	git add -A
	git commit -m "Agrega raw data a DVC"
	git push

## Extrae los datos en un repositorio intermedio y los da de alta en DVC
.PHONY: extraer
extraer:
	$(VENV_ACTIVATE); \
	$(PYTHON_INTERPRETER) enhigh_eda/procesamiento/extrae_enhigh.py --año 2024 && \
	$(PYTHON_INTERPRETER) enhigh_eda/procesamiento/extrae_enhigh.py --año 2022 # && \
	# $(PYTHON_INTERPRETER) enhigh_eda/procesamiento/extrae_enhigh.py --año 2020 && \
	# $(PYTHON_INTERPRETER) enhigh_eda/procesamiento/extrae_enhigh.py --año 2018 
	$(VENV_ACTIVATE); dvc add data/interm/
	git add -A
	git commit -m "Agrega datos descomprimidos (intermedios) a DVC"
	git push

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
