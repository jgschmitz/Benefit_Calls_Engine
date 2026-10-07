"""End-to-end CLI ingestion: OpenAI summary -> Voyage embedding -> Atlas upsert.
Run: python examples/store_call.py [transcript.txt] [--force]
With no file, stores both fictional samples. Existing matching calls are skipped.
"""
import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from config import SUMMARY_VERSION, OPENAI_MODEL, VOYAGE_MODEL, EMBEDDING_DIMENSIONS, require_settings
from atlas_connection import collection
from summarize_call import summarize, summary_text, print_summary_delta
from embed_summary import embed
from sample_calls import SAMPLE_CALLS
def ingest(transcript, source, force=False, progress=None):
    progress = progress or (lambda stage, data=None: None)
    transcript = transcript.strip()
    if not transcript:
        raise ValueError('Paste a transcript first.')
    require_settings('MONGO_URI', 'OPENAI_API_KEY', 'VOYAGE_API_KEY')
    coll = collection()
    call_id = hashlib.sha256(transcript.encode('utf-8')).hexdigest()
    signature = f'{SUMMARY_VERSION}|{OPENAI_MODEL}|{VOYAGE_MODEL}|{EMBEDDING_DIMENSIONS}'
    existing = coll.find_one({'_id': call_id, 'pipeline_signature': signature}, {'embedding': 0})
    if existing and (not force):
        progress('cached', existing)
        return (existing, 'Already stored; no API calls needed.')
    progress('summarizing')
    result = summarize(transcript, progress)
    progress('summary_ready', result.model_dump())
    text = summary_text(result)
    progress('embedding')
    vector = embed(text, 'document')
    progress('embedded', len(vector))
    now = datetime.now(timezone.utc)
    document = {**result.model_dump(), 'transcript': transcript, 'source': source, 'search_text': text, 'embedding': vector, 'embedding_model': VOYAGE_MODEL, 'embedding_dimensions': EMBEDDING_DIMENSIONS, 'summary_model': OPENAI_MODEL, 'pipeline_signature': signature, 'updated_at': now}
    progress('saving')
    coll.update_one({'_id': call_id}, {'$set': document, '$setOnInsert': {'created_at': now}}, upsert=True)
    document.pop('embedding')
    document['_id'] = call_id
    progress('saved')
    return (document, 'Summary and Voyage embedding saved to Atlas.')

def progress(stage, data=None):
    if stage == "summarizing":
        print_summary_delta.previous = ""
        print("\nOpenAI: summarizing...")
    elif stage == "summary_delta":
        print_summary_delta(stage, data)
    elif stage == "embedding":
        print("\nVoyage: embedding the summary...")
    elif stage == "saving":
        print("Atlas: saving...")
    elif stage == "saved":
        print("Atlas: saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", nargs="?", type=Path)
    parser.add_argument("--force", action="store_true", help="Regenerate an existing call")
    args = parser.parse_args()
    calls = {str(args.transcript): args.transcript.read_text()} if args.transcript else SAMPLE_CALLS
    for name, transcript in calls.items():
        document, message = ingest(transcript, name, args.force, progress)
        print(f"{document['title']}: {message}")
        print(f"Document ID: {document['_id']}")
