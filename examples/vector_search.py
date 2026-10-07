"""Voyage query embedding + Atlas Vector Search against stored summaries.
Run: python examples/vector_search.py "What approval do I need before my scan?"
"""
import sys
from config import VECTOR_INDEX, CANDIDATE_LIMIT, VOYAGE_MODEL, EMBEDDING_DIMENSIONS
from atlas_connection import collection
from create_indexes import require_indexes
from embed_summary import embed
def vector_search(query):
    vector = embed(query, 'query')
    return list(collection().aggregate([{'$vectorSearch': {'index': VECTOR_INDEX, 'path': 'embedding', 'queryVector': vector, 'numCandidates': CANDIDATE_LIMIT * 20, 'limit': CANDIDATE_LIMIT, 'filter': {'$and': [{'embedding_model': {'$eq': VOYAGE_MODEL}}, {'embedding_dimensions': {'$eq': EMBEDDING_DIMENSIONS}}]}}}, {'$set': {'retrieval_score': {'$meta': 'vectorSearchScore'}}}, {'$project': {'embedding': 0, 'transcript': 0}}], maxTimeMS=60000))

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]).strip() or "What approval do I need before my scan?"
    require_indexes([VECTOR_INDEX])
    for hit in vector_search(query)[:5]:
        print(f"\n{hit['title']} | vector score: {hit['retrieval_score']:.4f}")
        print(hit['summary'])
