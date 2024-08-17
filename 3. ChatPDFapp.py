from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
import os


@st.cache_resource(ttl="1h", show_spinner='Processing File...')        
def get_retriever_from_file(filepath, HF_Embed_Model):
    try:
        pdf_docs = PyPDFLoader(filepath).load()
        split_docs=RecursiveCharacterTextSplitter(chunk_size=1500,chunk_overlap=150).split_documents(pdf_docs)
        embeddings = HuggingFaceEmbeddings(model_name = HF_Embed_Model)
        db = FAISS.from_documents(split_docs, embeddings)
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    except Exception as e:
        st.write(e)
    return retriever

@st.cache_resource(ttl="1h")
def get_rag_LCEL_chain(model, groq_api_key):
    prompt_template = """
    Answer the below question using only the provide context.
    Question:
    {question}

    Context:
    {context}
    """
    prompt = ChatPromptTemplate.from_messages([("human", prompt_template)])
    llm_model = ChatGroq(model=model,groq_api_key=groq_api_key)
    parser = StrOutputParser()
    rag_chain = prompt|llm_model|parser
    return rag_chain

def save_file(file):
    filepath = file.name
    with open(filepath, "wb") as f:
       f.write(file.getvalue())

    return filepath


def remove_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)


def get_response (file, HF_Embed_Model, LLM_Model, groq_api_key, query):
        file_path = save_file(file)
        retriever = get_retriever_from_file(file_path, HF_Embed_Model)
        LEL_chain = get_rag_LCEL_chain(LLM_Model, groq_api_key)
        rag_chain = {"context":retriever,"question":RunnablePassthrough()}|LEL_chain             
        remove_file(file_path) 

        return rag_chain.invoke(query)



# Env variables and global variables
LLM_Model="Gemma2-9b-It"
HF_Embed_Model = "all-MiniLM-L6-v2"
groq_api_key = st.secrets["GROQ_API_KEY"]


# Streamlit UI
st.title("Chat PDF")
st.write(f'<p style="font-size: medium">Chat with PDF using Langchain HuggingFace Groq</p>', unsafe_allow_html=True)

file=st.file_uploader('Choose PDF file', type=['pdf'], accept_multiple_files=False)

if file:
    col1, col2 = st.columns(spec=[8, 1])
    query = col1.text_input(placeholder="Ask your question here", label="Question", label_visibility="collapsed")
    if col2.button('Go ➡️'):
        response = get_response(file, HF_Embed_Model, LLM_Model, groq_api_key, query)
        st.write(response)