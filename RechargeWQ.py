#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Load and process data
df = pd.read_csv('Recharge Water Quality.csv')
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Result', 'Site', 'Compound', 'Units'])

# Initialize Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Recharge Water Quality Dashboard", style={'textAlign': 'center'}),
    
    html.Label("Select Site:"),
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': site, 'value': site} for site in sorted(df['Site'].unique())],
        value=df['Site'].unique()[0]
    ),

    html.Label("Select Compound:"),
    dcc.Dropdown(
        id='compound-dropdown',
        options=[{'label': compound, 'value': compound} for compound in sorted(df['Compound'].unique())],
        value=df['Compound'].unique()[0]
    ),

    dcc.Graph(id='scatter-plot'),

    html.Button("Download Data", id="download-btn", n_clicks=0),
    dcc.Download(id="download-dataframe-csv")
])


# Callback to update the plot
@app.callback(
    Output('scatter-plot', 'figure'),
    Input('site-dropdown', 'value'),
    Input('compound-dropdown', 'value')
)
def update_plot(site, compound):
    filtered_df = df[(df['Site'] == site) & (df['Compound'] == compound)]
    
    if filtered_df.empty:
        return px.scatter(title=f"No data available for {compound} at {site}")

    unit = filtered_df['Units'].iloc[0] if not filtered_df['Units'].isna().all() else 'Unknown Unit'
    mcl_value = filtered_df['MCL'].iloc[0] if 'MCL' in filtered_df.columns else 'none'
    title = f'Results for {compound} at {site} (MCL = {mcl_value} {unit})'

    fig = px.scatter(
        filtered_df,
        x='Date',
        y='Result',
        color='Source',
        title=title,
        labels={'Result': f'Concentration ({unit})', 'Date': 'Date'},
        template='plotly_white',
        color_discrete_map={
            'Ground Water': 'rgb(95,153,174)',
            'Surface Water': 'rgb(55,58,64)'
        }
    )
    
    fig.update_traces(marker=dict(size=10))
    
    fig.update_layout(
        paper_bgcolor='rgb(245, 245, 247)',
        hovermode='x unified',
        showlegend=True,
        legend_title_text='Source',
        height=600
    )

    return fig


# Callback to handle CSV download
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-btn", "n_clicks"),
    Input("site-dropdown", "value"),
    Input("compound-dropdown", "value"),
    prevent_initial_call=True
)
def download_data(n_clicks, site, compound):
    filtered_df = df[(df['Site'] == site) & (df['Compound'] == compound)]
    return dcc.send_data_frame(filtered_df.to_csv, "filtered_data.csv")


# Run the app
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8080, debug=True)

