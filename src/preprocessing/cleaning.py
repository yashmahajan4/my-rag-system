import re
import html
import unicodedata


def normalize_unicode(text: str) -> str:
    """
    Normalize unicode characters.
    """
    return unicodedata.normalize("NFKC", text)


def decode_html_entities(text: str) -> str:
    """
    Convert HTML entities to text.
    """
    return html.unescape(text)


def remove_urls(text: str) -> str:
    """
    Remove raw URLs.
    """
    return re.sub(
        r"https?://\S+|www\.\S+",
        "",
        text
    )


def remove_emails(text: str) -> str:
    """
    Remove email addresses.
    """
    return re.sub(
        r"\S+@\S+",
        "",
        text
    )


def remove_page_numbers(text: str) -> str:
    """
    Remove standalone page numbers.
    """
    lines = text.splitlines()

    cleaned = []

    for line in lines:

        line = line.strip()

        if re.fullmatch(r"\d+", line):
            continue

        if re.fullmatch(r"page\s+\d+", line.lower()):
            continue

        cleaned.append(line)

    return "\n".join(cleaned)


def remove_extra_whitespace(text: str) -> str:

    text = re.sub(r"\t+", " ", text)
    text = re.sub(r" +", " ", text)

    text = re.sub(
        r"\n\s*\n\s*\n+",
        "\n\n",
        text
    )

    return text.strip()


def remove_control_characters(text: str) -> str:
    """
    Remove hidden characters.
    """
    return "".join(
        char
        for char in text
        if unicodedata.category(char)[0] != "C"
        or char in "\n\t"
    )


def remove_repeated_headers(
    text: str,
    threshold: int = 3
) -> str:
    """
    Removes lines repeated many times
    across a document.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
    ]

    counts = {}

    for line in lines:

        if len(line) < 5:
            continue

        counts[line] = counts.get(line, 0) + 1

    repeated = {
        line
        for line, count in counts.items()
        if count >= threshold
    }

    cleaned = [
        line
        for line in lines
        if line not in repeated
    ]

    return "\n".join(cleaned)


def clean_text(text: str) -> str:
    """
    Master cleaning pipeline.
    """

    if not text:
        return ""

    text = decode_html_entities(text)

    text = normalize_unicode(text)

    text = remove_control_characters(text)

    text = remove_urls(text)

    text = remove_emails(text)

    text = remove_page_numbers(text)

    text = remove_extra_whitespace(text)

    return text


def clean_documents(docs):
    """
    Clean LangChain Documents.
    """

    cleaned_docs = []

    for doc in docs:

        doc.page_content = clean_text(
            doc.page_content
        )

        cleaned_docs.append(doc)

    return cleaned_docs











