# wrds 
import wrds 
 
# common packages 
import os 
import re 
import pandas as pd 
import numpy as np 
import pickle as pkl 
from pprint import pprint 
from collections import OrderedDict 
from collections import defaultdict 
import multiprocessing  

conn = wrds.Connection() 
 
# Get S&P500 Index Membership from CRSP 
sp500 = conn.raw_sql(""" 
    select a.*, b.date, b.ret 
    from crsp.msp500list as a, crsp.msf as b 
    where a.permno=b.permno 
    and b.date >= a.start and b.date<= a.ending 
    and b.date>='01/01/2000' 
    order by date; 
""", date_cols=['start', 'ending', 'date']) 

# Add Other Company Identifiers from CRSP.MSENAMES 
mse = conn.raw_sql(""" 
    select comnam, ncusip, namedt, nameendt, permno, shrcd, exchcd, hsiccd, ticker 
    from crsp.msenames 
""", date_cols=['namedt', 'nameendt'])

# if nameendt is missing then set to today date 
mse['nameendt'] = mse['nameendt'].fillna(pd.to_datetime('today'))

# Merge with SP500 data 
sp500_full = pd.merge(sp500, mse, how='left', on='permno')
sp500_full = sp500_full.loc[(sp500_full.date>=sp500_full.namedt) & (sp500_full.date<=sp500_full.nameendt)]

ccm = conn.raw_sql(""" 
    select gvkey, liid as iid, lpermno as permno, linktype, linkprim, linkdt, linkenddt 
    from crsp.ccmxpf_linktable 
    where substr(linktype,1,1)='L' 
    and (linkprim='C' or linkprim='P') 
""", date_cols=['linkdt', 'linkenddt'])

# Set linkenddt to today if missing 
ccm['linkenddt'] = ccm['linkenddt'].fillna(pd.to_datetime('today'))

# Merge with SP500 data 
sp500ccm = pd.merge(sp500_full, ccm, how='left', on=['permno'])
sp500ccm = sp500ccm.loc[(sp500ccm['date'] >= sp500ccm['linkdt']) & (sp500ccm['date'] <= sp500ccm['linkenddt'])]

# Add CIK and merge with SEC Index 
names = conn.raw_sql("select gvkey, cik, sic, naics, gind, gsubind from comp.names")
sp500cik = pd.merge(sp500ccm, names, on='gvkey', how='left')

sp500cik.to_csv('sp500cik.csv', index=False)