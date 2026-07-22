# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
from pathlib import Path

# Read the SpaceX launch data into a pandas dataframe.
DATA_FILE = Path(__file__).with_name("spacex_launch_dash.csv")
spacex_df = pd.read_csv(DATA_FILE)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites = sorted(spacex_df['Launch Site'].unique())

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}]
                                    + [{'label': site, 'value': site} for site in launch_sites],
                                    value='ALL',
                                    placeholder='Select a Launch Site here',
                                    searchable=True,
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={value: str(value) for value in range(0, 10001, 1000)},
                                    value=[min_payload, max_payload],
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
)
def get_pie_chart(entered_site):
    """Render site successes, or success/failure outcomes for one site."""
    if entered_site == 'ALL':
        successes_by_site = spacex_df[spacex_df['class'] == 1]
        return px.pie(
            successes_by_site,
            names='Launch Site',
            title='Total Successful Launches by Site',
        )

    site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    return px.pie(
        site_df,
        names='class',
        title=f'Total Launch Outcomes for {entered_site}',
        labels={'class': 'Launch Outcome'},
    )

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value'),
)
def get_scatter_chart(entered_site, payload_range):
    """Render launch outcome versus payload for the selected filters."""
    low, high = payload_range
    filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(low, high)]
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

    return px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation between Payload and Success for all Sites'
        if entered_site == 'ALL'
        else f'Correlation between Payload and Success for {entered_site}',
        labels={'class': 'Launch Outcome'},
    )


# Run the app
if __name__ == '__main__':
    app.run()
