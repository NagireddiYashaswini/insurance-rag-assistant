
import chromadb

from fastembed import TextEmbedding

from rank_bm25 import BM25Okapi

# ----------------------------
# Initialize ChromaDB
# ----------------------------

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_or_create_collection(
    name="insurance_docs"
)

# ----------------------------
# Embedding Model
# ----------------------------

embedding_model = TextEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ----------------------------
# Store Chunks
# ----------------------------

def store_chunks(chunks, filename):

    """
    Stores text chunks and embeddings into ChromaDB.

    `chunks` may be either:
      - a list of plain strings (legacy format, page defaults to None)
      - a list of {"text": ..., "page": ...} dicts (page-aware format)
    """

    # Remove old chunks for same file

    try:

        existing = collection.get(
            where={
                "filename": filename
            }
        )

        if existing["ids"]:

            collection.delete(
                ids=existing["ids"]
            )

    except Exception as e:

        # NOTE: previously this silently swallowed all errors, which made
        # it impossible to notice if old chunks for a re-uploaded file
        # were failing to clear out. Log it instead so problems surface.
        print("Warning: could not clear old chunks for", filename, "-", e)

    # Normalize to a list of {"text": ..., "page": ...} dicts.

    normalized = []

    for chunk in chunks:

        if isinstance(chunk, dict):
            normalized.append({
                "text": chunk.get("text", ""),
                "page": chunk.get("page")
            })
        else:
            normalized.append({
                "text": chunk,
                "page": None
            })

    texts = [c["text"] for c in normalized]

    # Generate embeddings
    # fastembed returns a generator of numpy arrays, one per input text.
    # ChromaDB needs plain lists, so convert each vector with .tolist().

    embeddings = [
        vector.tolist()
        for vector in embedding_model.embed(texts)
    ]

    ids = []

    metadatas = []

    for i, chunk in enumerate(normalized):

        ids.append(
            f"{filename}_{i}"
        )

        metadatas.append({
            "filename": filename,
            # Chroma metadata values can't be None, so fall back to 0
            # (meaning "unknown page") for legacy/plain-string chunks.
            "page": chunk["page"] if chunk["page"] is not None else 0
        })

    # Store in ChromaDB

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(
        "Stored", len(texts),
        "chunks with filename metadata for", filename
    )

    return True


# ----------------------------
# Document management
# ----------------------------

def list_documents():
    """
    Returns the distinct list of filenames currently indexed in the
    vector store, so the frontend can show a document switcher instead
    of only remembering the single most-recently-uploaded file.
    """

    all_items = collection.get(include=["metadatas"])

    filenames = set()

    for metadata in all_items.get("metadatas", []) or []:
        if metadata and metadata.get("filename"):
            filenames.add(metadata["filename"])

    return sorted(filenames)


def delete_document(filename):
    """
    Removes every chunk belonging to `filename` from the vector store.
    Returns the number of chunks deleted.
    """

    existing = collection.get(
        where={
            "filename": filename
        }
    )

    ids = existing.get("ids", [])

    if ids:
        collection.delete(ids=ids)

    return len(ids)


# ----------------------------
# Search Chunks (hybrid: vector similarity + keyword/BM25 re-ranking)
# ----------------------------

def _tokenize(text):
    return text.lower().split()


def search_chunks(query, filename, n_results=3):

    """
    Hybrid search over a single document:

    1. Vector similarity search pulls a wider pool of semantically
       relevant candidates from ChromaDB.
    2. BM25 keyword scoring is run over that same candidate pool.
    3. Candidates are re-ranked by a weighted blend of the two scores,
       which helps when the exact wording of the query (e.g. a defined
       term like "surrender value") matters as much as its meaning.
    """

    # fastembed's query_embed() is also a generator; pull out the single
    # vector for this one query and convert it to a plain list.
    query_embedding = next(
        embedding_model.query_embed(query)
    ).tolist()

    # Pull a larger candidate pool than we ultimately need so BM25 has
    # something to re-rank.
    candidate_pool = max(n_results * 4, 10)

    results = collection.query(
        query_embeddings=[query_embedding],

        n_results=candidate_pool,

        where={
            "filename": filename
        }
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    ids = results["ids"][0]

    if not documents:

        # This is the situation that previously led to hallucinated
        # answers: no chunks matched this exact filename. Usually this
        # means the PDF hasn't been (re-)uploaded since the vector store
        # was last rebuilt, or the filename doesn't match what was
        # stored. Logging it here makes that immediately visible instead
        # of silently handing an empty context to the LLM.
        print(
            "No chunks found in ChromaDB for filename:", filename,
            "- try re-uploading this PDF."
        )

        return {
            "documents": [],
            "metadatas": [],
            "distances": [],
            "ids": []
        }

    # ---- BM25 re-ranking over the candidate pool ----

    tokenized_corpus = [_tokenize(doc) for doc in documents]

    try:
        bm25 = BM25Okapi(tokenized_corpus)
        bm25_scores = bm25.get_scores(_tokenize(query))
    except Exception as e:
        print("Warning: BM25 scoring failed, falling back to vector-only ranking -", e)
        bm25_scores = [0.0] * len(documents)

    # Normalize each score type to [0, 1] so they can be blended fairly.
    max_bm25 = max(bm25_scores) if bm25_scores and max(bm25_scores) > 0 else 1.0

    # Chroma distances are "lower is better" (cosine distance); convert
    # to a "higher is better" similarity in [0, 1] before blending.
    max_distance = max(distances) if distances else 1.0
    max_distance = max_distance if max_distance > 0 else 1.0

    combined = []

    for i in range(len(documents)):

        vector_similarity = 1 - (distances[i] / max_distance)
        keyword_score = bm25_scores[i] / max_bm25

        # Weighted toward semantic similarity, with keyword match as a
        # tie-breaker / boost for exact terminology.
        final_score = (0.7 * vector_similarity) + (0.3 * keyword_score)

        combined.append((final_score, i))

    combined.sort(key=lambda x: x[0], reverse=True)

    top_indices = [i for _, i in combined[:n_results]]

    return {
        "documents": [documents[i] for i in top_indices],
        "metadatas": [metadatas[i] for i in top_indices],
        "distances": [distances[i] for i in top_indices],
        "ids": [ids[i] for i in top_indices]
    }
