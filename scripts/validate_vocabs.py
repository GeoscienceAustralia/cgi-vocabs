from pathlib import Path
from pyshacl import validate
import httpx


def main():
    # get the validator
    # r = httpx.get("https://w3id.org/profile/vocpub/validator") # expired SSL cert
    r = httpx.get("https://raw.githack.com/surroundaustralia/vocpub-profile/master/validator.shacl.ttl") # temporary link
    assert r.status_code == 200

    # for all vocabs...
    invalid_vocabs = []
    vocabs_dir = Path(__file__).parent.parent / "vocabularies"
    for f in vocabs_dir.iterdir():
        # ...validate each file
        if f.name.endswith(".ttl"):
            v = validate(str(f), shacl_graph=r.text, shacl_graph_format="ttl")
            if not v[0]:
                invalid_vocabs.append(f)

    # check to see if we have any invalid vocabs
    if len(invalid_vocabs) > 0:
        print("Invalid Vocabs:")
        for iv in invalid_vocabs:
            print("\t- {}".format(iv))

    assert len(invalid_vocabs) == 0, "Invalid vocabs: {}".format(", ".join([str(x) for x in invalid_vocabs]))


if __name__ == "__main__":
    main()
