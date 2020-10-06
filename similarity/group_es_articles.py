from datetime import datetime, timedelta

from elasticsearch import Elasticsearch, helpers

from similarity.helpers.log_helpers import get_logger
from similarity.io.kv_storage import RedisStorage
from similarity.nlp.preprocess.preprocessor import SimplePreprocessor
from similarity.stream_clustering import MinhashLSH, StreamClustering

"""
A sample to stream message from Elasticsearch and grouping similar message in O(1) time complexity
using Minhash Local Sensitive Hashing
"""


def scan_docs(from_date, to_date):
    global DOC_COUNT
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "created_date": {
                                "from": from_date.strftime('%Y-%m-%d'),
                                "to": to_date.strftime('%Y-%m-%d')
                            }
                        }
                    }
                ],
                "must_not": [
                    {
                        "exists": {
                            "field": "is_sim"
                        }
                    }
                ]
            }
        }
    }

    count = es_client.count(index=INDEX_NAME, doc_type=DOC_TYPE, body=query)['count']
    logger.info("Scanning articles from %s to %s: found %d docs", from_date, to_date, count)

    query['_source'] = ['text']
    for doc in helpers.scan(client=es_client, index=INDEX_NAME, doc_type=DOC_TYPE, query=query,
                            scroll='20m', request_timeout=1200):
        DOC_COUNT += 1
        yield doc


def check_sim(docs):
    global SIM_COUNT, GROUP_COUNT
    for doc in docs:
        doc_id = doc['_id']
        text = doc['_source']['text']
        tokens = [token['content'] for sent in preprocessor.process_document(text) for token in sent]
        group_id = stream_sim_checker.find_group(doc_id, tokens)
        is_sim = group_id != doc_id

        if is_sim:
            SIM_COUNT += 1
        else:
            GROUP_COUNT += 1

        if DOC_COUNT % CHUNK_SIZE == 0:
            logger.info("***[Sim docs] / total: %d/%d" % (SIM_COUNT, DOC_COUNT))
            logger.info("***[No. of Group] / total: %d/%d" % (GROUP_COUNT, DOC_COUNT))
            logger.info("------------------------------------------------------------")

        yield {
            '_id': doc_id,
            'group_id': group_id,
            'is_sim': is_sim
        }


def gen_update_actions(docs_with_sim_info):
    for doc in docs_with_sim_info:
        yield {
            '_op_type': 'update',
            '_index': INDEX_NAME,
            '_type': DOC_TYPE,
            '_id': doc['_id'],
            'doc': {
                'group_id': doc['group_id'],
                'is_sim': doc['is_sim']
            }
        }


def update_docs(docs_with_sim_info):
    success_count, failed_count = 0, 0

    updated_actions = gen_update_actions(docs_with_sim_info)
    for idx, (ok, item) in enumerate(helpers.streaming_bulk(
            es_client, updated_actions, yield_ok=True, chunk_size=CHUNK_SIZE, request_timeout=1200)):
        if not ok:
            failed_count += 1
        else:
            success_count += 1

        if DOC_COUNT % CHUNK_SIZE == 0:
            logger.info('***[Indexed success] / total: %d/%d' % (success_count, idx + 1))
            logger.info('---------------------------------------')

    logger.info('***[Indexed success] / total: %d/%d' % (success_count, success_count + failed_count))


def main():
    from_date = datetime.strptime(FROM_DATE, "%Y-%m-%d")

    while from_date < datetime.strptime(TO_DATE, "%Y-%m-%d"):
        docs = scan_docs(from_date, from_date)
        docs_with_sim_status = check_sim(docs)
        update_docs(docs_with_sim_status)

        from_date = from_date + timedelta(days=1)


if __name__ == '__main__':
    es_client = Elasticsearch()

    """Update your ES index configs HERE"""
    INDEX_NAME = 'news_index'
    DOC_TYPE = 'news_doc_type'
    FROM_DATE = "2015-09-01"
    TO_DATE = "2016-09-01"

    CHUNK_SIZE = 1000
    DOC_COUNT = 0
    SIM_COUNT = 0
    GROUP_COUNT = 0

    logger = get_logger("check-sim")

    kv_storage = RedisStorage()
    kv_storage.delete('hash2doc')
    kv_storage.delete('doc2sim')

    hasher = MinhashLSH(dim=100, threshold=0.9, length=20)
    preprocessor = SimplePreprocessor()
    stream_sim_checker = StreamClustering(hasher, kv_storage)
    main()
