#dict to convert between month {int:string}
import calendar
MONTH_DICT = {idx:month.lower() for idx, month in enumerate(list(calendar.month_name)) if month}
MONTH_DICT_REV = {v:k for k,v in MONTH_DICT.items()}

#project directory
import pathlib
PROJECT_DIR = pathlib.Path(__file__).parents[1] #__file__ is an attribute of module variables.py
DATALOG = PROJECT_DIR.joinpath('data', 'datalog.csv')

#default start date
from datetime import datetime
START_DATE = datetime(year=2016, month=1, day=1)