#!/usr/bin/env python3

from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

doc0 =  Document(page_content="count the number of transactions for each user", metadata={"tag": "SQL"})
doc1 =  Document(page_content="draw a graph with this data", metadata={"tag": "graph"})
doc1 =  Document(page_content="draw a graph with transactiondate and quantity", metadata={"tag": "graph"})
doc2 =  Document(page_content="which join do you use and why", metadata={"tag": "SQL"})


embeddings = OpenAIEmbeddings()
vectordb = FAISS.from_documents([doc0, doc1, doc2], embeddings)

query_sql = "count the number of transactiosn for each user"
query_graph = "draw a graph of time and revenue"
query_follow_up = "what does join mean"
res = vectordb.similarity_search(query_follow_up, 1)
print(res[0].metadata["tag"])