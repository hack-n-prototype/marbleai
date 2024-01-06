import streamlit as st
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

SQL = "SQL"
GRAPH = "graph"
DATA = {
"count the number of transactions for each user": SQL,
"draw a graph with this data": GRAPH,
"draw a graph with transactiondate and quantity": GRAPH,
"which join do you use and why": SQL
}

def init():
    docs = []
    for content, tag in DATA.items():
        docs.append(Document(page_content=content, metadata={"tag": tag}))

    st.session_state.query_type_vector_db = FAISS.from_documents(docs, OpenAIEmbeddings())

    # query_sql = "count the number of transactiosn for each user"
# query_graph = "draw a graph of time and revenue"
# query_follow_up = "what does join mean"
# print(vectordb.similarity_search(query_follow_up, 1))

def get_query_type(query):
    res = st.session_state.query_type_vector_db.similarity_search(query, 1)
    return res[0].metadata["tag"]
