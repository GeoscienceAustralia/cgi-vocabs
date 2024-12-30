from pathlib import Path
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, SKOS


for f in sorted(Path(Path(__file__).parent.parent.resolve() / "vocabularies" / "geosciml").glob("**/*.ttl")):
    g = Graph()
    g.parse(f)
    for iri in g.subjects(RDF.type, SKOS.ConceptScheme):
        print(iri)

