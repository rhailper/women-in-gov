import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import time

def obtain_data(day,month,year, pre2019=True):
    '''Function that reads in the data from the ipu archives'''
    if pre2019==True:
        return pd.read_html(
            f'http://archive.ipu.org/wmn-e/arc/classif{day}{month}{year}.htm',
            header=[1],
        )[1]
    else:
        return pd.read_csv(
        f'https://data.ipu.org/api/women-ranking.csv?load-entity-refs=taxonomy_term%2Cfield_collection_item&max-depth=2&langcode=en&month={month}&year={year}'
        ) 

def clean(df):
    '''Function that corrects the column headers'''
    # Sets the multi-level columns using the columns and first row
    df.columns=pd.MultiIndex.from_tuples(zip(df.columns,df.iloc[0].values))
    df = df.iloc[1:, :]
    return df

# Extract all links from ipu archive page
url = 'http://archive.ipu.org/wmn-e/classif-arc.htm' # url to ipu archives page
page = requests.get(url)
data = page.text
soup = BeautifulSoup(data,features='lxml')

links = [link.get('href') for link in soup.find_all('a')]
# Extract dates from links
dates = [
    re.search(r'classif(.*?).htm', link)[1]
    for link in links
    if re.search(r'classif(.*?).htm', link) is not None
    and len(re.search(r'classif(.*?).htm', link)[1]) == 6
]
dates = [(date[:2], date[2:4], date[4:6]) for date in dates]

# Loop through months and years 1997-2018 and pull the data, save each file to the data/world_data folder
for d, m, y in dates:
    try:
        df = clean(obtain_data(d,m,y))
        # save dataframe to folder but change format of name to make formatting consistent (ex: 'wd_month_year')
        if (m[0]=='0') & (int(y)>19):
            df.to_csv('data/world_data/' + 'wd_' + m[1] + '_' + '19' + y + '.csv', index=False)
        elif (m[0]=='0') & (int(y)<=19):
            df.to_csv('data/world_data/' + 'wd_' + m[1] + '_' + '20' + y + '.csv', index=False)
        elif (m[0]>'0') & (int(y)>19):
            df.to_csv('data/world_data/' + 'wd_' + m + '_' + '19' + y + '.csv', index=False)
        else:
            df.to_csv('data/world_data/' + 'wd_' + m + '_' + '20' + y + '.csv', index=False)
    except Exception:
        print(f'{str(m)},' + y + ' did not work.')
    time.sleep(15)


# The websites for 2019-2022 differed slightly from the previous years. Because of this, a slightly modified proccess was used to pull in this data.
# Loop through months and years 2019-2022 and pull the data, save each file to the data/world_data folder
day='na'
for year in ['2019','2020','2021','2022']:
    for month in range(1,13):
        try:
            df = obtain_data(day,month,year,pre2019=False)
            df.to_csv('data/world_data/' + 'wd_' + str(month) + '_' + year + '.csv', index=False)
        except:
            print(f'{str(month)} {year} + did not work.')
        time.sleep(15)