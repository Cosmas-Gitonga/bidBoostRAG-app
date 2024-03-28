import streamlit as st
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from get_pdf_text import get_pdf_text
from get_text_chunks import get_text_chunks
from get_vector_store import get_vector_store
from get_converstation_chain import get_conversation_chain
from file_converter import file_converter
from upload_files import upload_files
from create_folder import create_folder
from pdf_data_store import pdf_token_pages
import pandas as pd
import numpy as np
import time

from htmlTemplates import css, bot_template, user_template
import os

def handle_user_question(user_question):
        st.session_state.response = st.session_state.conversation({"question": user_question})
        st.session_state.chat_history = st.session_state.response['chat_history']

        for i,message in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
                st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
def handle_history():
    if st.session_state.chat_history:
        for i,message in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
                st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

def handle_clear_chat():
    st.session_state.response = None
    st.session_state.chat_history = None
    



def main():
    UPLOAD_DIRECTORY = 'docs/proposals/'

    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    loaded_pdfs = [os.path.join(UPLOAD_DIRECTORY, fname) for fname in os.listdir(UPLOAD_DIRECTORY)]
    load_dotenv()
    st.set_page_config(page_title="BidBoost RAG", page_icon=":books")
    
    st.write(css, unsafe_allow_html=True)
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "response" not in st.session_state:
        st.session_state.response = None
    if "embeddings_meta_df":
        st.session_state.embeddings_meta_df = None

    st.header("BidBoost RAG 👽")
    st.subheader("Proposals Information Retriever")

    user_question = st.text_input("What would you like to retrieve?")
    if st.button('Clear chat'):
        handle_clear_chat()
        user_question = ''

    if user_question:
        try:
            handle_user_question(user_question)
        except:
            st.warning("Please upload and process proposals", icon='⚠️')
    elif user_question == '' :
        handle_history()

    with st.sidebar:
        st.subheader("Proposals")
        if st.checkbox("Manage Collections"):
            st.header("Manage Proposal Documents")
            collections = ["Collection 1", "Collection 2"]  # Define your collections
            for collection in collections:
                with st.expander(f"Manage {collection}"):
                    create_folder_button = st.button(f"Create {collection} Folder", key=f"create_{collection}")
                    if create_folder_button:
                        create_folder(collection)
                    upload_files(collection)

        pdf_docs = st.file_uploader("Upload Proposals Here and Click Process", accept_multiple_files=True)
        if st.button("process"):
            with st.spinner("Processing"):
                # save pdf files
                loaded_pdfs = file_converter(pdf_docs, UPLOAD_DIRECTORY)
                # get pdf text
                sources, raw_docs, page_contents = get_pdf_text(loaded_pdfs)
                
                #generate token data
                pdf_data = pdf_token_pages(loaded_pdfs)
                pdf_df = pd.DataFrame(pdf_data)
                pdf_df.to_csv('data/viz.csv', index=False)

                #save pdfs data
                df_info_data = pd.DataFrame({
                    'Source': sources,
                    'Document': raw_docs,
                    'Page Content': page_contents
                })

                df_info_data.to_csv('data/pdf_info_data.csv', index=False)

                # get the text chunks
                token_chunks = get_text_chunks(raw_docs)
    
                # create vectore store
                vector_store = get_vector_store(token_chunks)

            
                #create conversation chain
                st.session_state.conversation = get_conversation_chain(vector_store)
                
                # Retrieve embeddings from the vector store
                
                if st.session_state.conversation:
                    st.session_state.response = vector_store.get(include=["metadatas", "documents", "embeddings"])
                    # st.write('response',st.session_state.response)
                    st.session_state.embeddings_meta_df = pd.DataFrame(
                        {
                            "id": st.session_state.response["ids"],
                            "source": ["none" if metadata is None else metadata["source"] for metadata in st.session_state.response["metadatas"]]
,
                            "document": st.session_state.response["documents"],
                            "embedding": st.session_state.response["embeddings"],
                        }
                    )
                    # st.write('response',st.session_state.embeddings_meta_df)
                st.success('Proposals Succesfully Processed!', icon="✅")
                
                    
    # Function to embed query and compute distances
   
    def embed_and_compute_distances(user_question, embeddings_meta_df):
        if user_question and st.session_state.conversation:
            # Embed user question
            embedding = OpenAIEmbeddings()
            question_embedding = embedding.embed_query(user_question)
            
            # Compute distances
            st.session_state.embeddings_meta_df["dist"] = st.session_state.embeddings_meta_df.apply(
                lambda row: np.linalg.norm(
                    np.array(row["embedding"]) - question_embedding
                ),
                axis=1,
            )
            
            # Save dataframe to CSV
            st.session_state.embeddings_meta_df.to_csv('data/response_data.csv')
     
    if st.session_state.conversation == True:
        st.session_state.embeddings_meta_df = pd.DataFrame(
                            {
                                "id": st.session_state.response["ids"],
                                "source": ["none" if metadata is None else metadata["source"] for metadata in st.session_state.response["metadatas"]]
    ,
                                "document": st.session_state.response["documents"],
                                "embedding": st.session_state.response["embeddings"],
                            }
                        )
        # st.write('response',st.session_state.embeddings_meta_df)
        embed_and_compute_distances(user_question, st.session_state.embeddings_meta_df)
            
    else:
        time.sleep(5)
    # while True:
    #     if st.session_state.conversation == True:
    #         st.session_state.embeddings_meta_df = pd.DataFrame(
    #                             {
    #                                 "id": st.session_state.response["ids"],
    #                                 "source": ["none" if metadata is None else metadata["source"] for metadata in st.session_state.response["metadatas"]]
    #     ,
    #                                 "document": st.session_state.response["documents"],
    #                                 "embedding": st.session_state.response["embeddings"],
    #                             }
    #                         )
    #         # st.write('response',st.session_state.embeddings_meta_df)
    #         embed_and_compute_distances(user_question, st.session_state.embeddings_meta_df)
    #         break
    #     else:
    #         time.sleep(5)

        # if user_question and st.session_state.embeddings_meta_df.sample()[0] != None:
        #     embed_and_compute_distances(user_question, st.session_state.embeddings_meta_df)

    # Continuously check for user input and process when available
    # while True:
    #     st.write(st.session_state.embeddings_meta_df)
    #     if user_question and st.session_state.embeddings_meta_df.sample()[0] != None:
    #         embed_and_compute_distances(user_question, st.session_state.embeddings_meta_df)
    #         break
    #     else:
    #         time.sleep(1) 
    
    


if __name__ == '__main__':
    main()