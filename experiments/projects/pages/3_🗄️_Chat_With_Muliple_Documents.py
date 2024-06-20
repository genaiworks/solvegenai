import streamlit as st 
from utils import *
import constants
from datasets import (
    load_dataset,
)
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
import os
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from langchain.indexes import VectorstoreIndexCreator



# if "Huggingface_API_KEY" not in st.session_state:
#     st.session_state["HuggingFace_API_KEY"] =''
# if "Pinecone_API_KEY" not in st.session_state:
#     st.session_state["Pinecone_API_KEY"] =''
    
st.title(' Chat with multiple documents 🐼')

markdown = """
Web App URL: <https://www.solvegenai.com>
"""
st.sidebar.title("About")
st.sidebar.info(markdown)
img_file = open('images/logo.png', "rb")
img = img_file.read()

logo = img
st.sidebar.image(logo)
st.sidebar.title("Keys 🗝 ")

st.session_state["OPENAI_API_KEY"]=st.sidebar.text_input("What is your OPENAI_API_KEY", type="password")
st.session_state["ASTRA_DB_API_ENDPOINT"]=st.sidebar.text_input("What is your ASTRA_DB_API_ENDPOINT", type="password")
st.session_state["ASTRA_DB_APPLICATION_TOKEN"]=st.sidebar.text_input("What is your ASTRA_DB_APPLICATION_TOKEN", type="password")
st.session_state["ASTRA_DB_KEYSPACE"]=st.sidebar.text_input("What is your ASTRA_DB_KEYSPACE", type="password")
st.session_state["Data_Dir"]=st.sidebar.text_input("Enter Directory Containing Data")

load_dotenv()

# OPENAI_API_KEY=st.session_state["OPENAI_API_KEY"]
# ASTRA_DB_API_ENDPOINT=st.session_state["ASTRA_DB_API_ENDPOINT"]
# ASTRA_DB_APPLICATION_TOKEN=st.session_state["ASTRA_DB_APPLICATION_TOKEN"]
# ASTRA_DB_KEYSPACE=st.session_state["ASTRA_DB_KEYSPACE"]

OPENAI_API_KEY=os.environ.get("OPENAI_API_KEY")
ASTRA_DB_API_ENDPOINT=os.environ.get("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_APPLICATION_TOKEN=os.environ.get("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_KEYSPACE=os.environ.get("ASTRA_DB_KEYSPACE")

    
load_button = st.sidebar.button("Load data to database", key="load_button")

#Captures user input
prompt = st.text_input("How can I help you my friend .💁", key="prompt")
# document_count = st.slider('No of links to return - (0 LOW || 5 HIGH)', 0,5,2, step=1)
submit = st.button("Search") 

embedding = OpenAIEmbeddings()
vstore = AstraDBVectorStore(
    embedding=embedding,
    collection_name="db_collection",
    api_endpoint=ASTRA_DB_API_ENDPOINT,
    token=ASTRA_DB_APPLICATION_TOKEN,
    namespace=ASTRA_DB_KEYSPACE,
    )

if load_button:
    if st.session_state["OPENAI_API_KEY"] != "" and st.session_state["ASTRA_DB_APPLICATION_TOKEN"] != "" :
        
        loader = DirectoryLoader(st.session_state["Data_Dir"])
        splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
        docs = loader.load_and_split(text_splitter=splitter)
        inserted_ids = vstore.add_documents(docs)
        
        st.sidebar.success("Pushing data to astradb done")
        
    else:
        st.sidebar.error("Please enter your OPENAI_API_KEY  and Astra DB key")
    

    
if submit:
    prompt_template = """
    You are an expert "
    Craft thoughtful answers based on this roadmap, mixing and matching existing paths.
    Your responses should be concise and strictly related to the provided context.

    ROADMAP CONTEXT:
    {context}

    QUESTION: {question}

    YOUR ANSWER:"""

    prompt_template = ChatPromptTemplate.from_template(prompt_template)

    llm = ChatOpenAI()


    retriever = vstore.as_retriever(search_kwargs={"k": 3})

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )

    # retrieved_content = chain.invoke("Tell me summary of Retrieval-Augmented Generation for Large Language Models")
    retrieved_content = chain.invoke(prompt)
    st.write(retrieved_content)

    # if st.session_state["Huggingface_API_KEY"] != "" and st.session_state["Pinecone_API_KEY"] != "" :
    #     index_name="testindex"
    #     #Create embedding instance
    #     embeddings = create_embeddings()
    #     st.write("Embedding instance creation done")
        
    #     # Pull index data from pinecone
    #     index = pull_from_pinecone( embeddings,index_name)
    #     st.write("Pinecone index retrieval done")
        
    #     # Fetch relevant document from pinecone
    #     query=prompt
    #     k=document_count
    #     relevant_docs = similar_docs(index, query, k)
    #     st.write(relevant_docs)
        
    #     for i, doc in enumerate(relevant_docs):
    #         st.write(" ** Result **" + str(relevant_docs.index(doc) + 1))
    #         st.write(" ** info ** " + doc[0].page_content)
    #         st.write(" ** link ** " + doc[0].metadata['source'])
        
        
    st.success("Please find the search results : ")
        
