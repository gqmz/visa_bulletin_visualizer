#imports for HTML extraction
import requests
import lxml.html as lh
import pandas as pd 
import numpy as np

#import for url parsing
from urllib.parse import urlparse
import validators
from validators import ValidationFailure
from validators.url import url

class validUrl():
    """
    Checks if url is valid, doesn't check if it exists.
    """
    def __init__(self, url):
        self.url = url
    
    def is_valid_url(self):
        result = validators.url(self.url)
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
        
        #type-cast year
        try:
            self.year = int(self.year)
        except ValueError:
            print("URL year is not an integer")

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
            table = table[1:]
            table.columns = columns

            #specify state of table
            if idx==0:
                table['state'] = 'final'
            else:
                table['state'] = 'filing'
            table_list.append(table)
        
        self.data = pd.concat(table_list) #set object data attribute
        self.data['month'] = self.month
        self.data['year'] = self.year

        #repluce 'U' (unauthorized) with NaN
        self.data.replace(to_replace='U', value=np.nan, inplace=True)
