from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
import streamlit as st


def get_conversation_chain(vector_store):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm = llm,
        retriever=vector_store.as_retriever(),
        memory=memory
    )
    return conversation_chain