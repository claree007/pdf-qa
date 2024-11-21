import io
import base64
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from cfg import Cfg
from db.chroma_db import ChromaDB
from utils.logger import init_logger
from parsers.pdf_reader import PyPDFReader
from utils.text_preprocessing import TextPreprocessing
from llms.openai_llm import OpenAILLM, OpenAIEmbeddings
from parsers.json_handler import extract_json, handle_md_json

vector_db = None
reader = None
text_preprocessor = None
llm = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global vector_db, reader, text_preprocessor, llm

    init_logger()
    embeddings = OpenAIEmbeddings(model=Cfg.embedding_model)
    llm = OpenAILLM(model=Cfg.openai_model)
    vector_db = ChromaDB(
        collection_name=Cfg.vector_db_collection_name, 
        vectorizer_fn=embeddings.get_embeddings
    )
    vector_db.get_or_create_collection()

    text_preprocessor = TextPreprocessing()
    reader = PyPDFReader(text_preprocessor=text_preprocessor)
    yield

app = FastAPI(lifespan=lifespan)

# Allow requests from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.post("/parse")
async def parse_document(payload: dict):
    logging.info("Ingesting document")
    try:
        document = payload['document']
        document = base64.b64decode(document)
        document = io.BytesIO(document)
    except Exception as e:
        logging.error(f"No document path provided: {e}")
        return {"error": "Please provide a document path"}
    
    try:
        extracted_text = reader.process_document(document)
    except Exception as e:
        logging.error(f"Error extracting text from document: {e}")
        return {"error": "Error extracting text from document"}
    
    formatted_text = text_preprocessor.process_text(extracted_text)

    return {"extracted_text": formatted_text}

@app.post("/chunking")
def document_chunking(payload: dict):
    document = payload['document']
    text_list = text_preprocessor.split_text(document)
    return {"text_list": text_list}

@app.post("/vector_db/create_collection")
def create_collection():
    vector_db.get_or_create_collection()
    return {"message": "Collection created successfully."}

@app.post("/vector_db/delete_collection")
def delete_collection():
    vector_db.drop_collection()
    return {"message": "Collection deleted successfully."}

@app.post("/vector_db/insert")
def insert(payload: dict):
    data = payload['data']
    vector_db.insert(data=data)
    return {"message": "Data inserted successfully."}

@app.post("/vector_db/insert_bulk")
def insert_bulk(payload: dict):
    data = payload['data']
    vector_db.insert_bulk(data=data)
    return {"message": "Data inserted successfully."}

@app.post("/vector_db/get_similar")
def get_similar(payload: dict):
    queries = payload['queries']
    limit = payload.get('limit', Cfg.limit)
    response = vector_db.get_similar(queries=queries, limit=limit)
    return {"response": response}

@app.post("/document_chat")
def chat(payload: dict):
    questions = payload.get("questions")

    if not questions:
        return {"error": "Please provide questions to be asked."}
  
    query_answers = get_similar({"queries": questions, "limit": 3})
    query_answers = query_answers["response"]

    # pass the retrieved answers to the LLM for each query
    responses = []
    for i, query in enumerate(questions):
        context = "\n\n".join(query_answers[i])
        user_message = f"Context:\n{context}\n\nUser question:\n{query}"
        response = llm.get_llm_response(
            system_message=Cfg.system_message, 
            user_message=user_message, 
        )
        try:
            extracted_response = extract_json(response)["answer"]
        except:
            extracted_response = handle_md_json(response)
            if not extracted_response:
                extracted_response = response
            else:
                extracted_response = extracted_response["answer"]

        responses.append(extracted_response)
    
    result = dict(zip(questions, responses))
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=Cfg.app_host, port=Cfg.app_port)