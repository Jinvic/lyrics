set windows-shell := ["pwsh", "-c"]

process:
    python scripts/preprocess.py

serve: process
    zensical serve

build: process
    zensical build

# （[^）]*）
convert file:
    python .\scripts\convert_photrans.py {{file}}
