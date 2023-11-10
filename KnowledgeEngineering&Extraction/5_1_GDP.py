# import data from csv.gz
import pandas as pd

# import data
file = 'data/vertiefungsbeispiel-gdp.csv.gz'

# renaming columns with predicate name
column_names = ['default:rank', 'country', 'default:imfGDP', 'default:unGDP', 'default:gdpPerCapita', 'dpo:populationTotal']

# read csv
df = pd.read_csv(file, compression='gzip', names=column_names, skiprows=1)

from rdflib import Namespace, Graph, Literal
from rdflib.collection import Collection
from rdflib import FOAF, DC

# namespaces
DPO = Namespace('https://dbpedia.org/')
default = Namespace('http://moodle.fhgr.ch/mod/resource/view.php/')


g = Graph()
for idx, (rank, country, imfGDP, unGDP, gdpPerCapita, populationTotal) in df.iterrows():
    country = country.replace(' ', '_')
    g.add((getattr(default, country), default.rank, Literal(rank)))
    g.add((getattr(default, country), default.imfGDP, Literal(imfGDP)))
    g.add((getattr(default, country), default.unGDP, Literal(unGDP)))
    g.add((getattr(default, country), default.gdpPerCapita, Literal(gdpPerCapita)))
    g.add((getattr(default, country), DPO.populationTotal, Literal(populationTotal)))
    print(((getattr(default, country), default.rank, Literal(rank))))

print([x for x in g.triples((None, None, None))])