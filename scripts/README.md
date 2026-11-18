Run from the repo root. Each dataset goes through the same three steps.

Condominium/Apartment (NAPIC downloads saved as work/kl.xlsx and work/sel.xlsx):

    python scripts/clean.py      work/kl.xlsx work/sel.xlsx work/all.pkl
    python scripts/summarise.py  work/all.pkl work
    python scripts/export_repo.py work/flagged.pkl data "Condominium/Apartment" 2024

Serviced Apartment (saved as work/sa/kl.xlsx and work/sa/sel.xlsx):

    python scripts/clean.py      work/sa/kl.xlsx work/sa/sel.xlsx work/sa/all.pkl
    python scripts/summarise.py  work/sa/all.pkl work/sa
    python scripts/export_repo.py work/sa/flagged.pkl data/serviced_apartment "Serviced Apartment" none

clean.py fills NAPIC's merged cells and parses price, area and date. summarise.py flags outliers.
export_repo.py writes the CSV and JSON files. Requires pandas and openpyxl.
