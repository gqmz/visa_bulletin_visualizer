#imports for HTML extraction
import requests
import lxml.html as lh
import pandas as pd 
import numpy as np

#import for url parsing
from urllib.parse import urlparse, urlunparse, ParseResult

#import for url validation
from validators import ValidationFailure
from validators.url import url

#import global variables
import tools.variables as variables

#imports for dealing with datetime objects
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime

class validUrl():
    """
    Checks if url is valid, doesn't check if it exists.
    """
    def __init__(self, url):
        self.url = url
    
    def is_valid_url(self):
        result = url(self.url)
        if isinstance(result, ValidationFailure):
            return False
        return result

class getUrlData():
    """
    example of valid url: 'https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2021/visa-bulletin-for-january-2021.html'
    Using valid url, extract:
    1. month, year of bulletin
    2. 2 employment based tables
    3. add month, year to tables
    4. store both tables
    """
    def __init__(self, valid_url):
        self.valid_url = valid_url
        self.get_tables()

    def get_date(self):
        """
        extract & assign month & year attributes
        """
        parsed_url = urlparse(self.valid_url)
        page = parsed_url.path.split('/')[-1] #'visa_bulletin-for-<month>-<year>.html
        page_elements = page.split('.')[0].split('-')

        self.month = page_elements[3]
        self.year = page_elements[4]

    def get_tables(self):
        #extract date from url
        self.get_date()

        #extract employment tables from url
        tables = pd.read_html(self.valid_url)
        employment_tables = [x for x in tables if len(x)==9] #employment tables have len=9
        
        table_list = []
        for idx, table in enumerate(employment_tables):
            #set first row of table as column
            columns = table.iloc[0]
            columns[0:4] = ['EBn', 'ALL', 'CHINA', 'CENTRALAMERICA']
            new_table  = pd.DataFrame(table.values[1:], columns=columns)

            #specify state of table
            if idx==0:
                new_table.loc[:, 'state'] = 'final'
            else:
                new_table.loc[:, 'state'] = 'filing'
            table_list.append(new_table)
        
        self.data = pd.concat(table_list) #set object data attribute

        #add datetime to table
        self.data['date'] = '-'.join([self.year, str(variables.MONTH_DICT_REV[self.month]), '1'])
        self.data['date'] = pd.to_datetime(self.data['date'])

        #repluce 'U' (unauthorized) with NaN
        self.data.replace(to_replace='U', value=np.nan, inplace=True)

class urlGen():
    """
    Generates list of valid urls
    Inputs:
        start & end dates as datetime objects
    """
    def __init__(self, start_dt=datetime(2010,1,1), end_dt=datetime.now()):
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.url_list = self.generate_list()

    def build_path(self, month, year):
        prefix = '/content/travel/en/legal/visa-law0/visa-bulletin/'
        page = '-'.join(['/visa-bulletin-for-', month, str(year)]) + '.html'
        return prefix + str(year)  + page

    def generate_list(self):
        url_list = []

        #generate month, year from 2010 to now: https://stackoverflow.com/a/155172
        for dt in rrule(freq=MONTHLY, dtstart=self.start_dt, until=self.end_dt):
            month = variables.MONTH_DICT[dt.month] #get month as string
            year = dt.year #int

            url_obj = ParseResult(scheme='https',
                                    netloc='travel.state.gov',
                                    path=self.build_path(month, year),
                                    params='', query='', fragment='')
            url_list.append(urlunparse(url_obj))
        return url_list