# This module will abstract vector database operations (initially FAISS).
from langchain.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.docstore.document import Document as LangchainDocument
from typing import List, Optional, Any, Dict

# Using a common open-source embedding model
DEFAULT_EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

class VectorStoreHandler:
    def __init__(self, embedding_model_name: str = DEFAULT_EMBEDDING_MODEL):
        """
        Initializes the VectorStoreHandler.

        Args:
            embedding_model_name (str): The name of the Sentence Transformer model to use for embeddings.
        """
        try:
            self.embedding_model = SentenceTransformerEmbeddings(model_name=embedding_model_name)
            print(f"VectorStoreHandler initialized with embedding model: {embedding_model_name}")
        except Exception as e:
            print(f"Error initializing SentenceTransformerEmbeddings with model '{embedding_model_name}': {e}")
            print("Ensure the model name is correct and you have an internet connection "
                  "if the model needs to be downloaded for the first time.")
            raise # Re-raise the exception to halt initialization if embeddings can't be loaded.
            
        self.vector_store: Optional[FAISS] = None # FAISS index will be created/loaded when documents are added

    def init_store_from_documents(self, documents: List[LangchainDocument]):
        """
        Initializes or re-initializes the FAISS vector store from a list of Langchain Documents.
        If a store already exists, it will be replaced.

        Args:
            documents (List[LangchainDocument]): A list of Langchain Document objects (chunks).
        """
        if not documents:
            print("No documents provided to initialize the vector store. Store remains uninitialized.")
            self.vector_store = None
            return

        try:
            print(f"Initializing FAISS vector store with {len(documents)} document chunks...")
            # This will compute embeddings for the documents and build the FAISS index.
            self.vector_store = FAISS.from_documents(documents, self.embedding_model)
            print("FAISS vector store initialized successfully.")
        except Exception as e:
            print(f"Error creating FAISS vector store from documents: {e}")
            self.vector_store = None # Ensure store is None on failure


    def add_documents_to_store(self, documents: List[LangchainDocument]):
        """
        Adds new documents to an existing FAISS vector store.
        If the store doesn't exist, it initializes it with these documents.

        Args:
            documents (List[LangchainDocument]): A list of Langchain Document objects.
        """
        if not documents:
            print("No documents provided to add to the vector store.")
            return

        if self.vector_store is None:
            print("Vector store not yet initialized. Initializing with provided documents.")
            self.init_store_from_documents(documents)
        else:
            try:
                print(f"Adding {len(documents)} new document chunks to existing FAISS store...")
                # FAISS.add_documents handles embedding the new documents
                self.vector_store.add_documents(documents)
                print(f"{len(documents)} documents added successfully to FAISS store.")
            except Exception as e:
                print(f"Error adding documents to existing FAISS store: {e}")
                # Depending on the error, the store might be in an inconsistent state.
                # For simplicity, we don't try to recover here.

    def search_relevant_chunks(self, query: str, k: int = 5) -> List[LangchainDocument]:
        """
        Performs a similarity search in the vector store for a given query.

        Args:
            query (str): The user query string.
            k (int): The number of top relevant chunks to retrieve.

        Returns:
            List[LangchainDocument]: A list of the most relevant Langchain Document chunks.
                                     Returns an empty list if the store is not initialized or on error.
        """
        if self.vector_store is None:
            print("Vector store is not initialized. Cannot perform search.")
            return []
        
        if not query:
            print("Search query is empty. Returning no results.")
            return []

        try:
            print(f"Performing similarity search for query: '{query}' (top k={k})")
            # The query string will be embedded automatically by FAISS's similarity_search method
            # using the embedding_model provided during its initialization.
            relevant_docs = self.vector_store.similarity_search(query, k=k)
            print(f"Similarity search found {len(relevant_docs)} relevant chunks.")
            return relevant_docs
        except Exception as e:
            print(f"Error during similarity search: {e}")
            return []

    def get_store_status(self) -> Dict[str, Any]:
        """Returns basic status information about the vector store."""
        if self.vector_store is None:
            return {"status": "Not initialized", "num_docs": 0}
        
        # FAISS through Langchain might not directly expose total number of docs easily
        # without `index_to_docstore_id` and `docstore`.
        # This is a proxy, as len(index_to_docstore_id) gives the number of vectors.
        num_docs = len(self.vector_store.index_to_docstore_id) if self.vector_store.index else 0
        return {"status": "Initialized", "num_docs": num_docs, "embedding_model": self.embedding_model.model_name}


if __name__ == '__main__':
    print("\n--- Testing VectorStoreHandler ---")
    
    # 1. Initialize handler
    try:
        handler = VectorStoreHandler()
        print(f"Handler status: {handler.get_store_status()}")
    except Exception as e:
        print(f"Failed to initialize VectorStoreHandler: {e}. This might be due to model download issues.")
        print("Skipping further tests for VectorStoreHandler.")
        exit()


    # 2. Create some dummy Langchain Documents (chunks)
    doc1_content = "Langchain is a framework for developing applications powered by language models."
    doc1_metadata = {"source": "manual_doc1.txt", "chunk_number": 1}
    doc1 = LangchainDocument(page_content=doc1_content, metadata=doc1_metadata)

    doc2_content = "It provides tools for managing prompts, chains, memory, and indexes like vector stores."
    doc2_metadata = {"source": "manual_doc1.txt", "chunk_number": 2}
    doc2 = LangchainDocument(page_content=doc2_content, metadata=doc2_metadata)
    
    doc3_content = "FAISS is a library for efficient similarity search and clustering of dense vectors."
    doc3_metadata = {"source": "manual_doc2.txt", "chunk_number": 1}
    doc3 = LangchainDocument(page_content=doc3_content, metadata=doc3_metadata)

    initial_docs = [doc1, doc2]

    # 3. Initialize store with documents
    print("\n--- Initializing store with first set of documents ---")
    handler.init_store_from_documents(initial_docs)
    print(f"Handler status after init: {handler.get_store_status()}")

    # 4. Perform a search
    query1 = "What is Langchain?"
    print(f"\n--- Searching for: '{query1}' ---")
    results1 = handler.search_relevant_chunks(query1, k=1)
    if results1:
        print(f"Found {len(results1)} result(s):")
        for res_doc in results1:
            print(f"  Source: {res_doc.metadata.get('source')}, Content: '{res_doc.page_content[:50]}...'")
    else:
        print("No results found.")

    # 5. Add more documents
    print("\n--- Adding more documents to the store ---")
    additional_docs = [doc3]
    handler.add_documents_to_store(additional_docs) # This should call `add_documents` on FAISS
    print(f"Handler status after adding docs: {handler.get_store_status()}")

    # 6. Perform another search that should find the new document
    query2 = "Tell me about FAISS"
    print(f"\n--- Searching for: '{query2}' ---")
    results2 = handler.search_relevant_chunks(query2, k=1)
    if results2:
        print(f"Found {len(results2)} result(s):")
        for res_doc in results2:
            print(f"  Source: {res_doc.metadata.get('source')}, Content: '{res_doc.page_content[:50]}...'")
    else:
        print("No results found.")
        
    # 7. Test with empty query
    print("\n--- Searching with empty query ---")
    results_empty_query = handler.search_relevant_chunks("", k=1)
    if not results_empty_query:
        print("Correctly returned no results for empty query.")

    # 8. Test search on uninitialized store (by creating a new handler)
    print("\n--- Testing search on uninitialized store ---")
    handler_new = VectorStoreHandler()
    results_uninit = handler_new.search_relevant_chunks("test", k=1)
    if not results_uninit:
        print("Correctly returned no results for uninitialized store.")
        
    print("\n--- VectorStoreHandler tests complete ---")
