from pathlib import Path
from pyshacl import validate
import httpx


def main():
    # get the validator
    r = httpx.get("https://w3id.org/profile/vocpub/validator")
    assert r.status_code == 200

    # for all vocabs...
    invalid_vocabs = {} # format {vocab_filename: error_msg}
    vocabs_dir = Path(__file__).parent.parent / "vocabularies"
    for f in vocabs_dir.iterdir():
        # ...validate each file
        if f.name.endswith(".ttl"):
            try:
                v = validate(str(f), shacl_graph=r.text, shacl_graph_format="ttl")
                if not v[0]:
                    invalid_vocabs[f.name] = v[2]
            # syntax errors crash the validate() function
            except Exception as e:
                invalid_vocabs[f.name] = e

    # check to see if we have any invalid vocabs
    if len(invalid_vocabs.keys()) > 0:
        print("Invalid Vocabs:\n")
        for vocab, error in invalid_vocabs.items():
            print(f"- {vocab}:")
            print(error)
            print("-----")

    assert len(invalid_vocabs.keys()) == 0, "Invalid vocabs: {}".format(", ".join([str(x) for x in invalid_vocabs.keys()]))


if __name__ == "__main__":
    main()
