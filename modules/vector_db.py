#!/usr/bin/env python3

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from modules.logger import get_logger
from modules.button_helpers import BUTTON_TEXTS
logger = get_logger(__name__)

BUTTON_RESULTS_SIZE = 2 # total number of buttons to display minus 1 for the proceed button

class Vectordb:
    def __init__(self, openai_api_key, documents, ids=None):
        self.embedding_function = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.db = Chroma.from_documents(documents, self.embedding_function, ids=ids)

    def search(self, query, k=BUTTON_RESULTS_SIZE):
        retrieved_docs = self.db.similarity_search_with_score(query, k)
        return retrieved_docs
    
    def save(self, docs):
        self.db.add_documents(docs)

def create_button_documents():
    button_docs = [Document(page_content=button, metadata={"source": "local"}) for button in BUTTON_TEXTS]
    return button_docs, BUTTON_TEXTS

