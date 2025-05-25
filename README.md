# Text Document Similarity Engine

## Description

This project provides a Python-based solution for identifying and grouping similar text documents. It leverages techniques like MinHash and Locality Sensitive Hashing (LSH) for efficient similarity estimation and supports stream-based clustering, making it suitable for processing documents incrementally. An example script demonstrates how to group similar articles fetched from an Elasticsearch index.

## Features

- **Efficient Similarity Detection:** Utilizes MinHash and Locality Sensitive Hashing (LSH) to quickly find candidate similar items in large datasets.
- **Stream-Based Clustering:** Processes and groups documents incrementally as they arrive, suitable for real-time or continuous data feeds.
- **Text Preprocessing:** Includes utilities for basic text preprocessing, such as tokenization.
- **Pluggable Storage:** Features a Key-Value storage abstraction (`KVStorage`) with a Redis implementation (`RedisStorage`) for persisting necessary data for the clustering process.
- **Elasticsearch Integration Example:** Provides a script (`similarity/group_es_articles.py`) demonstrating a practical use case of fetching articles from Elasticsearch, identifying similarities, and updating them with group information.
- **Configurable Hashing:** Allows customization of MinHash parameters (signature dimension, LSH threshold, and band/row configuration).

## Installation

To use this project, you'll need to install the required Python libraries. You can do this using pip:

```bash
pip install redis==3.5.3 elasticsearch==7.9.1
```

Alternatively, if you have a `requirements.txt` file with these dependencies, you can run:

```bash
pip install -r requirements.txt
```
Ensure you have Python 3.x installed.

## Usage

This library can be used in two main ways: by running the example Elasticsearch article grouping script or by integrating the `StreamClustering` component directly into your application.

### Running the Elasticsearch Article Grouping Script

The `similarity/group_es_articles.py` script is designed to stream articles from an Elasticsearch index, identify similar articles, and group them.

**Prerequisites:**
- Elasticsearch instance running and accessible.
- Redis instance running and accessible (used by `RedisStorage` for `StreamClustering`).

**Configuration:**
Before running the script, you need to configure the following parameters within the script itself (in the `if __name__ == '__main__':` block):
- `INDEX_NAME`: Your Elasticsearch index name (e.g., 'news_index').
- `DOC_TYPE`: Your Elasticsearch document type (e.g., 'news_doc_type').
- `FROM_DATE`: The start date for fetching articles (format: "YYYY-MM-DD").
- `TO_DATE`: The end date for fetching articles (format: "YYYY-MM-DD").
- Elasticsearch client connection details if not localhost default.
- Redis connection details if not localhost default (for `RedisStorage`).

**Running the script:**
Once configured, you can run the script directly:
```bash
python similarity/group_es_articles.py
```
The script will:
1. Scan documents from Elasticsearch for the specified date range.
2. For each document, preprocess its text content.
3. Use `StreamClustering` (with `MinhashLSH` and `RedisStorage`) to find a group ID for the document.
4. Update the documents in Elasticsearch with their respective `group_id` and an `is_sim` flag.
5. Log progress and statistics.

Make sure the Elasticsearch index mapping for the text field is suitable for your needs (e.g., appropriate analyzer). The script expects a field named `text` in the `_source` of the documents.

### Using StreamClustering directly

The `StreamClustering` class (`similarity/stream_clustering.py`) provides a flexible way to find groups for incoming items based on their tokenized representation.

**Core Components:**
- **Hashing Strategy:** An object that implements a `hash(self, tokens: list) -> list` method. `MinhashLSH` is provided as one such strategy.
- **Key-Value Storage:** An object that implements the `KVStorage` interface (defined in `similarity/io/kv_storage.py`), used to store mappings between hashes and document/group IDs. `RedisStorage` is a provided implementation.

**Example:**

```python
from similarity.stream_clustering import StreamClustering, MinhashLSH
from similarity.io.kv_storage import RedisStorage # Assuming Redis is running
from similarity.nlp.preprocess.preprocessor import SimplePreprocessor

# 1. Initialize the hashing strategy
# dim: The dimension of the MinHash signature (number of hash functions).
# threshold: The Jaccard similarity threshold for considering items similar.
# length: The number of hash values per item to generate for LSH banding (bands * rows).
hasher = MinhashLSH(dim=128, threshold=0.85, length=16) # Example parameters

# 2. Initialize the Key-Value storage
kv_storage = RedisStorage(host='localhost', port=6379) # Default Redis connection
# Clear previous state if needed for a fresh run
# kv_storage.delete('hash2doc') # Stores mapping from LSH hash to a representative document ID
# kv_storage.delete('doc2sim')  # Stores mapping from a document ID to its group ID

# 3. Initialize StreamClustering
stream_clusterer = StreamClustering(hasher, kv_storage)

# 4. (Optional) Initialize a preprocessor to get tokens
preprocessor = SimplePreprocessor()

# 5. Process items
documents = [
    {"id": "doc1", "text": "This is the first document about apples."},
    {"id": "doc2", "text": "Another article discussing apple varieties."},
    {"id": "doc3", "text": "Oranges and bananas are fruits too."},
    {"id": "doc4", "text": "A final document on the topic of apples."},
]

for doc in documents:
    doc_id = doc["id"]
    text_content = doc["text"]
    
    # Preprocess text to get tokens
    # The preprocessor returns a list of sentences, each sentence is a list of tokens (dictionaries)
    tokens = [token['content'] for sent in preprocessor.process_document(text_content) for token in sent]
    
    if not tokens:
        print(f"Document {doc_id} has no tokens after preprocessing.")
        group_id = doc_id # Assign doc_id as group_id if no tokens
    else:
        group_id = stream_clusterer.find_group(doc_id, tokens)
    
    print(f"Document ID: {doc_id}, Group ID: {group_id}")

# Expected output might show doc1, doc2, and doc4 grouped together if similarity is high enough.
# doc3 would likely be in its own group.
```

This example demonstrates how to set up `StreamClustering` with `MinhashLSH` and `RedisStorage` to group incoming documents. You can implement custom hashing strategies or KV storage solutions by adhering to their respective interfaces.


## Key Components

This project is composed of several key modules that work together:

- **`similarity/lsh/lsh.py`**:
  - Contains implementations of Locality Sensitive Hashing (LSH) and MinHash.
  - `MinHashSignature`: Creates MinHash signatures for sets of items (e.g., tokens). MinHash is a technique to quickly estimate Jaccard similarity between sets.
  - `LSH`: Implements the LSH algorithm using a banding approach. It takes MinHash signatures and hashes them into buckets such that similar signatures are likely to fall into the same bucket. This allows for efficient finding of candidate similar pairs.
  - `Cluster`: A class that uses `MinHashSignature` and `LSH` to cluster items based on Jaccard similarity.

- **`similarity/nlp/preprocess/preprocessor.py`**:
  - Provides text preprocessing capabilities.
  - `SimplePreprocessor`: A basic preprocessor that likely performs tasks such as tokenization, lowercasing, and potentially stop word removal or stemming (though the exact steps would need to be confirmed by inspecting its `process_document` method). It prepares text data for the hashing process.
  - Includes `SentenceSplitter` and `Tokenizer` which are fundamental NLP tasks.

- **`similarity/io/kv_storage.py`**:
  - Defines an abstract interface `KVStorage` for key-value store operations (`get`, `put`, `delete`).
  - `RedisStorage`: An implementation of `KVStorage` using Redis. This is used by `StreamClustering` to persist mappings required for the clustering process, such as LSH bucket contents (`hash2doc`) and document-to-group assignments (`doc2sim`).

## Requirements

The project relies on the following Python libraries:

- `redis==3.5.3`: Used by `RedisStorage` for key-value storage, essential for `StreamClustering`.
- `elasticsearch==7.9.1`: Used in the example script `similarity/group_es_articles.py` to fetch articles from and update articles in an Elasticsearch index.

You can install these using pip:
```bash
pip install -r requirements.txt
```
Python 3.x is required.

## License

This project is licensed under the Apache License, Version 2.0.
A copy of the license is available in the `LICENSE` file in this repository.
You can also find it at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0).
