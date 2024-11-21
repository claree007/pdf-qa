import os
import uuid
import logging
import traceback
import chromadb

from cfg import Cfg
import chromadb.utils.embedding_functions as embedding_functions

persistent_db_path = Cfg.vector_db_persistent_path

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

class ChromaDB:
    def __init__(self, collection_name, vectorizer_fn):
        self.collection_name = collection_name
        self.chroma_client = chromadb.PersistentClient(path=persistent_db_path)
        self.vectorizer_fn = vectorizer_fn
        self.collection = None

    def get_or_create_collection(self):
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name, 
            embedding_function=embedding_functions.OpenAIEmbeddingFunction(
                api_key=OPENAI_API_KEY,
                model_name=Cfg.embedding_model
            )
        )
        logging.info(f"Created collection {self.collection_name}.")
            
    def drop_collection(self):
        if self.collection is not None:
            self.chroma_client.delete_collection(name=self.collection_name)
            logging.info(f"Collection {self.collection_name} deleted successfully.")
            self.collection = None
        else:
            logging.info("Collection not initialized. Please create a collection first.")
    
    def view_document(self, ids):
        if self.collection is not None:
            try:
                data_objects = self.collection.get(ids=ids)
                return [data_object.properties for data_object in data_objects]
            except:
                logging.error(traceback.format_exc())
                logging.error(f"Document with IDs {ids} not found.")
        else:
            logging.info("Collection not initialized. Please create a collection first.")

    def insert(self, document):
        if self.collection is not None:
            document = str(document)
            document_embedding = self.vectorizer_fn(document)
            doc_id = self.get_uuid()
            self.collection.add(
                documents=[document],
                embeddings=[document_embedding],
                ids=[doc_id]
            )
        else:
            logging.info("Collection not initialized. Please create a collection first.")

    def insert_bulk(self, data, batch_size=Cfg.vector_db_batch_size):
        if self.collection is not None:
            for i in range(0, len(data), batch_size):
                documents = data[i:i+batch_size]
                document_embeddings = self.vectorizer_fn(documents)
                doc_ids = [self.get_uuid() for _ in range(len(documents))]
                self.collection.add(
                    documents=documents,
                    embeddings=document_embeddings,
                    ids=doc_ids
                )
        else:
            logging.info("Collection not initialized. Please create a collection first.")

    def delete_documents(self, ids):
        if self.collection is not None:
            try:
                self.collection.delete(ids=ids)
            except:
                logging.error(traceback.format_exc())
                logging.error(f"Document with IDs {ids} not found.")
        else:
            logging.info("Collection not initialized. Please create a collection first.")

    def get_similar(self, queries, limit=2, **kwargs):
        if self.collection is not None:
            # Encode the query
            query_vectors = self.vectorizer_fn(queries)
            
            response = self.collection.query(
                query_embeddings=query_vectors,
                n_results=limit
            )
            logging.info(f"Retrieved searches: {response}")
            retrieved_documents = []
            for query_result in response['documents']:
                current_query_documents = []
                for d in query_result:
                    current_query_documents.append(d)
                retrieved_documents.append(current_query_documents)

            return retrieved_documents
        
        else:
            logging.info("Collection not initialized. Please create a collection first.")

    def get_uuid(self):
        return uuid.uuid4().hex
