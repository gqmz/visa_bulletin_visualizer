import pandas as pd 
import numpy as np
import regex as re

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

#file manipulation
import pathlib

"""
Class definitions
"""

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
        self.get_date()
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
        #extract employment tables from url
        try:
            tables = pd.read_html(self.valid_url)
            self.check_tables(tables)
        except Exception as e:
            print(f"Exception during pd.read_html {e}")
            print(f"url: {self.valid_url}")
            self.data = pd.DataFrame()

    def check_tables(self, tables):
        """
        check for employment tables
        Post 2010 urls expect exactly 2 tables meeting criterion
        """
        employment_tables = [x for x in tables if len(x)==9] #employment tables have len=9
        if len(employment_tables)==2:
            try:
                self.combine_tables(employment_tables) #combine tables into data attribute
                self.data_column_operations()
                self.data_row_operations()
            except Exception as e:
                #if ANY error occurs during table processing
                print(f"Exception during table processing {e}")
                print(f"url: {self.valid_url}")
                self.data = pd.DataFrame()
        else:
            self.data = pd.DataFrame()

    def combine_tables(self, employment_tables):
        """
        Input:
            employment_tables: contains 2 tables, one each for final & final action dates for employment-based green cards
        1. Set standardized columns for EACH table read from url
        2. Concat tables into data attribute
        """
        #1. Set standardized columns for EACH table read from url
        for idx1, table in enumerate(employment_tables):
            columns = list(table.iloc[0]) #first row contains raw columns names
        
            #iterate through column names & modify list elements
            for idx, col in enumerate(columns):
                if 'CHINA' in col:
                    columns[idx] = 'CHINA'
                elif any(s in col for s in ['EL', 'SALVADOR', 'GUATEMALA']):
                    columns[idx] = 'CENTRALAMERICA'
                elif 'Employment' in col:
                    columns[idx] = 'EBn'
                elif any(s in col for s in ['All', 'Chargeability', 'Except']):
                    columns[idx] = 'ALL'
                else:
                    pass #don't change this element

            #modify attribute with correct row selection, standard columns
            employment_tables[idx1]  = pd.DataFrame(table.values[1:], columns=columns)

            #add state of table
            if idx1==0:
                employment_tables[idx1]['state'] = 'final'
            else:
                employment_tables[idx1]['state'] = 'filing'

        #2. Concat tables into data attribute
        self.data = pd.concat(employment_tables)

    def data_column_operations(self):
        """
        Modify data columns in place
        1. add bulletin date as column
        """
        #1. add bulletin date as column
        self.data['date'] = '-'.join([self.year, str(variables.MONTH_DICT_REV[self.month]), '1'])#add bulletin release date as column (YYYY-MM-DD format)

    def data_row_operations(self):
        """
        Modify data rows in place
        1. U->np.nan
        2. clean up EBn column values
        3. C->bulletin date, swap out dates
        """
        #1. U->np.nan
        self.data.replace(to_replace='U', value=np.nan, inplace=True)

        #2. clean up EBn column values
        def categories(x):
            """
            Define how to modify cell value
            """
            if any(s in x for s in ['I5', 'R5']):
                return '5th regional'
            elif any(s in x for s in ['C5', 'T5']):
                return '5th non-regional'
            elif any(s in x for s in ['Certain', 'Religious']):
                return 'Religious Workers'
            else:
                return x
        self.data['EBn'] = self.data['EBn'].apply(lambda x: categories(x))

        #3. C->bulletin date, swap out dates
        month_abbr_dict = {k[0:3].upper():str(v) for k,v in variables.MONTH_DICT_REV.items()}
        def swap_dates(x):
            if x!=x: #math.isnan(x) throws TypeError: must be real number, not str
                return x #return np.nan as is
            elif re.match(r"^\d{2}[A-Z]{3}\d{2}", x): #match date format from url
                day, month, year = x[0:2], x[2:5], x[5:]
                x = '-'.join(['20'+year, month_abbr_dict[month], day])

            return x #returns swapped date or previously filled in date (the C's)
        countries = list(set(self.data.columns) - set(['EBn', 'state', 'date']))
        for country in countries:
            self.data[country] = np.where(self.data[country]=='C', self.data['date'], self.data[country])
            self.data[country] = self.data[country].apply(lambda x: swap_dates(x))
        
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
        #both month & year come in as ints
        prefix = '/content/travel/en/legal/visa-law0/visa-bulletin/'
        page = '-'.join(['/visa-bulletin-for', 
                        variables.MONTH_DICT[month], 
                        str(year)]) + '.html'

        fiscal_year = year+1 if month>=10 else year #fiscal year starts in October
        return prefix + str(fiscal_year) + page

    def generate_list(self):
        url_list = []

        #generate month, year from 2010 to now: https://stackoverflow.com/a/155172
        for dt in rrule(freq=MONTHLY, dtstart=self.start_dt, until=self.end_dt):
            month = dt.month #int  #get month as string
            year = dt.year #int

            #https://stackoverflow.com/a/53993037
            url_obj = ParseResult(scheme='https',
                                    netloc='travel.state.gov',
                                    path=self.build_path(month, year),
                                    params='', query='', fragment='')
            url_list.append(urlunparse(url_obj))
        return url_list

class buildDatabase():
    """
    Write to ~/data/datalog.csv
    Inputs:
        start_dt, end_dt: start & end datetime object
        all: 
            True->delete datalog if exists, download all data and save to datalog
            False->check for datalog:
                IF doesn't exist, switch to all=True mode
                ELSE, download & save latest data
    """
    def __init__(self, all=True):
        self.all = all
        self.router()

    def router(self):
        """
        routes control flow based on value of self.all
        """
        if self.all:
            variables.DATALOG.unlink(missing_ok=True) #delete file, will be replaces
            #build url_list
            data = self.get_url_data() #use defaults
            data.to_csv(variables.DATALOG, index=None)
        else: #user wants to update datalog
            if not variables.DATALOG.is_file(): #datalog doesn't exist
                #build url_list
                data = self.get_url_data()
                data.to_csv(variables.DATALOG, index=None)
            else: #datalog exists
                old_data = pd.read_csv(variables.DATALOG)

                #find start date
                old_data['date'] = pd.to_datetime(old_data['date'])
                latest_date = old_data['date'].max() #pandas.Timestamp object
                # (year, month, day) = [int(x) for x in latest_date.split('-')]
                (year, month, day) = latest_date.year, latest_date.month, latest_date.day 

                start = datetime(year=year+int(month/12),
                                    month=(month%12)+1, day=1)
                print(latest_date, start)
                
                #build url_list
                data = self.get_url_data(start=start)
                variables.DATALOG.unlink(missing_ok=True) #delete file, will be replaces
                pd.concat([old_data, data]).to_csv(variables.DATALOG, index=None)

    def get_url_data(self, start=variables.START_DATE, end=datetime.now()):
        """
        Input:
            start & end datetime objects
        Output:
            dataframe object
        """
        data = pd.DataFrame()

        gen = urlGen(start_dt=start, end_dt=end)
        """
        note: start date is calculated as (latest_month in DATALOG) + 1, 
        so if user uses self.all=True when (latest_month in DATALOG) == current month, rrule will not iterate in urlGen
        """
        if len(gen.url_list)>0:
            table_list = []
            for url in gen.url_list:
                if validUrl(url).is_valid_url(): #validate url
                    data_object = getUrlData(url)
                    table_list.append(data_object.data)

            #concat data object from all urls
            data = pd.concat(table_list)
        return data



    