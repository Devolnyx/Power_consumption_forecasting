import yaml
import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

#import locale
#locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

try:
    project_path = os.path.abspath(os.path.curdir)
    config_path = "/config/config.yaml"
    config = yaml.safe_load(open(project_path + config_path))
except:
    config = yaml.safe_load(open("/opt/airflow/config/config_airflow.yaml"))

colors = {
    'grid': "#b9b9b9",
    'graph_font': "#000000",
    'plot_area': "#ffffff",
    'plot_background': "#fafafa",
    'background_color': '#ffffff'
}

# Create a dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])


def plot(data, predictions, num_records, title):

    fig = go.Figure(
        data=[go.Scatter(x=data[-num_records:]['dt'], y=data[-num_records:]['value'], fill='tozeroy', name='Показания'),
              go.Scatter(x=predictions['dt'], y=predictions['value'], fill='tozeroy', name='Прогноз'),
              ]
    )

    fig.update_layout(height=400,
                      xaxis=dict(gridcolor=colors['grid'],
                                 showline=True, linewidth=1, linecolor=colors['grid'], mirror=True),
                      yaxis=dict(gridcolor=colors['grid'], zeroline=False,
                                 showline=True, linewidth=1, linecolor=colors['grid'], mirror=True),
                      yaxis_title="КВт*ч",
                      font_color=colors['graph_font'],
                      title_text=title,
                      plot_bgcolor=colors['plot_area'],
                      paper_bgcolor=colors['plot_background'],
                      hovermode="x unified",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                      margin=dict(l=20, r=20, b=30, t=80, pad=1),
                      )

    fig.update_yaxes(
        title_standoff=3,
        title_font={"size": 12})

    return fig


header = html.Div(
        html.Div(dbc.Button("Обновить", id="update", n_clicks=0, className="ant-electro-btn-primary",
            style={'margin': '3px', 'margin-right': '1%', 'font-size': '14px'}), style={'float': 'right'}),
        style={'margin-top': '5px', 'margin-bottom': '5px', 'width': '100%', 'padding-right': '2%',
                    'backgroundColor': "grey", 'box-shadow': '2px 2px 2px rgba(0,0,0,0.3)'})

graphs_content = dbc.Container(
    [
        dbc.Row([
            dcc.Loading(type="circle",
            children=[dcc.Graph(id='onestep_plot', animate=False,
                           config={'displaylogo': False, 'locale': 'ru'})]
            )
        ], style={'padding': '5px'}),
        dbc.Row([
            dcc.Loading(type="circle",
                        children=[dcc.Graph(id='multistep_plot', animate=False,
                                            config={'displaylogo': False, 'locale': 'ru'})]
            )
        ], style={'padding': '5px'})
    ], fluid=True, style={'background-color': colors['background_color']}
)

app.layout = html.Div(children=[
    dcc.Store(id='memory'),
    dcc.Interval(
        id='interval-component',
        interval=5 * 60 * 1000,  # 5 minutes in milliseconds
        n_intervals=0),
    dbc.Row(header, style={'display': 'flex'}),
    dbc.Row(graphs_content)
])


@app.callback([Output(component_id='memory', component_property='data')],
              [Input(component_id='interval-component', component_property='n_intervals'),
              Input(component_id='update', component_property='n_clicks')]
              )
def update_data(n, n_clicks):
    data = []
    data_path = os.path.join('./resources/')
    data_list = os.listdir(data_path)
    for csv in sorted(data_list):
        if csv.endswith('.csv'):
            data.append(pd.read_csv(os.path.join(data_path, csv)).to_json())
    return [data]


@app.callback([Output(component_id='onestep_plot', component_property='figure'),
               Output(component_id='multistep_plot', component_property='figure')],
              Input(component_id='memory', component_property='data')
              )
def update_data(data):
    multistep_df = pd.read_json(data[0]).dropna(subset=['value'])
    multistep_pred = pd.read_json(data[1])
    onestep_df = pd.read_json(data[2]).dropna(subset=['value'])
    onestep_pred = pd.read_json(data[3])

    fig1 = plot(multistep_df, multistep_pred, 48, 'Прогноз потребление электроэнергии (24 часа)')
    fig2 = plot(onestep_df, onestep_pred, 12, 'Прогноз потребление электроэнергии (30 минут)')
    return [fig1, fig2]

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
