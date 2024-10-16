from pathlib import Path
from rdflib import Graph

THIS_FILE = Path(__file__).resolve()
ITEMS_DIR = THIS_FILE.parent.parent / "vocabularies"

all_ttl_files = Path(ITEMS_DIR).glob("*.ttl")

for f in ITEMS_DIR.glob("**/*.ttl"):
    print(f"Tidying {f}")
    g = Graph().parse(f)
    open(f, "w").write(g.serialize(format="longturtle"))

print("done")
