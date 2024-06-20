import streamlit as st

st.set_page_config(
    page_title="SolveGenAI Application",
    page_icon="👋",
)

st.title("Welcome to SloveGenAI")
st.sidebar.success("Please select documentation search or database search")

if "doc_db_search" not in st.session_state:
    st.session_state["doc_db_search"] = ""

doc_db_search = st.text_input("Start Chat Here", st.session_state["doc_db_search"])
submit = st.button("Submit")
if submit:
    st.session_state["doc_db_search"] = doc_db_search
    st.write("You have entered: ", doc_db_search)