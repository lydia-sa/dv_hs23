from rdflib import Graph
import pandas as pd
import ssl

#ctx = ssl.create_default_context()
#ctx.check_hostname = False
#ctx.verify_mode = ssl.CERT_NONE

ssl._create_default_https_context = ssl._create_unverified_context

#1.Abfrage: Kanton, Gemeinden und deren Einwohnerzahl
GemeindeKantone_QUERY = '''
PREFIX schema: <http://schema.org/>
PREFIX gn: <http://www.geonames.org/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?PLZ ?Gemeinde ?Name ?Population ?Cantonname ?Cantonpopul
WHERE {
        SERVICE <https://geo.ld.admin.ch/query>
            {   ?Gemeinde gn:featureCode gn:A.ADM3 .
                ?Gemeinde schema:name ?Name .
                ?Gemeinde gn:population ?Population .
                ?Gemeinde <http://purl.org/dc/terms/issued> ?Date .

                ?Gemeinde gn:parentADM1 ?Canton .
                ?Canton schema:name ?Cantonname .
                ?Canton gn:population ?Cantonpopul .

                OPTIONAL {?Gemeinde gn:postalCode ?PLZ}.

            FILTER (?Date = "2023-01-01"^^xsd:date)
                }
            }
            ORDER BY DESC(?Population)
            
        '''

# Graph erstellen und SPARQL-Abfrage durchführen
g = Graph()
results = g.query(GemeindeKantone_QUERY)

result_list = []
for row in results:
    result_list.append(row)

# Liste in ein Pandas DataFrame umwandeln
df_g = pd.DataFrame(result_list, columns=['plz', 'gemeinde', 'name', 'population', 'cantonname', 'cantonpopul'])

# DataFrame anzeigen
#print(df_g)

#----------------------------------

#2te Abfrage "Kurznamen Kanton":

KurznamenKanton_QUERY = '''
PREFIX schema: <http://schema.org/>

select  ?Canton ?Kurzname ?Cantonname
where {
        SERVICE <https://geo.ld.admin.ch/query>
            {?Canton schema:name ?Cantonname.
            ?Canton <http://schema.org/alternateName> ?Kurzname.
        
        FILTER (lang(?Cantonname) ='de' || lang(?Cantonname) ='fr' || lang(?Cantonname) ='it')
}}
'''

# Graph erstellen und SPARQL-Abfrage durchführen
g2 = Graph()
results_g2 = g2.query(KurznamenKanton_QUERY)

result_g2_list = []
for row in results_g2:
    result_g2_list.append(row)

# Liste in ein Pandas DataFrame umwandeln
df_g2 = pd.DataFrame(result_g2_list, columns=['canton', 'kurzname', 'cantonname',])

# DataFrame anzeigen
#print(df_g2)

#-----------------------------------------------
# 3te Abfrage: Anzahl Gesuche pro Jahr und Region für Förderprogramm

Gutsprachen_QUERY = '''
PREFIX schema: <http://schema.org/>

select  ?kurzname ?jahr ?anzahl ?s
where {
        SERVICE <https://lindas.admin.ch/query>
            {?s schema:eligibleRegion ?kurzname.
            ?s <https://energy.ld.admin.ch/sfoe/bfe_ogd18_gebaeudeprogramm_anzahl_gesuche/Jahr> ?jahr.
            ?s <https://energy.ld.admin.ch/sfoe/bfe_ogd18_gebaeudeprogramm_anzahl_gesuche/anzahl-gesuche-mit-auszahlungen> ?anzahl.
}}
'''

# Graph erstellen und SPARQL-Abfrage durchführen
g3 = Graph()
results_g3 = g3.query(Gutsprachen_QUERY)

result_g3_list = []
for row in results_g3:
    result_g3_list.append(row)

# Liste in ein Pandas DataFrame umwandeln
df_g3 = pd.DataFrame(result_g3_list, columns=['cantonname', 'jahr', 'anzahl', 'art' ])

# DataFrame anzeigen
print(df_g3)
