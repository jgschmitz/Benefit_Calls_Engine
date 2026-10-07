"""Atlas keyword retrieval against summary-derived search_text. No AI API calls.
Run: python examples/keyword_search.py "prior authorization"
"""
import sys
from config import TEXT_INDEX, CANDIDATE_LIMIT
from atlas_connection import collection
from create_indexes import require_indexes
def keyword_search(query):
    return list(collection().aggregate([{'$search': {'index': TEXT_INDEX, 'text': {'query': query, 'path': 'search_text'}}}, {'$limit': CANDIDATE_LIMIT}, {'$set': {'retrieval_score': {'$meta': 'searchScore'}}}, {'$project': {'embedding': 0, 'transcript': 0}}], maxTimeMS=60000))

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]).strip() or "prior authorization"
    require_indexes([TEXT_INDEX])
    for hit in keyword_search(query)[:5]:
        print(f"\n{hit['title']} | search score: {hit['retrieval_score']:.4f}")
        print(hit['summary'])
