from typing import List
import json
import os
import time
import argparse
from pathlib import Path
import httpx
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, SKOS


MAX_RETRIES = 3

DB_TYPE = "graphdb"  # options: "fuseki" | "graphdb"
# BASE_DB_URI = "http://fuseki.surroundaustralia.com/cgi-vocabs"
BASE_DB_URI = "http://localhost:7200/repositories/cgi-vocabs"
# WEBSITE_URL = "http://cgi.surroundaustralia.com"
WEBSITE_URL = "https://cgi.vocabs.ga.gov.au"

DB_USERNAME = os.environ.get("DB_USERNAME", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")


def add_vocabs(vocabs: List[Path], mappings: dict):
    # add new vocabs
    for vocab in vocabs:
        params = {}
        endpoint = ""
        if DB_TYPE == "fuseki":
            params = {"graph": str(mappings[vocab.name])}
            endpoint = f"{BASE_DB_URI}/data"
        elif DB_TYPE == "graphdb":
            params = {"context": f"<{str(mappings[vocab.name])}>"}
            endpoint = f"{BASE_DB_URI}/statements"
        else:  # unsupported db type
            raise ValueError(
                "Unsupported DB type. Supported types are: 'fuseki', 'graphdb'."
            )

        r = httpx.post(
            endpoint,
            params=params,
            headers={"Content-Type": "text/turtle"},
            content=open(vocab, "rb").read(),
            auth=(DB_USERNAME, DB_PASSWORD),
        )
        if not 200 <= r.status_code <= 300:
            print(r.content)
        assert 200 <= r.status_code <= 300, "Status code was {}".format(r.status_code)

    endpoint = ""

    if DB_TYPE == "fuseki":
        endpoint = f"{BASE_DB_URI}/update"
    elif DB_TYPE == "graphdb":
        endpoint = f"{BASE_DB_URI}/statements"
    else:  # unsupported db type
        raise ValueError(
            "Unsupported DB type. Supported types are: 'fuseki', 'graphdb'."
        )

    # re-add remaining vocabs in directory to default graph
    for f in Path(__file__).parent.parent.glob("vocabularies/**/*.ttl"):
        data = {"update": "ADD <{}> TO DEFAULT".format(str(mappings[f.name]))}
        r2 = httpx.post(endpoint, data=data, auth=(DB_USERNAME, DB_PASSWORD))
        if not 200 <= r2.status_code <= 300:
            print(r2.content)
        assert 200 <= r2.status_code <= 300, "Status code was {}".format(r2.status_code)


def remove_vocabs(vocabs: List[Path], mappings: dict):
    data = {"update": "DROP DEFAULT"}
    if DB_TYPE == "fuseki":
        endpoint = f"{BASE_DB_URI}/update"
    elif DB_TYPE == "graphdb":
        endpoint = f"{BASE_DB_URI}/statements"
    else:  # unsupported db type
        raise ValueError(
            "Unsupported DB type. Supported types are: 'fuseki', 'graphdb'."
        )

    # clear default graph
    r = httpx.post(endpoint, data=data, auth=(DB_USERNAME, DB_PASSWORD))
    if not 200 <= r.status_code <= 300:
        print(r.content)
    assert 200 <= r.status_code <= 300, "Status code was {}".format(r.status_code)

    # drop deleted graphs
    for vocab in vocabs:
        data = {"update": "DROP GRAPH <{}>".format(str(mappings[vocab.name]))}
        r2 = httpx.post(endpoint, data=data, auth=(DB_USERNAME, DB_PASSWORD))
        if not 200 <= r2.status_code <= 300:
            print(r2.content)
        assert 200 <= r2.status_code <= 300, "Status code was {}".format(r2.status_code)


def get_graph_uri_for_vocab(vocab: Path) -> URIRef:
    """We can get the Graph URI for a vocab from the vocab file as we know that all VocPub-conformant vocabs
    have one and only one ConceptScheme per file and that the CGI VocPrez installation uses the ConceptScheme URI
    as the Graph URI"""
    g = Graph().parse(str(vocab), format="ttl")
    for s in g.subjects(predicate=RDF.type, object=SKOS.ConceptScheme):
        return s


def get_all_vocabs_uris(vocabs: List[Path]) -> dict:
    mappings = {}
    for vocab in vocabs:
        mappings[vocab.name] = get_graph_uri_for_vocab(vocab)

    return mappings


# def add_to_vocab_index(file_path: Path, graph_uri: URIRef):
#     i = Path(__file__).parent.parent / "vocabularies" / "index.json"
#     with open(i, "r") as f:
#         mappings = json.load(f)
#     with open(i, "w") as f:
#         mappings[str(file_path)] = str(graph_uri)
#         f.write(json.dumps(mappings))
#
#
# def remove_from_vocab_index(file_path: Path):
#     i = Path(__file__).parent.parent / "vocabularies" / "index.json"
#     with open(i, "r") as f:
#         mappings = json.load(f)
#     del mappings[str(file_path)]
#     with open(i, "w") as f:
#         f.write(json.dumps(mappings))


if __name__ == "__main__":
    # for testing, includes index.json as mapping dict
    # index = json.load(
    #     open(Path(__file__).parent.parent / "vocabularies" / "index.json", "r")
    # )
    # remove_vocabs(
    #     [
    #         Path(__file__).parent.parent / "vocabularies" / "earthresourceml" / "ClassificationMethodUsed.ttl",
    #     ],
    #     index,
    # )
    # add_vocabs(
    #     [
    #         Path(__file__).parent.parent / "vocabularies" / "earthresourceml" / "WasteStorage.ttl",
    #     ], index
    # )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--modified",
        help="Vocabs to be updated in the DB",
    )

    parser.add_argument(
        "-a",
        "--added",
        help="Vocabs to be added to the DB",
    )

    parser.add_argument(
        "-d",
        "--deleted",
        help="Vocabs to be deleted from the DB",
    )

    parser.add_argument(
        "-r",
        "--renamed",
        help="Vocabs to be renamed in the DB",
    )

    args = parser.parse_args()

    modified = []
    if args.modified:
        for f in args.modified.split(","):
            # if the file is in the vocabularies/ folder and ends with .ttl, it's a vocab file
            if f.startswith("vocabularies/") and f.endswith(".ttl"):
                modified.append(Path(f))

    added = []
    if args.added:
        for f in args.added.split(","):
            # if the file is in the vocabularies/ folder and ends with .ttl, it's a vocab file
            if f.startswith("vocabularies/") and f.endswith(".ttl"):
                p = Path(f)
                added.append(p)

    removed = []
    if args.deleted:
        for f in args.deleted.split(","):
            # if the file is in the vocabularies/ folder and ends with .ttl, it's a vocab file
            if f.startswith("vocabularies/") and f.endswith(".ttl"):
                p = Path(f)
                removed.append(p)

    renamed = []
    if args.renamed:
        for f in args.renamed.split(","):
            # if the file is in the vocabularies/ folder and ends with .ttl, it's a vocab file
            if f.startswith("vocabularies/") and f.endswith(".ttl"):
                p = Path(f)
                renamed.append(p)

    i = Path(__file__).parent.parent / "vocabularies" / "index.json"
    with open(i, "r") as f:
        mappings = json.load(f)

    # remove all removed and modified vocabs
    remove_vocabs(removed + modified + renamed, mappings)

    # add all added and modified vocabs
    add_vocabs(added + modified + renamed, mappings)

    # print for testing
    print("modified:")
    print([str(x) for x in modified])
    print("added:")
    print([str(x) for x in added])
    print("removed:")
    print([str(x) for x in removed])
    print("renamed:")
    print([str(x) for x in renamed])

    # retries if GET request fails
    retries = 0
    reason = ""
    while retries < MAX_RETRIES:
        try:
            # rebuild VocPrez' cache
            r = httpx.get(f"{WEBSITE_URL}/cache-reload")
            if r.status_code != 200:
                reason = r.content
                time.sleep(0 if retries == 0 else 2 ** retries)
                retries += 1
                continue
            break
        except:
            assert retries < MAX_RETRIES, "Request failed too many times"
            time.sleep(0 if retries == 0 else 2 ** retries)
            retries += 1
            continue
    assert r.status_code == 200, f"Error code {r.status_code}: {reason}"
