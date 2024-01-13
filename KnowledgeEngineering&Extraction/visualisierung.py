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
    fig.update_layout(showlegend=False,
                      margin=dict(l=55, r=55, t=0, b=30),
                      height=200,)

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
    fig.update_layout(showlegend=False,
                      margin=dict(l=55, r=55, t=0, b=30),
                      height=200,)

    return fig


def gb_angebot_list(kanton_kurznamen):

    kanton_filtered_df = df_gebaudeprogramm_angebot[df_gebaudeprogramm_angebot['Kanton_Kurzname'] == kanton_kurznamen]


    gb_angebot_list_items = [
        # Liste erstellen - Aufzählungszeichen einfügen
        html.Li(
            # Link unter Namen
            dcc.Link(name, href=link, target='_blank'),
            style={'margin-bottom': '10px'}
        )
        for name, link in zip(kanton_filtered_df['Name'], kanton_filtered_df['Link'])
    ]

    return html.Ul(gb_angebot_list_items)


def update_energie_list(selected_gemeinde):
    # DataFrame filtern
    filtered_df = df_energie[df_energie['Gemeinde'] == selected_gemeinde]

    # Angebote in Kategorien zusammenfassen
    current_category = ''

    list_items = []
    for _, row in filtered_df.iterrows():
        # Überprüfen, ob sich die Kategorie ändert
        if row['category'] != current_category:
            # Kategorie als Überschrift hinzufügen
            list_items.append(html.Strong(f"Kategorie: {row['category']}",style={'margin-left': '-20px', 'margin-top': '15px', 'display': 'block'}))
            current_category = row['category']

        # Informationen für Anbieter und Name hinzu (inkl. Weblink)
        list_items.append(html.Li([
            html.Span(f"{row['Anbieter']}: "),
            dcc.Link(row['Programm_Name'], href=row['Website'], target='_blank')
        ]))

    return list_items


# IMPORT DATA
#-------------------------------------------------------------------
df_grundlagen = pd.read_csv('data/grundlagen_gemeinde_kantone.csv')
df_auszahlungen = pd.read_csv('data/gebaudeprogramm_SummeAuszahlungen.csv', sep=';')
df_gesuche = pd.read_csv('data/gebaudeprogramm_AnzahlGesuche.csv')
df_CO2 = pd.read_csv('data/gebaudeprogramm_CO2Wirkung.csv', sep=';')
df_Energiewirkung = pd.read_csv('data/gebaudeprogramm_Energiewirkung.csv', sep=';')
df_gebaudeprogramm_angebot = pd.read_csv('data/gebaudeprogramm_angebote.csv')
df_energie = pd.read_csv('data/energiefranken_angebote.csv')

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

# Kanton_Kurzname in die Liste der Gebeäudeprogramm-Angebote integrieren und bei allen Links auf die Gebäudeprogramm-Seite "https://www.dasgebaeudeprogramm.ch" vorne hinzufügen
df_gebaudeprogramm_angebot['Kanton_Kurzname'] = df_gebaudeprogramm_angebot['Kanton'].replace(kanton_dict_gb_angebot.keys() , kanton_dict_gb_angebot.values() , regex=True)

# Funktion zum Hinzufügen von "https://www.dasgebaeudeprogramm.ch" voran
def prepend_url(link):
    if link.startswith("/de/"):
        return "https://www.dasgebaeudeprogramm.ch" + link
    return link

# Wende die Funktion auf die 'Link'-Spalte an
df_gebaudeprogramm_angebot['Link'] = df_gebaudeprogramm_angebot['Link'].apply(prepend_url)

# Energiefranken: Programme von Kantonen löschen (bereits in der Liste von Gebäudeprogramm enthalten)
df_energie = df_energie[~df_energie['Anbieter'].str.startswith('Kanton')]

# START APP
#-------------------------------------------------------------------

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
server = app.server

# LAYOUT
#--------------------------------------------------------------------

app.layout = html.Div([
    dbc.Container([
    html.H3('Schweizer Förderprogramme', style={'font-family': 'Arial', 'font-size': '34px', 'font-weight': 'bold', 'color': '#006276'}),
    html.H3('das Gebäudeprogramm', style={'font-family': 'Arial', 'font-size': '20px', 'font-weight': 'bold', 'color': '#006276'}),

    dbc.Row([
            dbc.Col([
                dcc.Dropdown(id='dropdown_kanton',
                             options=sorted([{'label': i, 'value': i} for i in df_grundlagen['Kanton_Name'].unique()], key = lambda x: x['label']),
                             #placeholder='wähle einen Kanton',
                             value= 'Graubünden',
                             style= {'width':'100%'}
                             ),

                dcc.Graph(id='stable_diagram', figure={}),
            ], width={'size': 9}),

            dbc.Col([

                html.H6('Einsparungen in der ganzen Schweiz 2023',style={'text-align': 'center', 'font-size': '16px', }),
                html.H6('CO2',style={'text-align': 'center', 'font-size': '14px', }),
                dcc.Graph(id='pie_chart1', figure=pie_CO2(2023)),
                html.H6('Energie',style={'text-align': 'center', 'font-size': '14px', }),
                dcc.Graph(id='pie_chart2', figure=pie_Energiewirkung(2023)),
            ], width={'size': 3},),
        ]),

    html.Div(id='gb_angebot_list'),
    html.H3('weitere Programme', style={'margin-top': '30px', 'font-family': 'Arial', 'font-size': '20px', 'font-weight': 'bold', 'color': '#006276'}),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='dropdown_gemeinde',
                         options=sorted([{'label': i, 'value': i} for i in df_grundlagen['PLZ'].dropna().astype(int).unique()], key = lambda x: x['label']),
                         placeholder='wähle eine PLZ',
                         style= {'width':'100%'}
                         )], width={'size': 2}),
        dbc.Col([
            html.Div(id='output_container_gemeinde')], width={'size': 9}),
        ]),
    html.Ul(id='energie_angebot_list')
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

@app.callback(
    Output('energie_angebot_list', 'children'),
    Input('dropdown_gemeinde', 'value')
)
def update_energie_angebot_list(plz):
    return update_energie_list(plz)


# RUN THE APP
#--------------------------------------------------------------------
if __name__=='__main__':
    app.run_server(debug=False, port=8070)

