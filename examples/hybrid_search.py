"""Atlas keyword + vector retrieval, combined using Python reciprocal rank fusion.
Matches the existing demo. This is rank fusion, not Voyage reranking.
Run: python examples/hybrid_search.py "therapy visits and referral requirements"
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from config import TEXT_INDEX, VECTOR_INDEX, RRF_K
from create_indexes import require_indexes
from keyword_search import keyword_search
from vector_search import vector_search
def reciprocal_rank_fusion(keyword_hits, semantic_hits, semantic_weight=0.5):
    """Fuse ranks, never add incomparable raw keyword and vector scores."""
    fused = {}
    for label, hits, weight in (('keyword', keyword_hits, 1 - semantic_weight), ('semantic', semantic_hits, semantic_weight)):
        if weight <= 0:
            continue
        for rank, hit in enumerate(hits, 1):
            key = hit['_id']
            if key not in fused:
                fused[key] = {**hit, 'rrf_score': 0.0, 'keyword_rank': None, 'semantic_rank': None, 'keyword_score': None, 'semantic_score': None}
            fused[key]['rrf_score'] += weight / (RRF_K + rank)
            fused[key][f'{label}_rank'] = rank
            fused[key][f'{label}_score'] = hit['retrieval_score']
    return sorted(fused.values(), key=lambda d: (-d['rrf_score'], str(d['_id'])))

def search(query, mode, limit, semantic_weight):
    query = query.strip()
    if not query:
        raise ValueError('Enter a search query.')
    names = [TEXT_INDEX] if mode == 'Keyword' else [VECTOR_INDEX]
    if mode == 'Hybrid':
        names = [TEXT_INDEX, VECTOR_INDEX]
    require_indexes(names)
    if mode == 'Keyword':
        return keyword_search(query)[:limit]
    if mode == 'Semantic':
        return vector_search(query)[:limit]
    with ThreadPoolExecutor(max_workers=2) as pool:
        text_future = pool.submit(keyword_search, query)
        vector_future = pool.submit(vector_search, query)
        return reciprocal_rank_fusion(text_future.result(), vector_future.result(), semantic_weight)[:limit]

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]).strip() or "therapy visits and referral requirements"
    for hit in search(query, "Hybrid", limit=5, semantic_weight=0.5):
        print(f"\n{hit['title']} | RRF score: {hit['rrf_score']:.6f}")
        print(f"Keyword rank: {hit['keyword_rank']} | Semantic rank: {hit['semantic_rank']}")
        print(hit['summary'])
