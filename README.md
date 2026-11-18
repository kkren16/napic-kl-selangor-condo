# KL & Selangor condo/apartment transaction data (NAPIC, 2021–2026)

Cleaned resale transactions and median price summaries for **Condominium/Apartment** properties in **W.P. Kuala Lumpur** and **Selangor**. The data comes from NAPIC's Open Transaction Data.

- 40,492 recorded resales, dated January 2021 to September 2026
- Summaries at state, district, mukim and scheme level, covering the full period and 2024–2026 only
- CSV for everything, plus JSON for the summaries

## Fetching the data

Every file can be fetched by URL with no login. Two base URLs work:

```
https://raw.githubusercontent.com/kkren16/napic-kl-selangor-condo/main/data/
https://cdn.jsdelivr.net/gh/kkren16/napic-kl-selangor-condo@main/data/   ← CDN, cached, good for websites
```

JavaScript:

```js
const BASE = "https://cdn.jsdelivr.net/gh/kkren16/napic-kl-selangor-condo@main/data";

const mukims = await fetch(`${BASE}/summary_2024_2026/by_mukim.json`).then(r => r.json());
const setapak = mukims.find(m => m.mukim === "Mukim Setapak");
console.log(setapak.median_psf_rm); // 389 (2024–2026)
```

Python:

```python
import pandas as pd
BASE = "https://raw.githubusercontent.com/kkren16/napic-kl-selangor-condo/main/data"
tx = pd.read_csv(f"{BASE}/transactions.csv")
schemes = pd.read_csv(f"{BASE}/summary/by_scheme.csv")
```

## Files

| File | What it holds |
|---|---|
| `data/transactions.csv` | Every sale, one row each, including outliers (marked in the `outlier` column) |
| `data/summary/by_state.*` | Medians per state, Jan 2021 – Sep 2026 |
| `data/summary/by_state_year.*` | Per state, per year |
| `data/summary/by_district.*` | Per district |
| `data/summary/by_district_tenure.*` | Per district, freehold vs leasehold |
| `data/summary/by_district_year.*` | Per district, per year |
| `data/summary/by_mukim.*` | Per mukim |
| `data/summary/by_mukim_year.*` | Per mukim, per year |
| `data/summary/by_scheme.*` | Per scheme (development), with tenure and first/last sale month |
| `data/summary_2024_2026/*` | The same summaries using only sales from 2024 onward |
| `data/metadata.json` | Source, coverage, row counts and the outlier rule |

Each summary comes as both `.csv` and `.json`. The JSON is an array of records.

### Columns

**transactions.csv**: `state`, `district`, `mukim`, `scheme`, `tenure`, `month` (YYYY-MM), `year`, `unit_level`, `area_sqm`, `area_sqft`, `price_rm`, `psf_rm`, `outlier` (True/False)

**summaries**: the grouping columns, then `transactions`, `median_price_rm`, `median_psf_rm`, `median_size_sqft`. `by_scheme` also has `tenure`, `first_sale` and `last_sale`.

## Method

1. **Source:** NAPIC Open Transaction Data, property type Condominium/Apartment, downloaded separately for W.P. Kuala Lumpur and Selangor in November 2026.
2. **Merged cells:** the NAPIC Excel export merges cells for repeated values (scheme, month, tenure, area, unit level). Each merged value was copied to every row it covers.
3. **Size and PSF:** NAPIC gives parcel area in square metres. This was converted at 1 sq m = 10.7639 sq ft. PSF = price ÷ parcel area in sq ft.
4. **Scheme splits:** NAPIC records two developments as "THE ORION" (KL Town Centre). They are split by PSF at RM1,000 into `THE ORION (JALAN TUN RAZAK)`, the 2006 condo at about RM430–600 psf, and `THE ORION (NEWER HIGH-RISE, 2024 TRANSFERS)`, at about RM1,800–3,900 psf. Other scheme names may also cover more than one development, so check sizes and PSF before relying on a single scheme.
5. **Outliers:** 119 sales (0.29%) are left out of all medians but kept in `transactions.csv`. Step 1 marks any sale under RM50 psf (bulk or nominal transfers). Step 2 works out each scheme's median from the sales left after step 1, then marks sales below 0.4× or above 2.5× that median, in schemes with 5 or more such sales. Most outliers are bulk or block sales, likely related-party transfers, or obvious typos.
6. **Medians:** each median is the middle value of the sales in its group. Check the `transactions` column: groups with fewer than about 10 sales are unreliable.

The scripts in `scripts/` reproduce the outputs from the raw NAPIC downloads.

## Limitations

- **Resales only.** Developer (primary market) sales are not included.
- **Serviced residences and SOHOs** are usually classed as commercial by NAPIC, so they are not in this property type.
- **2025 and 2026 are incomplete.** A sale appears only after its transfer is stamped and recorded, which can take months.
- **Mukim are NAPIC's administrative boundaries.** They may not match everyday neighbourhood names. For example, there is no "Titiwangsa" mukim.
- **Missing details:** there are no unit numbers, exact dates, unit condition or corner/end-lot information.
- NAPIC asks users to verify figures before relying on them.

## Source and citation

National Property Information Centre (NAPIC), Jabatan Penilaian dan Perkhidmatan Harta (JPPH). *Open Transaction Data*: Condominium/Apartment, W.P. Kuala Lumpur and Selangor. https://napic.jpph.gov.my/en/open-sales-data, accessed November 2026. Cleaning and summaries are derived work.

NAPIC states no licence for reuse, only a disclaimer that the government and NAPIC are not responsible for any loss arising from use of the information. This repository makes no claim over the underlying data.
