#!/usr/bin/env python
# coding: utf-8


from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

import streamlit as st
import re


# ## Helper Functions

# Just a helper function to concatenate docs
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def clean_response(response):
    # Remove everything between <think> and </think> tags (including the tags)
    cleaned_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    
    # Remove any leading/trailing whitespace
    cleaned_response = cleaned_response.strip()
    
    return cleaned_response


# # Developing RAG

# ## Loading LLM

# Initialize Ollama with my local model
llm = OllamaLLM(model="deepseek-r1:1.5b")


# ## Loading Data

# Function to load the .docx file
def load_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
    return text

# Load the company manual
text = load_docx('manual.docx')

# Split the text into documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_text(text)


# ## Making vector embeddings & initializing vector store

# Make embeddings
local_embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Make vector store
vectorstore = Chroma.from_texts(all_splits, local_embeddings)

# Make a retriever from the store
retriever = vectorstore.as_retriever()


# ## Developing a chain

# Developing a chain

RAG_TEMPLATE = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Answer only those questions that are present in the context. If nothing is present, then say No information available.

<context>
{context}
</context>

Answer the following question:

{question}"""

rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)

qa_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
    | clean_response
)


# ========================= STREAMLIT APP =========================

def chatbot(query):
    # Get the response from the QA chain
    return qa_chain.invoke(query)

# Streamlit app
st.title("BlueSky Company Manual Chatbot")
st.write("Ask questions about the company's manual.")

# Input for user query
user_input = st.text_input("You: ")

# Chatbot response
if user_input:
    response = chatbot(user_input)
    st.write(f"Chatbot: {response}")