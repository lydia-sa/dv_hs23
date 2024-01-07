# IMPORT LIBRARIES
#-------------------------------------------------------------------
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px

# FUNKTIONEN
#-------------------------------------------------------------------
color_map={
    'Wärmedämmung': '#734A38',
    'Haustechnik': '#EC4D06',
    'Systemsanierung': '#AFB23B',
    'Neubau': '#F28C6A',
    'Zentrale Wärmeversorgung': '#84C0B9',
    'Indirekte Massnahmen': '#738284'
}

def stacked_bar_chart(kanton_kurzname='CH'):
    df_auszahlungen_grafik = df_auszahlungen[df_auszahlungen['Massnahmenbereich'] != 'Total']
    df_auszahlungen_grafik = df_auszahlungen_grafik[df_auszahlungen_grafik['Kanton_Kurzname'] == kanton_kurzname]

    df_gesuche_grafik = df_gesuche[df_gesuche['Kanton_Kurzname'] == kanton_kurzname]

    # Subplot erstellen
    fig = make_subplots(specs=[[{'secondary_y':True}]])

    # Balkendiagramm hinzufügen
    bar_fig = px.bar(df_auszahlungen_grafik,
                     x='Date',
                     y='VergütungCHF_Gebäudeprogramm',
                     color='Massnahmenbereich',
                     color_discrete_map=color_map
                     )

    fig.add_trace(bar_fig.data[3])
    fig.add_trace(bar_fig.data[0])
    fig.add_trace(bar_fig.data[2])
    fig.add_trace(bar_fig.data[1])
    fig.add_trace(bar_fig.data[4])
    fig.add_trace(bar_fig.data[5])
    fig.update_layout(barmode='stack')

    fig.add_trace(
        go.Scatter(x=df_gesuche_grafik['Date'],
                   y=df_gesuche_grafik['Anzahl_Gesuche_mit_Auszahlung'],
                   mode='markers',
                   marker=dict(color='black', size=12),
                   name='Anzahl Gesuche mit Auszahlung',
                   showlegend=True),
        secondary_y=True)

    # Achsenbeschreibung
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', title=None)
    fig.update_yaxes(showline=False, linewidth=1, linecolor='black', title='Auszahlungen (in CHF)')
    fig.update_yaxes(showline=False, linewidth=1, linecolor='black', title='', secondary_y= True)

    # Legende innerhalb des Graphen
    fig.update_layout(plot_bgcolor='white',
                      paper_bgcolor='white',
                      yaxis=dict(showgrid=True, gridcolor='#d9dbda', gridwidth=0.5, griddash='dot'),
)


    return fig


def pie_CO2(jahr):
    df_CO2_year = df_CO2[df_CO2['Date'] == jahr]
    df_CO2_grafik = df_CO2_year[df_CO2_year['Massnahmenbereich'] != 'Total CO2-Wirkung Gebäudeprogramm']

    fig = px.pie(df_CO2_grafik,
           names='Massnahmenbereich',
           values='CO2_Wirkung_Tonnen_CH',
           color='Massnahmenbereich',
           color_discrete_map=color_map,
           hole=0.9,
           #title= f'CO2 Wirkung {jahr} - Schweiz Total'
           )
    # Füge Annotation für den Gesamtwert in der Mitte hinzu
    fig.update_layout(annotations=[dict(
        text=f"{round(df_CO2_year[df_CO2_year['Massnahmenbereich'] == 'Total CO2-Wirkung Gebäudeprogramm']['CO2_Wirkung_Tonnen_CH'].iloc[0]/1e6,2)} Mio.Tonnen",
        x=0.5, y=0.5,
        font_size=12,
        showarrow=False)])

    # Aktualisiere die Beschriftungen (labels) im Diagramm
    fig.update_traces(textinfo='none')

    # Deaktiviere die Legende
    fig.update_layout(showlegend=False)

    return fig

def pie_Energiewirkung(jahr):
    df_Energiewirkung_year = df_Energiewirkung[df_Energiewirkung['Date'] == jahr]
    df_Energiewirkung_grafik = df_Energiewirkung_year[df_Energiewirkung_year['Massnahmenbereich'] != 'Total Energiewirkung Gebäudeprogramm']

    fig = px.pie(df_Energiewirkung_grafik,
           names='Massnahmenbereich',
           values='Energiewirkung_GWh_CH',
           color='Massnahmenbereich',
           color_discrete_map=color_map,
           hole=0.9,
           #title= f'Energiewirkung {jahr} - Schweiz Total'
           )
    # Füge Annotation für den Gesamtwert in der Mitte hinzu
    fig.update_layout(annotations=[dict(
        text=f"{df_Energiewirkung_year[df_Energiewirkung_year['Massnahmenbereich'] == 'Total Energiewirkung Gebäudeprogramm']['Energiewirkung_GWh_CH'].iloc[0]} GWh",
        x=0.5, y=0.5,
        font_size=12,
        showarrow=False)])

    # Aktualisiere die Beschriftungen (labels) im Diagramm
    fig.update_traces(textinfo='none')

    # Deaktiviere die Legende
    fig.update_layout(showlegend=False)

    return fig

def gb_angebot_list(kanton_kurznamen):

    kanton_filtered_df = df_gebaudeprogramm_angebot[df_gebaudeprogramm_angebot['Kanton_Kurzname'] == kanton_kurznamen]

    # Linkliste erstellen
    gb_angebot_list_items = [
        html.Li(
            dcc.Link(name, href=link, target='_blank'),
            style={'margin-bottom': '10px'}
        )
        for name, link in zip(kanton_filtered_df['Name'], kanton_filtered_df['Link'])
    ]

    return html.Ul(gb_angebot_list_items)


# IMPORT DATA
#-------------------------------------------------------------------
df_grundlagen = pd.read_csv('grundlagen_gemeinde_kantone.csv')
df_auszahlungen = pd.read_csv('gebaudeprogramm_SummeAuszahlungen.csv', sep=';')
df_gesuche = pd.read_csv('gebaudeprogramm_AnzahlGesuche.csv')
df_CO2 = pd.read_csv('gebaudeprogramm_CO2Wirkung.csv', sep=';')
df_Energiewirkung = pd.read_csv('gebaudeprogramm_Energiewirkung.csv', sep=';')
df_gebaudeprogramm_angebot = pd.read_csv('gebaudeprogramm_angebote.csv')

# CLEAN DATA
#-------------------------------------------------------------------
# Cleaning
kanton_dict_gb_angebot = {
    'zuerich': 'ZH',
    'bern': 'BE',
    'luzern': 'LU',
    'uri': 'UR',
    'schwyz': 'SZ',
    'obwalden': 'OW',
    'nidwalden': 'NW',
    'glarus': 'GL',
    'zug': 'ZG',
    'freiburg': 'FR',
    'solothurn': 'SO',
    'basel-stadt': 'BS',
    'basel-landschaft': 'BL',
    'schaffhausen': 'SH',
    'appenzell-ausserrhoden': 'AR',
    'appenzell-innerrhoden': 'AI',
    'st-gallen': 'SG',
    'graubuenden': 'GR',
    'aargau': 'AG',
    'thurgau': 'TG',
    'ticino': 'TI',
    'vaud': 'VD',
    'wallis': 'VS',
    'neuchatel': 'NE',
    'geneve': 'GE',
    'jura': 'JU'
}

df_gebaudeprogramm_angebot['Kanton_Kurzname'] = df_gebaudeprogramm_angebot['Kanton'].replace(kanton_dict_gb_angebot.keys() , kanton_dict_gb_angebot.values() , regex=True)

# Funktion zum Hinzufügen von "https://www.dasgebaeudeprogramm.ch" voran
def prepend_url(link):
    if link.startswith("/de/"):
        return "https://www.dasgebaeudeprogramm.ch" + link
    return link

# Wende die Funktion auf die 'Link'-Spalte an
df_gebaudeprogramm_angebot['Link'] = df_gebaudeprogramm_angebot['Link'].apply(prepend_url)



# START APP
#-------------------------------------------------------------------

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# LAYOUT
#--------------------------------------------------------------------

app.layout = html.Div([
    dbc.Container([
    dbc.Row([
            dbc.Col([
                dcc.Dropdown(id='dropdown_kanton',
                             options=sorted([{'label': i, 'value': i} for i in df_grundlagen['Kanton_Name'].unique()], key = lambda x: x['label']),
                             placeholder='wähle einen Kanton',
                             style= {'width':'40%'}
                             ),

                dcc.Graph(id='stable_diagram', figure={}),
            ], width={'size': 5}),

            dbc.Col([
                html.H6('Einsparungen in der ganzen Schweiz 2023',style={'text-align': 'center', 'font-size': '14px', }),
                html.H6('CO2',style={'text-align': 'center', 'font-size': '14px', }),
                dcc.Graph(id='pie_chart1', figure=pie_CO2(2023)),
                html.H6('Energie',style={'text-align': 'center', 'font-size': '14px', }),
                dcc.Graph(id='pie_chart2', figure=pie_Energiewirkung(2023)),
            ], width={'size': 5},),
        ]),

    html.Div(id='gb_angebot_list'),

    dcc.Dropdown(id='dropdown_gemeinde',
                 options=sorted([{'label': i, 'value': i} for i in df_grundlagen['PLZ'].dropna().astype(int).unique()], key = lambda x: x['label']),
                 placeholder='wähle eine PLZ',
                 style= {'width':'40%'}
                 ),
    html.Div(id='output_container_gemeinde'),
])
])

# CALLBACK FUNCTION
#--------------------------------------------------------------------
@app.callback(
    Output('stable_diagram', 'figure'),
    Input('dropdown_kanton', 'value')
)
def update_output_Kanton(kanton):
    kanton_kurznamen = df_grundlagen.loc[df_grundlagen['Kanton_Name'] == kanton, 'Kanton_Kurzname'].iloc[0]
    return stacked_bar_chart(kanton_kurznamen)

@app.callback(
    Output('gb_angebot_list', 'children'),
    Input('dropdown_kanton', 'value')
)
def update_gb_angebot_list(kanton):
    kanton_kurznamen = df_grundlagen.loc[df_grundlagen['Kanton_Name'] == kanton, 'Kanton_Kurzname'].iloc[0]
    return gb_angebot_list(kanton_kurznamen)


@app.callback(
    Output('dropdown_gemeinde', 'options'),
    Input('dropdown_kanton', 'value')
)
def update_gmeinde_options(kanton):
    filtered_data = df_grundlagen[df_grundlagen['Kanton_Name'] == kanton]
    options = sorted([{'label': i, 'value': i} for i in filtered_data['PLZ'].dropna().astype(int).unique()], key=lambda x: x['label'])

    return options


@app.callback(
    Output('output_container_gemeinde', 'children'),
    Input('dropdown_gemeinde', 'value')
)
def update_output_Gemeinde(plz):
    gemeinde_name = df_grundlagen.loc[df_grundlagen['PLZ'] == int(plz), 'Gemeinde_Name'].iloc[0]
    return gemeinde_name






# RUN THE APP
#--------------------------------------------------------------------
if __name__=='__main__':
    app.run_server(debug=True, port=8020)

