
import chromadb

from langchain_community.embeddings import (
    HuggingFaceEmbeddings
)

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

embedding_model = HuggingFaceEmbeddings(
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

    embeddings = embedding_model.embed_documents(
        texts
    )

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

    1. Vector similarity search
    2. BM25 keyword ranking
    3. Combined scoring
    """

    query_embedding = embedding_model.embed_query(
        query
    )

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

    # ----------------------------
    # No Results
    # ----------------------------

    if len(documents) == 0:

        print(
            "No chunks found in ChromaDB for filename:",
            filename
        )

        return {
            "documents": [],
            "metadatas": [],
            "distances": [],
            "ids": []
        }

    # ----------------------------
    # BM25 Ranking
    # ----------------------------

    tokenized_corpus = [
        _tokenize(doc)
        for doc in documents
    ]

    try:

        bm25 = BM25Okapi(tokenized_corpus)

        bm25_scores = list(
            bm25.get_scores(
                _tokenize(query)
            )
        )

    except Exception as e:

        print(
            "Warning: BM25 failed:",
            e
        )

        bm25_scores = [0.0] * len(documents)

    # ----------------------------
    # Normalize Scores
    # ----------------------------

    if len(bm25_scores) > 0 and max(bm25_scores) > 0:

        max_bm25 = max(bm25_scores)

    else:

        max_bm25 = 1.0

    if len(distances) > 0 and max(distances) > 0:

        max_distance = max(distances)

    else:

        max_distance = 1.0

    # ----------------------------
    # Combine Scores
    # ----------------------------

    combined = []

    for i in range(len(documents)):

        vector_similarity = 1 - (
            distances[i] / max_distance
        )

        keyword_score = (
            bm25_scores[i] / max_bm25
        )

        final_score = (
            0.7 * vector_similarity
        ) + (
            0.3 * keyword_score
        )

        combined.append(
            (final_score, i)
        )

    # ----------------------------
    # Sort Results
    # ----------------------------

    combined.sort(
        key=lambda x: x[0],
        reverse=True
    )

    top_indices = [
        i for _, i in combined[:n_results]
    ]

    # ----------------------------
    # Return Results
    # ----------------------------

    return {

        "documents": [
            documents[i]
            for i in top_indices
        ],

        "metadatas": [
            metadatas[i]
            for i in top_indices
        ],

        "distances": [
            distances[i]
            for i in top_indices
        ],

        "ids": [
            ids[i]
            for i in top_indices
        ]
    }

