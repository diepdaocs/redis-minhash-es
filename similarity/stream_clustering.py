from abc import ABC, abstractmethod

from similarity.io.kv_storage import KVStorage
from similarity.lsh import MinHashSignature, LSH


class Hashing(ABC):
    @abstractmethod
    def hash(self, tokens: list) -> list:
        pass


class MinhashLSH(Hashing):
    def __init__(self, dim=100, threshold=0.9, length=10):
        self.hasher = MinHashSignature(dim)
        self.lsh = LSH(length, threshold)

    def hash(self, tokens):
        sign = self.hasher.sign(tokens)
        hashes = self.lsh.hash(sign)
        return list(hashes)


class StreamClustering:
    def __init__(self, hasher: Hashing, kv_storage: KVStorage):
        self.hasher = hasher
        self.kv_storage = kv_storage
        self.hash2doc = 'hash2doc'
        self.doc2sim = 'doc2sim'

    def find_group(self, doc_id, tokens):
        """
        Find group of the current document
        :param doc_id: the document id
        :param tokens: the tokens of document text
        :return: the group id, if there no group id, the current doc id will be the group id
        """
        group_id = None
        hashes = self.hasher.hash(tokens)
        for hash_str in hashes:
            sim_id = self.kv_storage.get(self.hash2doc, hash_str)
            if not sim_id:
                self.kv_storage.put(self.hash2doc, hash_str, doc_id)
            else:
                if not group_id:
                    group_id = self.kv_storage.get(self.doc2sim, sim_id)
                    if not group_id and group_id != sim_id:
                        group_id = sim_id
                        self.kv_storage.put(self.doc2sim, doc_id, group_id)

        if not group_id:
            group_id = doc_id

        return group_id
