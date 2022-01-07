#code adapted from https://towardsdatascience.com/plotly-dashboards-in-python-28a3bb83702c

import dash
from dash import dcc, html
from pandas.io.formats import style
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

app = dash.Dash(
    __name__,
)

df = pd.read_csv(
    "https://raw.githubusercontent.com/ThuwarakeshM/geting-started-with-plottly-dash/main/life_expectancy.csv"
)

colors = {"background": "#011833", "text": "#7FDBFF"}
markdown_text = '''
Filter countries by development status using the 1st dropdown box.
Filter datapoints that have avg. no. of schooling years greater than the value in the 2nd dropdown box.
Lastly, choose the year for which you want to view data using the slider.
'''

#the layout property is the root of a Dash app's element hierarchy
#define layout components below
app.layout = html.Div(
    [
        #header
        html.H1(
            children="My Dashing Dashboard",
            style={"color":"#0000FF"}, #example of inline styling, every component has a style arg
            className='title'
        ),

        #markdown (block of text)
        html.Div(
            dcc.Markdown(children=markdown_text),
            className='pagemarkdown'
        ),

        #div for dropdown lists
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Country Development Status"),
                        dcc.Dropdown(
                            id="status-dropdown",
                            options=[
                                {"label": s, "value": s} for s in df.Status.unique()
                            ],
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Average schooling years greater than"),
                        dcc.Dropdown(
                            id="schooling-dropdown",
                            options=[
                                {"label": y, "value": y}
                                for y in range(
                                    int(df.Schooling.min()), int(df.Schooling.max()) + 1
                                )
                            ],
                            className="dropdown",
                        ),
                    ]
                ),
            ],
            className="row",
        ),

        #div for slider
        html.Div(
            [
                html.Label("Year Selection"),
                dcc.Slider(
                    id="year-slider",
                    min=df.Year.min(),
                    max=df.Year.max(),
                    step=None,
                    marks={year: str(year) for year in range(df.Year.min(), df.Year.max() + 1)}, #value: str label
                    value=df.Year.median(), #default value of slider
                ),
            ],
            className="slider"
        ),


        #plot title
        html.H2(children="The Plot",
            style={"color":"#FF0000"},
            className='graph1_name'
        ),

        #placeholder to render the chart
        html.Div(
            [
                html.Label("El Plotto"),
                dcc.Graph(id="life-exp-vs-gdp")
            ],
            className="graph1"
        )
    ],
    className="container",
)

#(component ID, property to change)
@app.callback(
    Output("life-exp-vs-gdp", "figure"), #returned object is assigned to component's fig attribute
    Input("year-slider", "value"), #input 1: selected_year
    Input("status-dropdown", "value"), #input 2: country_status
    Input("schooling-dropdown", "value"), #input 3: schooling
)#this is the decorator for the function below
def update_figure(selected_year, country_status, schooling):
    filtered_dataset = df[(df.Year == selected_year)]

    if schooling:
        filtered_dataset = filtered_dataset[filtered_dataset.Schooling <= schooling]

    if country_status:
        filtered_dataset = filtered_dataset[filtered_dataset.Status == country_status]

    #everytime we run the callback function, it creates a new figure instance and updates the UI
    #plotly express tightly integrates with pandas dataframes
    fig = px.scatter(
        filtered_dataset,
        x="GDP",
        y="Life expectancy",
        size="Population",
        color="continent",
        hover_name="Country",
        log_x=True,
        size_max=60,
    )

    fig.update_layout(
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
    )

    return fig

if __name__ == "__main__":
    app.run_server(debug=True, #automatically refresh browser with change in saved code (hot-reloading)
        port=8051)