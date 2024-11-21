class Cfg:
    # app
    app_host = "0.0.0.0"
    app_port = 8000
    logging_file_path = '/Users/ubuntu/Documents/logs/run.log'

    # vector db
    vector_db_collection_name = "zania_collection"
    vector_db_persistent_path = "/Users/ubuntu/Documents/persistent_db"
    vector_db_batch_size = 30
    limit = 2

    # embeddings
    embedding_model = "text-embedding-3-small"

    # Data ingestion
    chunk_size = 1000
    chunk_overlap = 100
    document_storage_path = "/Users/ubuntu/Documents/"

    # llm
    openai_model = "gpt-4o-mini"
    system_message = """You need to answer user questions based on the provided context. Provide your output as JSON as follows:\n{"answer": "your answer here"}\n\nIf the answer is not in the provided context, provide the JSON response as follows:\n{"answer": "Data Not Available"}"""