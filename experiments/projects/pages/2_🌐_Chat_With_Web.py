import streamlit as st 
from utils import *
import constants


if "Huggingface_API_KEY" not in st.session_state:
    st.session_state["HuggingFace_API_KEY"] =''
if "Pinecone_API_KEY" not in st.session_state:
    st.session_state["Pinecone_API_KEY"] =''
    
st.title(' Chat with websites 🐼')

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

st.session_state['Huggingface_API_KEY']=st.sidebar.text_input("What is your Huggingface_API_KEY", type="password")
st.session_state['Pinecone_API_KEY']=st.sidebar.text_input("What is your Pinecone_API_KEY", type="password")

load_button = st.sidebar.button("Load data to database", key="load_button")

    #Captures user input
prompt = st.text_input("How can I help you my friend .💁", key="prompt")
document_count = st.slider('No of links to return - (0 LOW || 5 HIGH)', 0,5,2, step=1)
submit = st.button("Search") 

if load_button:
    if st.session_state["Huggingface_API_KEY"] != "" and st.session_state["Pinecone_API_KEY"] != "" :
        #fetch data from site
        # sitemap_url ="https://jobs.excelcult.com/wp-sitemap-taxonomies-category-1.xml"
        sitemap_url =constants.WEBSITE_URL
        site_data = get_website_data(sitemap_url)
        # st.write(" Data pull done:")
        
        chunks_data = split_data(site_data)
        # st.write("Splitting data done:")
     
        embeddings = create_embeddings()
        # st.write("Embedding instance creation done:")
        
        pinecone_api_key = st.session_state["Pinecone_API_KEY"]
        index_name="testindex"
        push_to_pinecone(pinecone_api_key, embeddings, index_name,chunks_data)
        # st.write("pushing data to pinecone done")
        
        # st.sidebar.success("Pushing data to pinecone done")
        
    else:
        st.sidebar.error("Please enter your HuggingFace API key and Pinecone API key")
    

    
if submit:
    if st.session_state["Huggingface_API_KEY"] != "" and st.session_state["Pinecone_API_KEY"] != "" :
        index_name="testindex"
        #Create embedding instance
        embeddings = create_embeddings()
        st.write("Embedding instance creation done")
        
        # Pull index data from pinecone
        index = pull_from_pinecone( embeddings,index_name)
        st.write("Pinecone index retrieval done")
        
        # Fetch relevant document from pinecone
        query=prompt
        k=document_count
        relevant_docs = similar_docs(index, query, k)
        st.write(relevant_docs)
        
        for i, doc in enumerate(relevant_docs):
            st.write(" ** Result **" + str(relevant_docs.index(doc) + 1))
            st.write(" ** info ** " + doc[0].page_content)
            st.write(" ** link ** " + doc[0].metadata['source'])
        
        
        st.success("Please find the search results : ")
        
