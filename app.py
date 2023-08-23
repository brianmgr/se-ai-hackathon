# 2023 SE AI Hackathon
# Hosted by Rob Masson and Brian Mgrdichian. Special thanks to Pooja Srinath!

# Original code based on Lizzie Siegle's blog at https://www.twilio.com/blog/qa-over-docs-bot-langchain-python
# Unused code has been commented out, but left for context.


# import requests
import nltk
import ssl

# Added NLTK Punkt package for handling SSL with PDF retrieval
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('punkt', quiet=True)

# from langchain.document_loaders import TextLoader # use this with the loadPDFFromURL function
# from langchain.document_loaders import OnlinePDFLoader # use this with the loadPDFFromURL function
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain import HuggingFaceHub
from flask import Flask, request#, redirect
from twilio.twiml.messaging_response import MessagingResponse

# No longer using this function. Created a function for loading a PDF below instead
# def loadFileFromURL(text_file_url): #param: https://raw.githubusercontent.com/elizabethsiegle/qanda-langchain-sms-lougehrig/main/lougehrig.txt
#     output_file = "lougehrig.txt"
#     resp = requests.get(text_file_url)
#     with open(output_file, "w",  encoding='utf-8') as file:
#       file.write(resp.text)

#     # load text doc from URL w/ TextLoader
#     loader = TextLoader('./'+output_file)
#     txt_file_as_loaded_docs = loader.load()
#     return txt_file_as_loaded_docs

# No longer used- was taking WAY too long to download the PDF every time
# def loadPDFFromURL(pdf_doc):
#     loader = OnlinePDFLoader(pdf_doc)
#     pdf_file_as_loaded_docs = loader.load()
#     return pdf_file_as_loaded_docs

def loadPDFFromFile():
    loader = PyPDFLoader("ctia_short_code_monitoring_handbook_-_v1.8.pdf")
    # pages = loader.load_and_split()
    pdf_file_as_loaded_docs = loader.load()
    return pdf_file_as_loaded_docs

def splitDoc(loaded_docs):
    # split docs into chunks
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
    chunked_docs = splitter.split_documents(loaded_docs)
    return chunked_docs

def makeEmbeddings(chunked_docs):
    # Create embeddings and store them in a FAISS vector store
    embedder = HuggingFaceEmbeddings()
    vector_store = FAISS.from_documents(chunked_docs, embedder)
    return vector_store

def askQs(vector_store, chain, q):
    # Ask a question using the QA chain
    similar_docs = vector_store.similarity_search(q)
    resp = chain.run(input_documents=similar_docs, question=q)
    return resp

def loadLLM():
    llm=HuggingFaceHub(repo_id="declare-lab/flan-alpaca-large", model_kwargs={"temperature":0, "max_length":512})
    chain = load_qa_chain(llm, chain_type="stuff")
    return chain

app = Flask(__name__)
# Adding a route for local testing without SMS: /local
@app.route('/local', methods=['GET', 'POST'])
def local():
    inb_msg = request.form['Body'].lower().strip()
    chain = loadLLM()
    # LOCAL_ldocs = loadFileFromURL('https://raw.githubusercontent.com/elizabethsiegle/qanda-langchain-sms-lougehrig/main/lougehrig.txt')
    # LOCAL_ldocs = loadPDFFromURL('https://www.10dlc.org/ctia_short_code_monitoring_handbook_-_v1.8.pdf')
    LOCAL_ldocs = loadPDFFromFile()
    LOCAL_cdocs = splitDoc(LOCAL_ldocs) #chunked
    LOCAL_vector_store = makeEmbeddings(LOCAL_cdocs)
    LOCAL_resp = askQs(LOCAL_vector_store, chain, inb_msg)
    return str(LOCAL_resp)

# SMS endpoint: /sms
@app.route('/sms', methods=['GET', 'POST'])
def sms():
    resp = MessagingResponse()
    inb_msg = request.form['Body'].lower().strip()
    chain = loadLLM()
    # LOCAL_ldocs = loadFileFromURL('https://raw.githubusercontent.com/elizabethsiegle/qanda-langchain-sms-lougehrig/main/lougehrig.txt')
    # LOCAL_ldocs = loadPDFFromURL('https://www.10dlc.org/ctia_short_code_monitoring_handbook_-_v1.8.pdf')
    LOCAL_ldocs = loadPDFFromFile()
    LOCAL_cdocs = splitDoc(LOCAL_ldocs) #chunked
    LOCAL_vector_store = makeEmbeddings(LOCAL_cdocs)
    LOCAL_resp = askQs(LOCAL_vector_store, chain, inb_msg)
    resp.message(LOCAL_resp)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, port=8001)
