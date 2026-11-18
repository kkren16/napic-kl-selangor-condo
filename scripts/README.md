Run in order from the repo root, with the two NAPIC downloads saved as `work/kl.xlsx` and `work/sel.xlsx`:

    python scripts/clean.py       # fill merged cells, parse price/area/date, compute psf
    python scripts/summarise.py   # flag outliers
    python scripts/export_repo.py # write data/ (CSV + JSON) into ./repo

Requires pandas and openpyxl.
