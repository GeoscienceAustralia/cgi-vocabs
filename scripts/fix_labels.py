from pathlib import Path
from pyshacl import validate
from rdflib import Graph
from rdflib.namespace import SKOS
from rdflib import Literal


THIS_FILE = Path(__file__).resolve()
ITEMS_DIR = THIS_FILE.parent.parent / "vocabularies"

for f in ITEMS_DIR.glob("**/*.ttl"):
    print()
    print(f)
    g = Graph().parse(f)
    last_c = None
    for c, pl in g.subject_objects(SKOS.prefLabel):
        if not c == last_c:
            print(c)
        if pl.language == "en":
            print(f"PL {pl}")
        else:
            print(f"AL {pl}")
            g.remove((c, SKOS.prefLabel, pl))
            g.add((c, SKOS.altLabel, pl))
        last_c = c

    g.serialize(destination=f, format="longturtle")
