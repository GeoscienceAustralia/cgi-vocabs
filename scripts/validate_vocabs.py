from pathlib import Path
from pyshacl import validate
from rdflib import Graph

WARNINGS_INVALID = False # Allows warnings to flag as invalid when true
SHOW_WARNINGS = True
THIS_FILE = Path(__file__).resolve()
ITEMS_DIR = THIS_FILE.parent.parent / "vocabularies"

SHACL_GRAPH = Graph().parse("vocpub-4.10.ttl")

CONTEXT_GRAPH = Graph().parse(THIS_FILE.parent.parent / "_background" / "agents.ttl")

def main():
    # for all vocabs...
    warning_vocabs = {} # format {vocab_filename: warning_msg}
    invalid_vocabs = {} # format {vocab_filename: error_msg}
    for f in ITEMS_DIR.glob("**/*.ttl"):
        # ...validate each file
        try:
            DATA_GRAPH = Graph().parse(f) + CONTEXT_GRAPH
            v = validate(DATA_GRAPH, shacl_graph=SHACL_GRAPH, allow_warnings=True)
            if not v[0]:
                if "Severity: sh:Violation" in v[2]:
                    invalid_vocabs[f.name] = v[2]
                elif "Severity: sh:Warning" in v[2]:
                    warning_vocabs[f.name] = v[2]

        # syntax errors crash the validate() function
        except Exception as e:
            invalid_vocabs[f.name] = e

    # check to see if we have any invalid vocabs
    if len(warning_vocabs.keys()) > 0 and SHOW_WARNINGS:
        print("Warning Vocabs:\n")
        for vocab, warning in warning_vocabs.items():
            print(f"- {vocab}:")
            print(warning)
            print("-----")

    # check to see if we have any invalid vocabs
    if len(invalid_vocabs.keys()) > 0:
        print("Invalid Vocabs:\n")
        for vocab, error in invalid_vocabs.items():
            print(f"- {vocab}:")
            print(error)
            print("-----")

    if WARNINGS_INVALID:
        assert len(warning_vocabs.keys()) == 0, "Warning vocabs: {}".format(", ".join([str(x) for x in warning_vocabs.keys()]))
    assert len(invalid_vocabs.keys()) == 0, "Invalid vocabs: {}".format(", ".join([str(x) for x in invalid_vocabs.keys()]))


if __name__ == "__main__":
    main()
