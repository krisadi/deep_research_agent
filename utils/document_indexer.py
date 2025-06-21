import PyPDF2
import io
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document as LangchainDocument # Alias to avoid confusion
from typing import List

class DocumentIndexer:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        """
        Initializes the DocumentIndexer.

        Args:
            chunk_size (int): The target size for text chunks (in characters).
            chunk_overlap (int): The overlap between consecutive chunks (in characters).
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=False, 
        )
        print(f"DocumentIndexer initialized with chunk_size={chunk_size}, chunk_overlap={chunk_overlap} (OCR capabilities removed).")

    def _extract_text_from_pdf_pypdf2(self, pdf_file_stream: io.BytesIO, pdf_name: str) -> str:
        """Extracts text directly using PyPDF2."""
        text_parts = []
        try:
            pdf_file_stream.seek(0) # Reset stream position
            reader = PyPDF2.PdfReader(pdf_file_stream)
            if reader.is_encrypted:
                try:
                    reader.decrypt('') # Try with empty password, common for some PDFs
                except Exception as e_decrypt:
                    print(f"Could not decrypt PDF '{pdf_name}': {e_decrypt}. Text extraction will likely fail or be incomplete.")
                    # Fall through, extraction might still get some metadata or fail gracefully
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            if not text_parts and len(reader.pages) > 0:
                print(f"Warning: PyPDF2 extracted no text from '{pdf_name}' which has {len(reader.pages)} page(s). "
                      "The PDF might be image-based or have non-standard text encoding.")
            elif text_parts:
                 print(f"PyPDF2 extracted text from {len(text_parts)} page(s) in '{pdf_name}'.")
            return "\n".join(text_parts)
        except Exception as e:
            print(f"Error during PyPDF2 text extraction for '{pdf_name}': {e}")
            return ""

    def process_pdf(self, pdf_file_stream: io.BytesIO, pdf_name: str) -> List[LangchainDocument]:
        """
        Processes a single PDF file: extracts text using PyPDF2,
        chunks it, and prepares Langchain Document objects.
        """
        print(f"Processing PDF (text-only extraction): {pdf_name}")
        
        # 1. Direct text extraction using PyPDF2
        extracted_text = self._extract_text_from_pdf_pypdf2(pdf_file_stream, pdf_name)

        if not extracted_text.strip():
            print(f"No text could be extracted from '{pdf_name}' using PyPDF2.")
            return []

        # 2. Chunking the text
        print(f"Chunking text from '{pdf_name}' (total {len(extracted_text)} chars)...")
        text_chunks = self.text_splitter.split_text(extracted_text)
        
        langchain_docs = []
        for i, chunk_content in enumerate(text_chunks):
            metadata = {
                "source": pdf_name,
                "chunk_number": i + 1,
                "total_chunks": len(text_chunks),
            }
            doc = LangchainDocument(page_content=chunk_content, metadata=metadata)
            langchain_docs.append(doc)
        
        print(f"Created {len(langchain_docs)} Langchain Document chunks for '{pdf_name}'.")
        return langchain_docs

if __name__ == '__main__':
    print("\n--- Testing DocumentIndexer (No OCR) ---")
    indexer = DocumentIndexer(chunk_size=500, chunk_overlap=50)

    sample_pdf_path = "sample.pdf" # Ensure you have a TEXT-BASED sample.pdf for this test
    try:
        with open(sample_pdf_path, "rb") as f:
            pdf_bytes_io = io.BytesIO(f.read())
            print(f"\n--- Attempting to process '{sample_pdf_path}' (text-based extraction only) ---")
            
            documents = indexer.process_pdf(pdf_bytes_io, sample_pdf_path)
            
            if documents:
                print(f"\nSuccessfully processed '{sample_pdf_path}' into {len(documents)} chunks.")
                if len(documents) > 0:
                    print("First chunk metadata:", documents[0].metadata)
                    print("First chunk content (first 100 chars):", documents[0].page_content[:100] + "...")
            else:
                print(f"Processing '{sample_pdf_path}' yielded no document chunks. Ensure it's a text-based PDF.")

    except FileNotFoundError:
        print(f"\nTEST SKIPPED: '{sample_pdf_path}' not found. Place a sample text-based PDF for testing.")
    except Exception as e:
        print(f"\nAn unexpected error occurred during the test for '{sample_pdf_path}': {e}")

    print("\n--- DocumentIndexer (No OCR) tests complete ---")
