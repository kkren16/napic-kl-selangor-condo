import pandas as pd, numpy as np
d=pd.read_pickle('work/all.pkl')
g=d.groupby(['state','district','mukim','scheme'])
d['sch_n']=g.psf.transform('size'); d['sch_med']=g.psf.transform('median')
r=d.psf/d.sch_med
d['outlier']=(d.psf<50)|((d.sch_n>=5)&((r<0.4)|(r>2.5)))
c=d[~d.outlier].copy()
def agg(x):
    return pd.Series({'Transactions':len(x),'Median price (RM)':x.price_rm.median(),
        'Median PSF (RM)':x.psf.median(),'Median size (sq ft)':x.area_sqft.median()})
def summ(keys): return c.groupby(keys).apply(agg,include_groups=False).reset_index()
S={}
S['by_state']=summ(['state'])
S['by_state_year']=summ(['state','year'])
S['by_district']=summ(['state','district'])
S['by_district_tenure']=summ(['state','district','tenure'])
S['by_district_year']=summ(['state','district','year'])
S['by_mukim']=summ(['state','district','mukim'])
sch=summ(['state','district','mukim','scheme'])
ten=c.groupby(['state','district','mukim','scheme']).tenure.agg(lambda t:'/'.join(sorted(t.unique()))).reset_index()
rng=c.groupby(['state','district','mukim','scheme']).date.agg(['min','max']).reset_index()
early=c[c.year<=2022].groupby(['state','district','mukim','scheme']).agg(n_e=('psf','size'),psf_e=('psf','median')).reset_index()
late=c[c.year>=2024].groupby(['state','district','mukim','scheme']).agg(n_l=('psf','size'),psf_l=('psf','median')).reset_index()
k=['state','district','mukim','scheme']
sch=sch.merge(ten,on=k).merge(rng,on=k).merge(early,on=k,how='left').merge(late,on=k,how='left')
ok=(sch.n_e>=5)&(sch.n_l>=5)
sch['PSF change 2021-22 → 2024-26']=np.where(ok,sch.psf_l/sch.psf_e-1,np.nan)
S['by_scheme']=sch
c.to_pickle('work/clean.pkl'); d.to_pickle('work/flagged.pkl')
pd.to_pickle(S,'work/summ.pkl')
pd.set_option('display.width',200)
print(S['by_state'].round(0).to_string()); print(S['by_state_year'].round(0).to_string())
print(S['by_district'].round(0).to_string()); print(S['by_mukim'].sort_values('Transactions',ascending=False).head(15).round(0).to_string())
print(len(sch), ok.sum(), d.outlier.sum())
