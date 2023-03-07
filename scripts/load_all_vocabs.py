import os
import glob
from pathlib import Path
import json
import httpx

BASE_DB_URI = os.environ.get("BASE_DB_URI", None)
ENDPOINT = f"{BASE_DB_URI}/statements"
DB_USERNAME = os.environ.get("DB_USERNAME", None)
DB_PASSWORD = os.environ.get("DB_PASSWORD", None)

# get a list of relative pathname strings of all the turtle files in the vocabularies folder
voc_strings = glob.glob(str(Path(__file__).parent.parent / "vocabularies") + "/*/*.ttl")
print(voc_strings)

# build a list of Path objects using the pathname strings
voc_paths = []
for voc in voc_strings:
    voc_path = Path(voc)
    voc_paths.append(voc_path)

# get the index.json file as a Path object
index_file = Path(__file__).parent.parent / "vocabularies" / "index.json"

# open the index.json file and read the contents out into a dict
with open(index_file, "r") as f:
    uri_mappings = json.load(f)

# load the vocabs to their respective named graphs
for vocab in voc_paths:
    # set the 'context' parameter to the uri of the concept scheme of the vocab
    params = {"context": f"<{str(uri_mappings[vocab.name])}>"}

    # make a post request to the graphDB API to add the contents of the vocab to a named graph
    r = httpx.post(
        ENDPOINT,
        params=params,
        headers={"Content-Type": "text/turtle"},
        content=open(vocab, "rb").read(),
        auth=(DB_USERNAME, DB_PASSWORD),
    )

    # if the http response code is not a successful response print the content of the response and halt the program
    # with an assertion error containing the response code
    if not 200 <= r.status_code <= 300:
        print(r.content)
    assert 200 <= r.status_code <= 300, "Status code was {}".format(r.status_code)

# load the vocabs to the default graph
for vocab in voc_paths:
    # set the payload to update the default graph with the vocab
    data = {"update": "ADD <{}> TO DEFAULT".format(str(uri_mappings[vocab.name]))}

    # make a post request to the graphDB API to add the contents of the vocab to the default graph
    r2 = httpx.post(ENDPOINT, data=data, auth=(DB_USERNAME, DB_PASSWORD))

    # if the http response code is not a successful response print the content of the response and halt the program
    # with an assertion error containing the response code
    if not 200 <= r2.status_code <= 300:
        print(r2.content)
    assert 200 <= r2.status_code <= 300, "Status code was {}".format(r2.status_code)