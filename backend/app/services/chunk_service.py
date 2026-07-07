from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)


def chunk_text(text):
    """
    Kept for backwards compatibility - chunks a single text blob with
    no page attribution.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(text)

    return chunks


def chunk_pages(pages):
    """
    Chunks a list of (page_number, page_text) tuples and returns a list
    of dicts: {"text": <chunk text>, "page": <page number>}.

    Splitting page-by-page (instead of joining every page into one
    string first) means a chunk never straddles a page boundary, so the
    page number attached to each chunk is always accurate.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = []

    for page_number, page_text in pages:

        page_chunks = splitter.split_text(page_text)

        for chunk in page_chunks:

            chunks.append({
                "text": chunk,
                "page": page_number
            })

    return chunks
