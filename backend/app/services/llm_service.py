from groq import Groq
from dotenv import load_dotenv
import os
import json
import re

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Shown whenever there is no retrieved context to answer from.
# Centralized here (instead of duplicated as a string) so routes/chat.py
# can short-circuit and skip the LLM call entirely when there's nothing
# to ground an answer in.
NO_CONTEXT_MESSAGE = (
    "I couldn't find the answer in the provided insurance documents."
)

# How many prior turns of chat history to feed back to the model as
# conversational memory. Kept small on purpose: this is only meant to
# resolve references like "its lock-in period" to the actual policy
# term being discussed, not to replace the retrieved document context.
MAX_HISTORY_TURNS = 4


def _extract_json(raw_text):
    """
    Best-effort extraction of a JSON object from the model's raw reply.
    Models occasionally wrap JSON in markdown fences or add stray text
    around it, so this strips fences and grabs the first {...} block
    before parsing, instead of assuming the reply is pure JSON.
    """

    text = raw_text.strip()

    # Strip ```json ... ``` or ``` ... ``` fences if present.
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"```$", "", text).strip()

    # Grab the first {...} block in case of any leading/trailing text.
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        text = match.group(0)

    return json.loads(text)


def _format_history(history):
    """
    Formats the last few conversation turns as plain text for the
    prompt. `history` is a list of {"question": ..., "answer": ...}
    dicts, oldest first.
    """

    if not history:
        return ""

    recent = history[-MAX_HISTORY_TURNS:]

    lines = []

    for turn in recent:
        question = (turn.get("question") or "").strip()
        answer = (turn.get("answer") or "").strip()

        if question:
            lines.append(f"User: {question}")
        if answer:
            lines.append(f"Assistant: {answer}")

    if not lines:
        return ""

    return (
        "Recent conversation (for resolving references like \"it\" or "
        "\"that policy\" only - do not treat this as document context):\n"
        + "\n".join(lines)
    )


def _attach_pages(source_texts, context_chunks):
    """
    Given short verbatim excerpts returned by the model, finds which
    retrieved chunk each excerpt came from so it can be tagged with a
    page number. Falls back to page=None if no chunk contains the
    excerpt (e.g. the model paraphrased slightly).
    """

    tagged = []

    for excerpt in source_texts:

        page = None

        for chunk in context_chunks:
            if excerpt and excerpt in chunk["text"]:
                page = chunk.get("page")
                break

        tagged.append({"text": excerpt, "page": page})

    return tagged


def generate_answer(question, context_chunks, history=None):

    """
    `context_chunks` is a list of {"text": ..., "page": ...} dicts (the
    retrieved chunks for this query).

    Returns a dict: {"answer": str, "sources": list[{"text", "page"}]}.

    "sources" are short, exact excerpts copied from the context that
    directly support the answer - not entire retrieved chunks. This
    avoids surfacing unrelated boilerplate policy wording alongside the
    real supporting text.
    """

    # Defensive check: even if this function is called directly with no
    # chunks, never let the model answer from its own general
    # knowledge. Empty context is exactly what previously caused
    # generic, non-policy-specific answers (e.g. a made-up "suicide
    # clause" duration) instead of the real document wording.
    if not context_chunks:
        return {"answer": NO_CONTEXT_MESSAGE, "sources": []}

    context_text = "\n\n".join(
        f"[Page {chunk.get('page') or '?'}] {chunk['text']}"
        for chunk in context_chunks
    )

    history_block = _format_history(history)

    prompt = f"""
You are an Insurance AI Assistant.

Answer the user's question using ONLY the information in the given
insurance context below. Do not use any outside knowledge, and do not
fill in typical/standard clause wording from general insurance
knowledge if it is not explicitly present in the context.

{history_block}

If the exact answer is not present in the context, set "answer" to
exactly: "{NO_CONTEXT_MESSAGE}" and "sources" to an empty list.

Respond with ONLY a JSON object (no markdown fences, no extra text)
in exactly this shape:

{{
  "answer": "<direct, concise answer to the question>",
  "sources": ["<short exact excerpt copied verbatim from the context, without the [Page N] marker>", "..."]
}}

Rules for "sources":
- Each entry must be copied verbatim from the context (no paraphrasing,
  and do not include the "[Page N]" marker itself in the excerpt).
- Each entry must be short - a single clause or sentence, not a whole
  paragraph, and must directly support the answer.
- Do NOT include unrelated boilerplate, headers, or surrounding text
  that isn't needed to support the answer.
- Include at most 3 entries, and omit any that aren't necessary.
- If the answer is the "couldn't find" message, "sources" must be [].

Context:
{context_text}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful insurance assistant. You must "
                    "answer strictly from the provided context and never "
                    "supplement it with outside/general knowledge. You "
                    "always reply with a single valid JSON object and "
                    "nothing else."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    raw_reply = response.choices[0].message.content

    try:

        parsed = _extract_json(raw_reply)

        answer = parsed.get("answer", "").strip()

        raw_sources = parsed.get("sources", [])

        # Guard against a malformed/empty answer slipping through.
        if not answer:
            answer = NO_CONTEXT_MESSAGE
            raw_sources = []

        if not isinstance(raw_sources, list):
            raw_sources = []

        # Keep only short, non-empty, string excerpts - defends against
        # the model still returning a whole chunk as one "source".
        raw_sources = [
            s.strip() for s in raw_sources
            if isinstance(s, str) and s.strip()
        ][:3]

        sources = _attach_pages(raw_sources, context_chunks)

        return {"answer": answer, "sources": sources}

    except Exception as e:

        # Fallback: the model didn't return valid JSON. Rather than
        # crash the request, fall back to treating the raw reply as the
        # answer with no fabricated sources - callers can still fall
        # back further to the raw retrieved chunks if they want.
        print("Warning: could not parse structured LLM output -", e)

        return {"answer": raw_reply.strip(), "sources": []}
