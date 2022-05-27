import pandas as pd
import numpy as np
import json

df0 = pd.read_csv('usurdb_commercial.csv')

rates = df0[[
    'energyratestructure/period0/tier0rate',
    'energyratestructure/period1/tier0rate',
    'energyratestructure/period2/tier0rate',
    'energyratestructure/period3/tier0rate',
    'energyratestructure/period4/tier0rate',
    'energyratestructure/period5/tier0rate',
    'energyratestructure/period6/tier0rate',
    'energyratestructure/period7/tier0rate',
    'energyratestructure/period8/tier0rate',
    'energyratestructure/period9/tier0rate',
    'energyratestructure/period10/tier0rate',
    'energyratestructure/period11/tier0rate',
    'energyratestructure/period12/tier0rate',
    'energyratestructure/period13/tier0rate',
    'energyratestructure/period14/tier0rate',
    'energyratestructure/period15/tier0rate',
    'energyratestructure/period16/tier0rate',
    'energyratestructure/period17/tier0rate',
    'energyratestructure/period18/tier0rate',
    'energyratestructure/period19/tier0rate',
    'energyratestructure/period20/tier0rate',
    'energyratestructure/period21/tier0rate',
    'energyratestructure/period22/tier0rate',
    'energyratestructure/period23/tier0rate'
                                            ]].values.tolist()

demands = df0[[
    'demandratestructure/period0/tier0rate',
    'demandratestructure/period1/tier0rate',
    'demandratestructure/period2/tier0rate',
    'demandratestructure/period3/tier0rate',
    'demandratestructure/period4/tier0rate',
    'demandratestructure/period5/tier0rate',
    'demandratestructure/period6/tier0rate',
    'demandratestructure/period7/tier0rate',
    'demandratestructure/period8/tier0rate'
                                            ]].values.tolist()


rates = [[x for x in y if not np.isnan(x)] for y in rates]
demands = [[x for x in y if not np.isnan(x)] for y in demands]

df1 = pd.DataFrame({'name': df0['name'], 
                    'utility': df0['utility'],
                    'eiaid': df0['eiaid'],
                    'peakkwcapacitymax': df0['peakkwcapacitymax'],
                    'demand_structure': demands,
                    'demand_wkday_sch': df0['demandweekdayschedule'],
                    'demand_wkend_sch': df0['demandweekendschedule'],
                    'rate_structure': rates,
                    'rate_wkday_sch': df0['energyweekdayschedule'],
                    'rate_wkend_sch': df0['energyweekendschedule']})

a = json.loads(df1['rate_wkday_sch'].values.tolist()[0])

print(a[0][0])

                                        
# df1.to_pickle('usurdb_commercial_dataframe.pkl')

#df1 = pd.read_csv('usurdb_commercial_dataframe.csv')

