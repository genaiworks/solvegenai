from pinecone import Pinecone, ServerlessSpec
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import pinecone 
import asyncio
from langchain.document_loaders import SitemapLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
import os

def get_website_data(sitemap_url):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loader = SitemapLoader(sitemap_url)
    docs = loader.load()
    return docs

def split_data(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
    docs_chunks = text_splitter.split_documents(docs)
    return docs_chunks

def create_embeddings():
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    return embeddings

def push_to_pinecone(pinecone_api_key, embeddings, index_name,docs):
    # pc = Pinecone(api_key=pinecone_api_key)
    # index = pc.Index(index_name)
    os.environ['PINECONE_API_KEY'] ="9b4609f9-94c6-49cf-ba6f-60f3df37db87"
    index = PineconeVectorStore.from_documents(docs, embeddings, index_name=index_name)
    # print (index.describe_index_stats())
    return index
    
def pull_from_pinecone( embeddings,index_name):
    # pc = Pinecone(api_key=pinecone_api_key)
    os.environ['PINECONE_API_KEY'] = "9b4609f9-94c6-49cf-ba6f-60f3df37db87"
    # index = pc.Index(index_name)
    index = PineconeVectorStore.from_existing_index(index_name, embeddings)
    return index

def similar_docs(index, query, k=2):
    similar_docs = index.similarity_search_with_score(query, int(k))
    print (similar_docs)
    return similar_docs

