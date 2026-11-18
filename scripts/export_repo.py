import pandas as pd, numpy as np, json, os
R='repo'; os.makedirs(f'{R}/data/summary',exist_ok=True); os.makedirs(f'{R}/data/summary_2024_2026',exist_ok=True)
d=pd.read_pickle('work/flagged.pkl')
t=pd.DataFrame({'state':d.state,'district':d.district,'mukim':d.mukim,'scheme':d.scheme,'tenure':d.tenure,
  'month':d.date.dt.strftime('%Y-%m'),'year':d.year.astype(int),'unit_level':d.level,'area_sqm':d.area_sqm,
  'area_sqft':d.area_sqft.astype('Int64'),'price_rm':d.price_rm.round(0).astype('Int64'),'psf_rm':d.psf.round(2),'outlier':d.outlier})
t=t.sort_values(['state','district','mukim','scheme','month']).reset_index(drop=True)
t.to_csv(f'{R}/data/transactions.csv',index=False)
c=t[~t.outlier]
def agg(g):
    x=c if g is None else g
    return x
def summ(df,keys):
    out=df.groupby(keys).agg(transactions=('price_rm','size'),median_price_rm=('price_rm','median'),
        median_psf_rm=('psf_rm','median'),median_size_sqft=('area_sqft','median')).reset_index()
    for k in ['median_price_rm','median_psf_rm','median_size_sqft']: out[k]=out[k].astype(float).round(0).astype(int)
    return out
levels={'by_state':['state'],'by_state_year':['state','year'],'by_district':['state','district'],
 'by_district_tenure':['state','district','tenure'],'by_district_year':['state','district','year'],
 'by_mukim':['state','district','mukim'],'by_mukim_year':['state','district','mukim','year'],
 'by_scheme':['state','district','mukim','scheme']}
files=[]
for folder,df in [('summary',c),('summary_2024_2026',c[c.year>=2024])]:
    for name,keys in levels.items():
        if folder=='summary_2024_2026' and 'year' in keys: continue
        s=summ(df,keys)
        if name=='by_scheme':
            ten=df.groupby(keys).tenure.agg(lambda x:'/'.join(sorted(x.unique()))).rename('tenure')
            rng=df.groupby(keys).month.agg(first_sale='min',last_sale='max')
            s=s.merge(ten,on=keys).merge(rng,on=keys)
        s=s.sort_values(keys).reset_index(drop=True)
        s.to_csv(f'{R}/data/{folder}/{name}.csv',index=False)
        s.to_json(f'{R}/data/{folder}/{name}.json',orient='records',indent=1,force_ascii=False)
        files.append((f'data/{folder}/{name}',len(s)))
meta={'source':'National Property Information Centre (NAPIC), JPPH — Open Transaction Data (napic.jpph.gov.my/en/open-sales-data)',
 'property_type':'Condominium/Apartment (resales only)','states':['W.P. Kuala Lumpur','Selangor'],
 'coverage':{'first_month':t.month.min(),'last_month':t.month.max()},'downloaded':'2026-11','generated':'2026-11-18',
 'transactions_total':int(len(t)),'transactions_used_in_medians':int(len(c)),'outliers_excluded':int(t.outlier.sum()),
 'outlier_rule':'psf_rm < 50, or in schemes with 5+ sales, psf below 0.4x or above 2.5x the scheme median psf',
 'sqm_to_sqft':10.7639,'note':'2025-2026 incomplete: sales appear only after stamping. Area is NAPIC parcel area.',
 'files':{f:n for f,n in files}}
json.dump(meta,open(f'{R}/data/metadata.json','w'),indent=2)
print(json.dumps(meta,indent=1)); 
