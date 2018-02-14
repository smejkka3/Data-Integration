import pandas as pd
import numpy as np
import re
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from uszipcode import ZipcodeSearchEngine

def prepare_zip(df):
    zipcode = df['ZIP'].values[i]
    if zipcode.isdigit() == False:
        zipcode = re.sub("[^0-9]", "", zipcode)
        df.iloc[i, df.columns.get_loc('ZIP')] = zipcode
    return zipcode

def prepare_ssn(df):
    ssn = df['SSN'].values[i]
    
    if(pd.isnull(ssn)):
        ssn = '00000000'
    else:
        if ssn.isdigit() == False:
            ssn = re.sub("[^0-9]", "", ssn)
            while(len(ssn) < 8):
                ssn += '0'
            if(len(ssn)>10):
                ssn = ssn[:10]
    return ssn

def clean_ssn(df,i,ssn):
    df.iloc[i, df.columns.get_loc('SSN')] = ssn

def set_unknown(df,i):
    df.iloc[i, df.columns.get_loc('State')] = "UNKNOWN"
    df.iloc[i, df.columns.get_loc('City')] = "UNKNOWN"
    df.iloc[i, df.columns.get_loc('ZIP')] = "UNKNOWN"

def set_by_zip(zip,df,i):
    zip = search.by_zipcode(zip)
    df.iloc[i, df.columns.get_loc('City')] = zip.City
    df.iloc[i, df.columns.get_loc('State')] = zip.State

def set_by_state_and_city(res,L_state,df):
    res = search.by_city_and_state(res[0].City,L_state[0])
    df.iloc[i, df.columns.get_loc('ZIP')] = res[0].Zipcode
    df.iloc[i, df.columns.get_loc('City')] = res[0].City

#not really reliable to set zip based only on city because one city can have more zip codes
def set_by_city(df,i,res):
    df.iloc[i, df.columns.get_loc('ZIP')] = res[0].Zipcode
    df.iloc[i, df.columns.get_loc('State')] = res[0].State

#really bad recall, lot of zips and cities for one state
def set_by_state():
    df.iloc[i, df.columns.get_loc('ZIP')] = res[0].Zipcode
    df.iloc[i, df.columns.get_loc('City')] = res[0].City

search = ZipcodeSearchEngine()

df = pd.read_csv("inputDB.csv")

for i in range(len(df)):
    if(i%10000==0):
        print("Cleaned", i, " rows")
    zip = prepare_zip(df)
    ssn = prepare_ssn(df)

    clean_ssn(df,i,ssn)
    if len(zip) == 5:
        set_by_zip(zip,df,i)
    else:
        try:
            L_city = search._find_city(df['City'].values[i], best_match=True)
            df.iloc[i, df.columns.get_loc('City')] = L_city[0]
            res = search.by_city(L_city[0])
            if(len(res) == 0):
                try:
                    L_state = search._find_city(df['State'].values[i], best_match=True)
                    df.iloc[i, df.columns.get_loc('State')] = L_state[0]
                    res = search.by_state(L_state[0])
                    if(len(res) == 0):
                        set_unknown(df,i)
                    else:
                        set_by_state_and_city(res,L_state,df)
                except ValueError:
                    set_unknown(df,i)
            else:
                set_by_city(df,i,res)
        except ValueError:
            try:
                L_state = search._find_city(df['State'].values[i], best_match=True)
                df.iloc[i, df.columns.get_loc('State')] = L_state[0]
                res = search.by_state(L_state[0])
                if len(res) == 0:
                    set_unknown(df,i)
                else:
                    set_by_state(df,i,res)
            except ValueError:
                set_unknown(df,i)

df = df.replace(np.nan, '', regex=True)
df = df.apply(lambda x: x.astype(str).str.upper())
df.to_csv("inputDB.csv",index=False)
