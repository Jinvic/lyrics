set shell := ["powershell.exe", "-c"]

serve:
    mkdocs serve

build:
    python scripts/preprocess.py
    mkdocs build -d dist
