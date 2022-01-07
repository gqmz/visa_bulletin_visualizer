#dash imports
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

#plotly imports
import plotly.express as px

#others
import pandas as pd
import numpy as np
import variables#change to plots.variables when calling from PROJECT_DIR
import pathlib
import sys
from datetime import datetime
epoch = datetime.utcfromtimestamp(0)

#data import 
if not variables.DATALOG.is_file():
    print("Datalog missing")
    sys.exit(0)
else:
    df = pd.read_csv(variables.DATALOG)
    if len(df.index)==0:
        print("Empty dataframe")
        sys.exit(0)
    else:
        print("good to go")
        countries = list(set(df.columns) - set(['EBn', 'state', 'date']))
        for country in countries:
            df[country] = pd.to_datetime(df[country])
        df = pd.melt(df, id_vars=['EBn', 'state', 'date'], value_vars=countries, var_name='country', value_name='priority')

"""
TO DO
1. single x & y-axis label for all subplots (https://stackoverflow.com/a/58180284)
2. figure sizing
3. stylesheets?
"""


app = dash.Dash(
    __name__
)

app.layout = html.Div(
    children=[
        #header1
        html.H1(
            children="Visualize the employment-based priority dates released by USCIS",
            className="header1"
        ),

        #header2
        html.H2(
            children="Data source: https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html",
            className="header2"
        ),

        #Dropdown for country selection
        html.Div(
            children=[
                #text for dropdown
                html.Div(
                    children=[
                        dcc.Markdown("Select country:"),
                    ]
                ),
                #dropdown
                html.Div(
                    children=[
                        dcc.Dropdown(
                            id='country-selection-dropdown',
                            options=[
                                {"label": s, "value":s} for s in df['country'].unique()
                            ],
                            value='CHINA', #default value of dropdown
                            className="dropdown"
                        )
                    ]
                ),
            ]
        ),

        #DatePickerSingle to pick your priority date
        html.Div(
            children=[
                #Text for date picker
                html.Div(
                    children = [
                        dcc.Markdown("Select your priority date (appears as horizontal line in plot):"),
                    ]
                ),
                #date picker
                html.Div(
                    children=[
                        dcc.DatePickerSingle(
                            id='date-picker-single',
                            min_date_allowed=datetime(2016, 1, 1),
                            max_date_allowed=datetime.now(),
                            initial_visible_month=datetime(2017, 8, 5),
                            date=datetime(2017, 8, 25),
                            className='date-picker'
                        )
                    ]   
                ),
            ]

        ),

        #graph
        dcc.Graph(id="all-data")
    ],
    className="container"
)

@app.callback(
    Output("all-data", "figure"),
    Input("country-selection-dropdown", "value"),
    Input("date-picker-single", "date")
)
def update_figure(selected_country, priority_date):
    filtered_dataset = df.loc[df['country']==selected_country]
    priority_date = datetime.fromisoformat(priority_date)

    #figure
    y = 'priority'
    x = 'date'
    color = 'state'

    fig = px.scatter(
        filtered_dataset,
        x=x, y=y, color=color,
        labels={
            color: "Visa Stage"
        },
        height=800,
        facet_col='EBn', facet_col_wrap=4,
        title="Priority dates by employment visa class"
    )
    #adding datetime as hline/vline: https://github.com/plotly/plotly.py/issues/3065#issuecomment-778652215
    fig.add_hline(y=(priority_date - epoch).total_seconds() * 1000.0, 
        # annotation_text="Priority Date",
        line_width=1, line_dash="dash", 
        line_color="green"
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
