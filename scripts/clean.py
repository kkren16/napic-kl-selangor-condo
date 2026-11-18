import openpyxl, pandas as pd, numpy as np
cols=['ptype','district','mukim','scheme','road','month','tenure','area','area_unit','mfa','mfa_unit','level','price']
out=[]
for f,state in [('work/kl.xlsx','W.P. Kuala Lumpur'),('work/sel.xlsx','Selangor')]:
    wb=openpyxl.load_workbook(f); ws=wb.active
    for r in list(ws.merged_cells.ranges):
        v=ws.cell(r.min_row,r.min_col).value
        ws.unmerge_cells(str(r))
        for row in range(r.min_row,r.max_row+1):
            for col in range(r.min_col,r.max_col+1):
                ws.cell(row,col).value=v
    rows=list(ws.iter_rows(min_row=2,values_only=True))
    d=pd.DataFrame(rows,columns=cols).astype(str).replace({'None':np.nan,'':np.nan})
    d['state']=state; out.append(d)
d=pd.concat(out,ignore_index=True)
d=d[d.price.notna()]
for c in ['ptype','district','mukim','scheme','month','tenure']: d[c]=d[c].str.strip()
d['scheme']=d.scheme.str.upper().str.replace(r'\s+',' ',regex=True)
d['price_rm']=pd.to_numeric(d.price.str.replace(r'[RM,\s]','',regex=True),errors='coerce')
d['area_sqm']=pd.to_numeric(d.area.str.replace(',',''),errors='coerce')
d['area_sqft']=(d.area_sqm*10.7639).round(0)
d['psf']=d.price_rm/(d.area_sqm*10.7639)
# NAPIC records two developments under "THE ORION" (KL Town Centre): the 2006 condo on Jalan Tun Razak
# (~RM430-600 psf) and a much newer high-rise whose units first transferred in 2024 (~RM1,800-3,900 psf).
orion=d.scheme.eq('THE ORION')
d.loc[orion&(d.psf<1000),'scheme']='THE ORION (JALAN TUN RAZAK)'
d.loc[orion&(d.psf>=1000),'scheme']='THE ORION (NEWER HIGH-RISE, 2024 TRANSFERS)'
d['date']=pd.to_datetime(d.month,format='%B %Y',errors='coerce')
d['year']=d.date.dt.year
d['level']=d.level.str.strip()
d.to_pickle('work/all.pkl')
print(d.groupby('state').size()); print(d.isna().sum()[lambda s:s>0])
print(d.groupby(['state','year']).size().unstack(0))
print(d.date.min(), d.date.max())
print(d.groupby('state').district.value_counts())
print(d[['price_rm','area_sqm','psf']].describe(percentiles=[.001,.005,.01,.5,.99,.999]).to_string())
