"""Voyage-only example: embed summary text without calling OpenAI or MongoDB.
Run: python examples/embed_summary.py [summary.txt]
"""
import math
import sys
from pathlib import Path
import voyageai
from config import VOYAGE_API_KEY, VOYAGE_MODEL, EMBEDDING_DIMENSIONS, require_settings
def voyage_client(key):
    return voyageai.Client(api_key=key, timeout=60, max_retries=2)

def embed(text, input_type):
    require_settings('VOYAGE_API_KEY')
    vector = voyage_client(VOYAGE_API_KEY).embed(texts=[text], model=VOYAGE_MODEL, input_type=input_type, output_dimension=EMBEDDING_DIMENSIONS, output_dtype='float', truncation=False).embeddings[0]
    if len(vector) != EMBEDDING_DIMENSIONS or not all((math.isfinite(x) for x in vector)):
        raise ValueError('Voyage returned an invalid embedding dimension or value.')
    return vector

if __name__ == "__main__":
    text = Path(sys.argv[1]).read_text() if len(sys.argv) > 1 else (
        "The agent explained that the knee MRI requires prior authorization. "
        "The estimated patient cost is $560 if the allowed amount is $1,200."
    )
    vector = embed(text, "document")
    print(f"Model: {VOYAGE_MODEL}; dimensions: {len(vector)}")
    print(f"First eight values: {vector[:8]}")
