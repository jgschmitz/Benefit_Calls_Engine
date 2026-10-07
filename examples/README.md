# Plan Benefit Search: Focused Python Examples

Small runnable examples of the same pipeline as `app.py`, without Streamlit.
Drop this `examples/` folder beside your existing `app.py` and root README.
These examples do not import or modify the app.

## Examples

| Script | What it demonstrates | Services called |
|---|---|---|
| `summarize_call.py` | Stream a factual summary and validate its structured JSON | OpenAI |
| `embed_summary.py` | Turn summary text into a 1,024-dimensional vector | Voyage AI |
| `store_call.py` | Summarize, embed, and upsert calls with duplicate detection | OpenAI, Voyage AI, Atlas |
| `create_indexes.py` | Explicitly create missing text/vector indexes and inspect readiness | Atlas |
| `keyword_search.py` | Search summary text using `$search` | Atlas |
| `vector_search.py` | Embed a query and retrieve semantically similar summaries | Voyage AI, Atlas |
| `hybrid_search.py` | Combine keyword and vector ranks with reciprocal rank fusion | Voyage AI, Atlas |

`config.py` holds the settings, `atlas_connection.py` shares the connection,
and `sample_calls.py` contains the two fictional transcripts. Each example can
run separately with its required credentials. Keep the folder together because
examples share these small modules; none requires the Streamlit app.

## Configuration

Fill in the plain variables in `examples/config.py`:

```python
MONGO_URI = ""
VOYAGE_API_KEY = ""
OPENAI_API_KEY = ""
```

The examples use `plan_benefit_search.call_summaries`, `gpt-4.1-mini` for summaries,
and `voyage-4-large` with 1,024 dimensions for embeddings, matching the supplied
app. They retain the legacy `openai.ChatCompletion.create()` API; no OpenAI SDK
upgrade is needed. They use the app's existing Python packages. Commit credential
placeholders, keeping your actual keys and URI in your local copy.

## Run from the repository root

Preview the two independent AI steps:

```bash
python examples/summarize_call.py
python examples/embed_summary.py
```

Create indexes explicitly, ingest the fictional calls, and check readiness:

```bash
python examples/create_indexes.py
python examples/store_call.py
python examples/create_indexes.py --status
```

When both indexes report `queryable=True`, run the retrieval examples:

```bash
python examples/keyword_search.py "prior authorization"
python examples/vector_search.py "What will I pay for my knee scan?"
python examples/hybrid_search.py "therapy visits and referral requirements"
```

Atlas indexes update asynchronously; newly stored documents may take a moment to
appear in search even after an index is queryable. Existing indexes with the same
names are preserved. Confirm their definitions match if you created them manually.

To use your own text files or repeat the live summarization:

```bash
python examples/summarize_call.py transcript.txt
python examples/embed_summary.py summary.txt
python examples/store_call.py transcript.txt
python examples/store_call.py --force
```

The summarization example prints the narrative as it streams, then the validated
JSON. The embedding example uses a short built-in summary unless given a text file.
`store_call.py` combines both stages and saves the complete document. It uses the
same transcript hash and pipeline signature as the app, so unchanged calls already
stored by the app are skipped. `--force` regenerates and updates those documents.

## What is stored and searched

Each stored call contains the transcript, structured summary, follow-up actions,
unresolved questions, summary-derived `search_text`, Voyage `embedding`, model
metadata, and timestamps. Keyword retrieval searches `search_text`; vector
retrieval searches its embedding. The query is embedded with `input_type="query"`,
while summaries use `input_type="document"`. Model and dimension filters keep
vector retrieval aligned with the configured embeddings.

## Hybrid ranking

Atlas returns up to 50 candidates from each retrieval method. Python deduplicates
by document ID and adds weighted reciprocal-rank contributions:

```text
score = 0.5 / (60 + keyword_rank) + 0.5 / (60 + semantic_rank)
```

A missing rank contributes zero. Raw keyword and vector scores are not added.
This matches the meeting demo; it does not call the Voyage reranking API.

## Verification

Python syntax and an offline fusion check were run when packaging. Live API calls
and Atlas operations require your credentials and have not been exercised here.
