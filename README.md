# Visa Bulletin Visualizer

Dash web app to visualize employment-based priority date data released by USCIS [link](https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html). Specifically, data tables are pulled from every monthly bullentin since 2016 and plotted by visa class. The user can select data by country and insert a marker for priority date.

## Repository structure

```
.gitignore
Procfile
dash_plots.py
data
   |-- datalog.csv
plots
   |-- __init__.py
   |-- dash_plots.py
   |-- tutorial.py
   |-- variables.py
requirements.txt
runtime.txt
tests
   |-- __init__.py
   |-- test_getUrlData.py
   |-- test_validUrl.py
tools
   |-- __init__.py
   |-- data.py
   |-- variables.py
```
Procfile, requirement.txt & runtime.txt are required to deploy the Dash web app on [Heroku](https://dashboard.heroku.com/login).

## Usage

### Repository setup

To run this application, you'll need [Git](https://git-scm.com/) installed on your machine. From your command line:

```
# Clone this repository
$ git clone https://github.com/gqmz/visa_bulletin_visualizer.git

# Go in the repository
$ cd visa_bulletin

# Install dependencies
$ pip install -r requirements.txt
```

### Launch Dash app locally

```
# Run the dash app on localhost
$ python dash_app.py
```