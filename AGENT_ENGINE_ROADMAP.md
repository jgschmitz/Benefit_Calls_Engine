# Extending the Demo with Atlas Agent Engine

This demo turns benefit-call transcripts into structured summaries with OpenAI,
embeds those summaries with Voyage AI, and stores and searches them in MongoDB
Atlas. A natural next step is a conversational agent that can use these functions
as tools and help users investigate the calls.

This document describes a proposed extension. Agent Engine integration is not
implemented in the current application.

## First milestone: Ask questions across calls

Keep the Streamlit interface and add a conversational investigation experience:

> “Find calls about physical therapy authorization.”
>
> “Which of those calls still have unresolved follow-up actions?”
>
> “Show me what the agent told the patient about the visit limit.”

The proposed agent would search the stored summaries, retrieve supporting call
records, and answer with references to those records. Follow-up questions would
use conversation context to stay focused on the calls already discussed.

## Reuse the existing building blocks

| Current component | Proposed role in the agent |
|---|---|
| OpenAI summarization | Generate a structured summary of a selected transcript |
| Voyage AI embeddings | Embed summaries and search queries |
| Atlas keyword and vector search | Retrieve relevant calls |
| Python reciprocal rank fusion | Combine the two retrieval result sets, as in the current demo |
| Atlas document lookup | Retrieve a selected call's full summary, transcript, and follow-up actions |
| Streamlit interface | Present the conversation, retrieved evidence, and processing steps |

Atlas Agent Engine documents support for agent deployment and management,
session state, and long-term memory. The proposed integration would wrap the
existing Python functions as agent tools and connect the interface to the agent.
The exact SDK, tool definitions, and deployment configuration remain implementation
work; this is not a drop-in deployment of the current Streamlit application.

## Proposed tools

| Tool | Purpose |
|---|---|
| `search_calls(query)` | Return relevant call summaries and their document IDs |
| `get_call(call_id)` | Retrieve the source record supporting an answer |
| `get_follow_up_actions(call_ids)` | Return recorded follow-up actions and unresolved questions for selected calls |

Start with retrieval over already stored calls. Add summarization and ingestion
tools later if the conversational workflow needs them.

Recorded follow-up actions describe the state captured in the call. Without a
separate status update, the agent should not assume an action is still open or
has been completed. Answers should distinguish what the agent said during a call
from independently verified plan coverage.

## Later milestone: Compare calls with plan benefits

Add authoritative plan documents so the agent can compare statements made during
a call with the applicable benefit provisions.

For example:

> “Find calls where patients were confused about therapy authorization. Compare
> what they were told with the applicable plan provisions.”

This requires plan identifiers, effective dates, document versions, and source
references that connect each call to the correct benefits. A separate plan lookup
tool could retrieve those provisions. The agent could then flag potential
discrepancies for review and show both pieces of evidence.

Call summaries alone are not sufficient to verify coverage. Missing plan context
should remain an explicit unanswered question.

## Suggested implementation sequence

1. Expose the existing call search and document lookup functions as agent tools.
2. Connect a Streamlit conversation view to an Agent Engine-hosted agent.
3. Add session context for follow-up questions and display source call references.
4. Evaluate retrieval and answers against the two fictional sample calls.
5. Introduce plan-document retrieval and comparison as a separate milestone.

The existing app and focused Python examples remain useful demonstrations of the
underlying pipeline throughout this extension.

## Documentation and status

[MongoDB Atlas Agent Engine documentation](https://www.mongodb.com/docs/agentengine/)

As reviewed on October 7, 2026, the documentation labels Atlas Agent Engine Public
Preview and does not recommend production workloads during that preview. This
roadmap is intended for an exploratory demo; consult the current documentation
when implementing it.
