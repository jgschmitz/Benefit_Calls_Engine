"""Create only missing Atlas Search and Vector Search indexes.
Run: python examples/create_indexes.py
Status only: python examples/create_indexes.py --status
Existing definitions are never replaced. Builds are asynchronous.
"""
import argparse
from pymongo.errors import CollectionInvalid
from pymongo.operations import SearchIndexModel
from config import COLLECTION_NAME, TEXT_INDEX, VECTOR_INDEX, EMBEDDING_DIMENSIONS
from atlas_connection import collection
TEXT_DEFINITION = {'mappings': {'dynamic': False, 'fields': {'search_text': {'type': 'string', 'analyzer': 'lucene.standard'}}}}

VECTOR_DEFINITION = {'fields': [{'type': 'vector', 'path': 'embedding', 'numDimensions': EMBEDDING_DIMENSIONS, 'similarity': 'cosine'}, {'type': 'filter', 'path': 'embedding_model'}, {'type': 'filter', 'path': 'embedding_dimensions'}]}

def index_status():
    return {item['name']: item for item in collection().list_search_indexes()}

def create_missing_indexes():
    coll = collection()
    try:
        coll.database.create_collection(COLLECTION_NAME)
    except CollectionInvalid:
        pass
    existing = index_status()
    created = []
    for name, kind, definition in ((TEXT_INDEX, 'search', TEXT_DEFINITION), (VECTOR_INDEX, 'vectorSearch', VECTOR_DEFINITION)):
        if name not in existing:
            coll.create_search_index(SearchIndexModel(name=name, type=kind, definition=definition))
            created.append(name)
    return created

def require_indexes(names):
    indexes = index_status()
    for name in names:
        item = indexes.get(name)
        if not item or not item.get('queryable'):
            status = item.get('status', 'not created') if item else 'not created'
            raise RuntimeError(f'Index {name} is {status}. Run create_indexes.py --status until queryable.')
        if name == VECTOR_INDEX:
            fields = item.get('latestDefinition', {}).get('fields', [])
            vectors = [f for f in fields if f.get('type') == 'vector' and f.get('path') == 'embedding']
            if fields and (not vectors or vectors[0].get('numDimensions') != EMBEDDING_DIMENSIONS):
                raise RuntimeError('Existing vector index has different dimensions. Match its definition in Atlas to create_indexes.py.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    if not args.status:
        print("Created:", create_missing_indexes() or "No missing indexes")
    for name, info in index_status().items():
        print(f"{name}: {info.get('status')} | queryable={info.get('queryable', False)}")
