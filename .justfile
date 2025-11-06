set shell := ["powershell.exe", "-c"]

process:
    python scripts/preprocess.py

serve:
    python scripts/preprocess.py
    mkdocs serve

build:
    python scripts/preprocess.py
    mkdocs build -d dist

# （[^）]*）
convert file:
    python .\scripts\convert_photrans.py {{file}}
