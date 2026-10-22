# Tableau Noir — recettes du projet. `just` sans argument liste tout.
set shell := ["bash", "-cu"]

default:
    @just --list

# Installe l'environnement
setup:
    uv sync

# Entraîne le modèle d'xG sur les tirs Wyscout (data/raw/wyscout requis)
xg:
    uv run tableau-noir xg

# Télécharge les données StatsBomb (cache), calcule les stats et écrit web/data/
export:
    uv run tableau-noir export

# Sert le site en local : http://localhost:8000
serve:
    uv run python -m http.server 8000 --directory web

# Tous les tests (Python, puis logique du site)
test:
    uv run pytest
    node --test web/tests/*.test.mjs

# Lint, format et typage
check:
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy
