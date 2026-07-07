from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):
    """
    Kept for backwards compatibility - returns the full document as a
    single string (pages joined with newlines).
    """

    pages = extract_pages_from_pdf(pdf_path)

    return "\n".join(page_text for _, page_text in pages)


def extract_pages_from_pdf(pdf_path):
    """
    Returns a list of (page_number, page_text) tuples, 1-indexed.

    Extracting per-page (instead of one big blob) is what lets the rest
    of the pipeline attach a page number to every chunk, which in turn
    lets the assistant cite "page 4" instead of just an unattributed
    excerpt.
    """

    reader = PdfReader(pdf_path)

    pages = []

    for i, page in enumerate(reader.pages):

        extracted = page.extract_text()

        if extracted:
            pages.append((i + 1, extracted))

    return pages
