set shell := ["powershell.exe", "-c"]

process:
    python scripts/preprocess.py

serve:
    python scripts/preprocess.py
    zensical serve

build:
    python scripts/preprocess.py
    zensical build

# （[^）]*）
convert file:
    python .\scripts\convert_photrans.py {{file}}
