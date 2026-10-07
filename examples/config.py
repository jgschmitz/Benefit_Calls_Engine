"""Demo configuration. Fill in the credentials here; no environment variables."""
MONGO_URI = ''

VOYAGE_API_KEY = ''

OPENAI_API_KEY = ''

DB_NAME = 'plan_benefit_search'

COLLECTION_NAME = 'call_summaries'

OPENAI_MODEL = 'gpt-4.1-mini'

VOYAGE_MODEL = 'voyage-4-large'

EMBEDDING_DIMENSIONS = 1024

TEXT_INDEX = 'call_summaries_text'

VECTOR_INDEX = 'call_summaries_vector'

SUMMARY_VERSION = '1'

CANDIDATE_LIMIT = 50

RRF_K = 60

def require_settings(*names):
    missing = [name for name in names if not globals()[name].strip()]
    if missing:
        raise ValueError('Fill in these variables at the top of the script: ' + ', '.join(missing))
