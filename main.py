"""
PROGRAM FLOW:

1. PREPROCESSING:

parsing (/parsing dir) -> embedding (get_embeddings_df in embedding.py) -> generate KG (create_nodes.py)
    I-------------------------------------------------------------------------------I

2. RAG:
query (input main.py) -> embedding (get_embedding_str in embedding.py)-> vector search (neo.py) -> LLM (infer.py) -> response (output main.py)
                                                                                                        I
                                                                                            (query + returned content)
"""



