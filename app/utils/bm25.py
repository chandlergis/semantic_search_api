from typing import List, Dict
import math

class BM25:
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.documents: List[List[str]] = []
        self.avgdl = 0
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_len: List[int] = []

    def add_document(self, document: List[str]):
        pass

    def calculate_idf(self):
        pass

    def search(self, query: List[str], top_n: int = 5) -> List[tuple[int, float]]:
        pass
