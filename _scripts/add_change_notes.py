from pathlib import Path
from rdflib import Graph
from rdflib.namespace import RDF, SKOS
from rdflib import Literal


THIS_FILE = Path(__file__).resolve()
ITEMS_DIR = THIS_FILE.parent.parent / "vocabularies"

for f in ITEMS_DIR.glob("**/*.ttl"):
    print()
    print(f)
    g = Graph().parse(f)
    for cs in g.subjects(RDF.type, SKOS.ConceptScheme):
        print(cs)
        g.add((cs, SKOS.changeNote, Literal("2024-10-16 NJC: update to Vbe ocPub 4.10 valid.", lang="en")))

    g.serialize(destination=f, format="longturtle")
