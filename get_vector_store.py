from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from InstructorEmbedding import INSTRUCTOR
from langchain.vectorstores import FAISS
from langchain.vectorstores import Chroma
import streamlit as st

#creating a directory to store the vector store instance
persist_directory = 'docs/chroma/'

def get_vector_store(token_chunks):
    
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    # vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    # loading intializing chroma with both embeddings and tokens
    vectordb = Chroma.from_documents(
        documents=token_chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    return vectordb
