from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS, XSD
from hashlib import sha1


def calculate_id(iri: URIRef, existing_container_iris: list[Literal]) -> Literal:
    # try to use ID part of IR
    iri_str = str(iri)
    candidate_id = iri_str.split("/")[-1].split("#")[-1]

    # unique check
    if candidate_id not in [x.value for x in existing_container_iris]:
        id = candidate_id
    else:
        # not unique ID so create a hash from the IRI
        id = sha1(iri_str.encode()).hexdigest()

    return Literal(id, datatype=XSD.token)


g = Graph().parse("../vocabularies/earthresourceml/CommodityCode.ttl")

existing_ids = []
existing_ids.append(Literal("industrial-mineral", datatype=XSD.token))

for s in g.subjects(RDF.type, SKOS.Concept):
    has_id = False
    for o in g.objects(s, DCTERMS):
        has_id = True
    if not has_id:
        id = calculate_id(s, existing_ids)
        existing_ids.append(id)
        g.add((s, DCTERMS.identifier, id))

g.serialize(destination="CommodityCode.ids.ttl", format="longturtle")
