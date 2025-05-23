import dash
from dash import html, dcc, Output, Input
import pandas as pd
import plotly.express as px

# Read the SpaceX launch data
spacex_df = pd.read_csv('spacex_launch_dash.csv')
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a list of launch sites for the dropdown
sites = [{'label': 'All Sites', 'value': 'ALL'}] + \
         [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = 'SpaceX Launch Dashboard'

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center'}),
    
    # TASK 1: Launch Site Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=sites,
        value='ALL',
        placeholder='Select a Launch Site',
        searchable=True
    ),
    html.Br(),

    # TASK 2: Success Pie Chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Payload Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=100,
        marks={
            int(min_payload): str(int(min_payload)),
            int(max_payload): str(int(max_payload))
        },
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Success-Payload Scatter Chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for updating pie chart based on selected site
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Aggregate success counts by site
        df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(df, names='Launch Site', title='Total Successful Launches by Site')
    else:
        # Filter for the selected site
        df = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = df['class'].value_counts().reset_index()
        counts.columns = ['Outcome', 'Count']
        counts['Outcome'] = counts['Outcome'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(counts, names='Outcome', values='Count',
                     title=f'Success vs Failure for site {selected_site}')
    return fig

# TASK 4: Callback for scatter chart showing payload vs. success
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    # Filter by payload range
    mask = (
    (spacex_df['Payload Mass (kg)'] >= low) &
    (spacex_df['Payload Mass (kg)'] <= high)
)
    filtered_df = spacex_df[mask]
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation between Payload and Success',
        labels={'class': 'Launch Outcome'}
    )
    return fig

# Run the app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
