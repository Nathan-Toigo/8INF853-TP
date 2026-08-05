# Pipeline CI local — projet 8INF950ETE2026
# Prérequis : Python 3.11+, make (WSL/Linux/macOS)
# Crée automatiquement .venv/ (contourne PEP 668 sous Debian/WSL)

PYTHON ?= $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python3)
SCRIPTS = scripts

.PHONY: help setup-wsl ci-variants-a fig6

help:
	@echo "Cibles disponibles :"
	@echo "  make setup-wsl        Prérequis WSL/Debian (python3-venv, évite PEP 668)"
	@echo "  make ci-variants-a    Pipeline CI sur les 4 variantes A + MAJ etat-de-lart-outils-ia.md"
	@echo "  make fig6             Diagramme (Figure 6) a partir de etat-de-lart-outils-ia.md -> fig6.png"
	@echo ""
	@echo "Python détecté : $(PYTHON)"
	@echo "Forcer l'interpréteur : make ci-variants-a PYTHON=python3"

setup-wsl:
	sudo apt update
	sudo apt install -y python3-venv python3-pip

ci-variants-a:
	$(PYTHON) $(SCRIPTS)/run_ci_local.py

fig6:
	@if [ ! -x .venv/bin/python ]; then $(PYTHON) -m venv .venv; fi
	.venv/bin/pip install -q -r $(SCRIPTS)/requirements.txt
	.venv/bin/python $(SCRIPTS)/generate_fig6_chart.py
