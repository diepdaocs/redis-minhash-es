import re


def chunk_text(text, byte_size, granularity=3):
    chunks = []

    # Determine chunk size
    chunk_size = int(byte_size / 5)
    granularity = min(int(chunk_size / 5) or 1, granularity)

    tmp_text = text[:chunk_size]
    txt_len = len(text)
    while len(tmp_text.encode('utf-8')) < byte_size and chunk_size < txt_len:
        chunk_size += granularity
        tmp_text = text[:chunk_size]

    # Chunk text
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i: i + chunk_size])

    return chunks


def generate_ngrams(items, min_gram, max_gram):
    result = []
    for ngram in range(min_gram, max_gram + 1):
        for idx in range(0, len(items) - ngram + 1):
            result.append(items[idx: idx + ngram])

    return result


prevent_zero_div = 1e-21


def is_mostly_numeric(text, num_ratio=0.5):
    return len([c for c in text if c.isnumeric()]) / float(len(text) + prevent_zero_div) >= num_ratio


def is_mostly_alpha(text, alpha_ratio=0.5):
    return len([c for c in text if c.isalpha()]) / float(len(text) + prevent_zero_div) >= alpha_ratio


def is_mostly_numeric_tokens(tokens, num_ratio=0.5):
    return len([c for c in tokens if c.isnumeric()]) / float(len(tokens) + prevent_zero_div) >= num_ratio


def tokenize(text):
    return [t for t in [re.sub(r'\W+', '', t.strip()).strip() for t in text.split(' ')] if t and t.strip()]
