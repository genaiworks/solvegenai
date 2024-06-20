from dotenv import load_dotenv
import streamlit as st 
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.messages import AIMessage,HumanMessage
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import base64

def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)


def init_database(user:str, password:str, host:str, port:str, database:str) ->SQLDatabase:
    db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return SQLDatabase.from_uri(db_uri)

def get_response(user_query: str, db:SQLDatabase, chat_history:str):
    sql_chain = get_sql_chain(st.session_state.db)
    
    template = """
        You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
        Based on the table schema below, question, sql query, and sql response, write a natural language response.
        <SCHEMA>{schema}</SCHEMA>

        Conversation History: {chat_history}
        SQL Query: <SQL>{query}</SQL>
        User question: {question}
        SQL Response: {response}"""
        
    prompt = ChatPromptTemplate.from_template(template)
    
    
    
    # llm = ChatOpenAI(model="gpt-3.5-turbo")
    
    llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
    # chain = (
    #     RunnablePassthrough.assign(query=sql_chain).assign(
    #         schema=lambda _: db.get_table_info(),
    #         response= lambda vars: print("variables   ===>: ", vars)
    #         # response= lambda vars: db.run(vars["query"]),
    #     )
    #     | prompt
    #     | llm
    #     | StrOutputParser()
    # )
    chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
            schema=lambda _: db.get_table_info(),
            response= lambda vars: db.run(vars["query"]),
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
    })
    

def get_sql_chain(db):
    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
    
    <SCHEMA>{schema}</SCHEMA>
    
    Conversation History: {chat_history}
    
    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
    
    For example:
    Question: which 3 artists have the most tracks?
    SQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
    Question: Name 10 artists
    SQL Query: SELECT Name FROM Artist LIMIT 10;
    
    Your turn:
    
    Question: {question}
    SQL Query:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
    
    # llm = ChatOpenAI(model="gpt-3.5-turbo")
    
    def get_schema(_):
        return db.get_table_info()
    
    return(
        RunnablePassthrough.assign(schema=get_schema)
        | prompt 
        | llm
        | StrOutputParser()
    )
    

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content= "Hello I am database assistant.  Ask me anything about your database."),
    ]
    
    

load_dotenv()
st.set_page_config(page_title="Chat with Database 🤖", page_icon=":speech_balloon:")
load_css()

markdown = """
Web App URL: <https://www.solvegenai.com>
"""
st.sidebar.title("About")
st.sidebar.info(markdown)
img_file = open('images/logo.png', "rb")
img = img_file.read()

logo = img
st.sidebar.image(logo)


# with open('univ1-modified.jpeg', "rb") as image_file:
#     encoded_string = base64.b64encode(image_file.read())
#     st.markdown(
#     f"""
#     <style>
#     .stApp {{
#         overflow:hidden;
#         background-image: url(data:image/{"jpeg"};base64,{encoded_string.decode()});
#         background-size:cover;
#     }}
#     </style>
#     """,
#     unsafe_allow_html=True
#     )
st.title("Chat with Database 🐼 ")

with st.sidebar:
    st.subheader("Settings")
    st.write("This is simple chat application using MySQL.  Connect the database and start chatting")
    st.text_input("Host", value="localhost", key="Host")
    st.text_input("Port", value="3306", key="Port")
    st.text_input("User", value="root",key="User")
    st.text_input("Password", type="password", value="pass", key="Password")
    st.text_input("Database", value="Chinook", key="Database")
    
    if st.button("Connect"):
        with st.spinner("Connecting to the database"):
            db = init_database(
                st.session_state["User"],
                st.session_state["Password"],
                st.session_state["Host"],
                st.session_state["Port"]
                ,st.session_state["Database"],)
            st.session_state.db = db
            st.success("Successfully connected to database")
        
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Type here to chat with the database")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)
            
    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)
    
    st.session_state.chat_history.append(AIMessage(content=response))
