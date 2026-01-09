from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from langgraph.graph import StateGraph,END,START
from typing import TypedDict,List

import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


loader=PyPDFLoader('Collabifyy_Technical_Roadmap_Detailed.pdf')

docs=loader.load()



splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)



split_docs = splitter.split_documents(docs)
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


vectorstore = Chroma.from_documents(
    documents=split_docs,
    embedding=embedding
)


retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 4,
        "fetch_k": 10,
        "lambda_mult": 0.7
    }
)


query = "tell me the objective of this roadmap?"

results = retriever.invoke(query)
context = "\n\n".join(d.page_content for d in results)


model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)


prompt = f"""
You are reading a short technical roadmap.

Extract ONLY the answer to the question below.
Be concise and structured.
Do not repeat unrelated sections.

Context:
{context}

Question:
{query}
"""

response = model.invoke(prompt)
print(response.content)