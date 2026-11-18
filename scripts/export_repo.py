"""Write one dataset's transactions, summaries and metadata as CSV/JSON.

usage: export_repo.py [FLAGGED.pkl] [OUT_DIR] [PROPERTY_TYPE] [RECENT_FROM_YEAR or none]
  condo:    export_repo.py work/flagged.pkl    repo/data                    "Condominium/Apartment" 2024
  serviced: export_repo.py work/sa/flagged.pkl repo/data/serviced_apartment "Serviced Apartment"    none
"""
import pandas as pd, json, os, sys
a = sys.argv[1:] + ['work/flagged.pkl', 'repo/data', 'Condominium/Apartment', '2024'][len(sys.argv[1:]):]
IN, OUT, PTYPE, RECENT = a[0], a[1], a[2], (None if a[3] == 'none' else int(a[3]))
os.makedirs(f'{OUT}/summary', exist_ok=True)
if RECENT: os.makedirs(f'{OUT}/summary_{RECENT}_2026', exist_ok=True)

d = pd.read_pickle(IN)
t = pd.DataFrame({'state': d.state, 'district': d.district, 'mukim': d.mukim, 'scheme': d.scheme, 'tenure': d.tenure,
  'month': d.date.dt.strftime('%Y-%m'), 'year': d.year.astype(int), 'unit_level': d.level, 'area_sqm': d.area_sqm,
  'area_sqft': d.area_sqft.astype('Int64'), 'price_rm': d.price_rm.round(0).astype('Int64'), 'psf_rm': d.psf.round(2),
  'outlier': d.outlier})
t = t.sort_values(['state', 'district', 'mukim', 'scheme', 'month']).reset_index(drop=True)
t.to_csv(f'{OUT}/transactions.csv', index=False)
c = t[~t.outlier]

def summ(df, keys):
    out = df.groupby(keys).agg(transactions=('price_rm', 'size'), median_price_rm=('price_rm', 'median'),
        median_psf_rm=('psf_rm', 'median'), median_size_sqft=('area_sqft', 'median')).reset_index()
    for k in ['median_price_rm', 'median_psf_rm', 'median_size_sqft']:
        out[k] = out[k].astype(float).round(0).astype(int)
    return out

levels = {'by_state': ['state'], 'by_state_year': ['state', 'year'], 'by_district': ['state', 'district'],
 'by_district_tenure': ['state', 'district', 'tenure'], 'by_district_year': ['state', 'district', 'year'],
 'by_mukim': ['state', 'district', 'mukim'], 'by_mukim_year': ['state', 'district', 'mukim', 'year'],
 'by_scheme': ['state', 'district', 'mukim', 'scheme']}
sets = [('summary', c)] + ([(f'summary_{RECENT}_2026', c[c.year >= RECENT])] if RECENT else [])
files = []
for folder, df in sets:
    for name, keys in levels.items():
        if folder != 'summary' and 'year' in keys: continue
        s = summ(df, keys)
        if name == 'by_scheme':
            ten = df.groupby(keys).tenure.agg(lambda x: '/'.join(sorted(x.unique()))).rename('tenure')
            rng = df.groupby(keys).month.agg(first_sale='min', last_sale='max')
            s = s.merge(ten, on=keys).merge(rng, on=keys)
        s = s.sort_values(keys).reset_index(drop=True)
        s.to_csv(f'{OUT}/{folder}/{name}.csv', index=False)
        s.to_json(f'{OUT}/{folder}/{name}.json', orient='records', indent=1, force_ascii=False)
        files.append((f'{folder}/{name}', len(s)))

meta = {'source': 'National Property Information Centre (NAPIC), JPPH — Open Transaction Data (napic.jpph.gov.my/en/open-sales-data)',
 'property_type': f'{PTYPE} (resales only)', 'states': ['W.P. Kuala Lumpur', 'Selangor'],
 'coverage': {'first_month': t.month.min(), 'last_month': t.month.max()}, 'downloaded': '2026-11', 'generated': '2026-11-18',
 'transactions_total': int(len(t)), 'transactions_used_in_medians': int(len(c)), 'outliers_excluded': int(t.outlier.sum()),
 'outlier_rule': 'step 1: psf_rm < 50; step 2: in schemes with 5+ sales left after step 1, psf below 0.4x or above 2.5x that scheme median psf (computed after step 1)',
 'scheme_splits': {'THE ORION': 'split by psf at RM1,000 into THE ORION (JALAN TUN RAZAK) and THE ORION (NEWER HIGH-RISE, 2024 TRANSFERS)'} if d.scheme.str.startswith('THE ORION (').any() else {},
 'sqm_to_sqft': 10.7639, 'note': 'Recent months incomplete: sales appear only after stamping. Area is NAPIC parcel area.',
 'files': {f: n for f, n in files}}
json.dump(meta, open(f'{OUT}/metadata.json', 'w'), indent=2, ensure_ascii=False)
print(json.dumps({k: meta[k] for k in ['property_type', 'coverage', 'transactions_total', 'outliers_excluded']}, ensure_ascii=False))
