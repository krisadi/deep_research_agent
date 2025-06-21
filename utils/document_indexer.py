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

    def process_pdf(self, pdf_file_stream: io.BytesIO, pdf_name: str, pdf_type: str = "Unknown") -> List[LangchainDocument]:
        """
        Processes a single PDF file: extracts text using PyPDF2,
        chunks it, and prepares Langchain Document objects.
        
        Args:
            pdf_file_stream: The PDF file stream
            pdf_name: Name of the PDF file
            pdf_type: Type/category of the PDF content (e.g., "Patient_Data", "Research_Paper")
        """
        print(f"Processing PDF (text-only extraction): {pdf_name} (Type: {pdf_type})")
        
        # 1. Direct text extraction using PyPDF2 with page tracking
        extracted_text, page_mapping = self._extract_text_from_pdf_pypdf2_with_pages(pdf_file_stream, pdf_name)

        if not extracted_text.strip():
            print(f"No text could be extracted from '{pdf_name}' using PyPDF2.")
            return []

        # 2. Chunking the text
        print(f"Chunking text from '{pdf_name}' (total {len(extracted_text)} chars)...")
        text_chunks = self.text_splitter.split_text(extracted_text)
        
        langchain_docs = []
        for i, chunk_content in enumerate(text_chunks):
            # Determine which page this chunk comes from
            chunk_start = sum(len(chunk) for chunk in text_chunks[:i])
            chunk_end = chunk_start + len(chunk_content)
            
            # Find the page that contains the majority of this chunk
            page_number = self._find_page_for_chunk(chunk_start, chunk_end, page_mapping)
            
            metadata = {
                "source": pdf_name,
                "chunk_number": i + 1,
                "total_chunks": len(text_chunks),
                "page_number": page_number,
                "pdf_type": pdf_type,  # Add PDF type to metadata
            }
            doc = LangchainDocument(page_content=chunk_content, metadata=metadata)
            langchain_docs.append(doc)
        
        print(f"Created {len(langchain_docs)} Langchain Document chunks for '{pdf_name}' (Type: {pdf_type}).")
        return langchain_docs

    def _extract_text_from_pdf_pypdf2_with_pages(self, pdf_file_stream: io.BytesIO, pdf_name: str) -> tuple[str, List[tuple[int, int, int]]]:
        """
        Extracts text directly using PyPDF2 with page tracking.
        Returns (full_text, page_mapping) where page_mapping contains (page_num, start_pos, end_pos)
        """
        text_parts = []
        page_mapping = []
        current_pos = 0
        
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
                    # Record the position range for this page
                    start_pos = current_pos
                    end_pos = current_pos + len(page_text)
                    page_mapping.append((page_num + 1, start_pos, end_pos))  # page_num + 1 for 1-based indexing
                    current_pos = end_pos + 1  # +1 for the newline character
            
            if not text_parts and len(reader.pages) > 0:
                print(f"Warning: PyPDF2 extracted no text from '{pdf_name}' which has {len(reader.pages)} page(s). "
                      "The PDF might be image-based or have non-standard text encoding.")
            elif text_parts:
                 print(f"PyPDF2 extracted text from {len(text_parts)} page(s) in '{pdf_name}'.")
            return "\n".join(text_parts), page_mapping
        except Exception as e:
            print(f"Error during PyPDF2 text extraction for '{pdf_name}': {e}")
            return "", []

    def _find_page_for_chunk(self, chunk_start: int, chunk_end: int, page_mapping: List[tuple[int, int, int]]) -> int:
        """
        Determines which page a chunk belongs to based on its position in the text.
        Returns the page number (1-based) that contains the majority of the chunk.
        """
        if not page_mapping:
            return 1  # Default to page 1 if no mapping available
        
        # Find the page that contains the majority of this chunk
        chunk_center = (chunk_start + chunk_end) // 2
        
        for page_num, start_pos, end_pos in page_mapping:
            if start_pos <= chunk_center <= end_pos:
                return page_num
        
        # If no exact match, find the closest page
        closest_page = 1
        min_distance = float('inf')
        
        for page_num, start_pos, end_pos in page_mapping:
            # Calculate distance to page center
            page_center = (start_pos + end_pos) // 2
            distance = abs(chunk_center - page_center)
            if distance < min_distance:
                min_distance = distance
                closest_page = page_num
        
        return closest_page

if __name__ == '__main__':
    print("\n--- Testing DocumentIndexer (No OCR) ---")
    indexer = DocumentIndexer(chunk_size=500, chunk_overlap=50)

    sample_pdf_path = "sample.pdf" # Ensure you have a TEXT-BASED sample.pdf for this test
    try:
        with open(sample_pdf_path, "rb") as f:
            pdf_bytes_io = io.BytesIO(f.read())
            print(f"\n--- Attempting to process '{sample_pdf_path}' (text-based extraction only) ---")
            
            # Test with PDF type
            documents = indexer.process_pdf(pdf_bytes_io, sample_pdf_path, pdf_type="Test_Data")
            
            if documents:
                print(f"\nSuccessfully processed '{sample_pdf_path}' into {len(documents)} chunks.")
                if len(documents) > 0:
                    print("First chunk metadata:", documents[0].metadata)
                    print("First chunk content (first 100 chars):", documents[0].page_content[:100] + "...")
                    # Verify PDF type is in metadata
                    if 'pdf_type' in documents[0].metadata:
                        print(f"PDF Type correctly set: {documents[0].metadata['pdf_type']}")
                    else:
                        print("Warning: PDF type not found in metadata")
            else:
                print(f"Processing '{sample_pdf_path}' yielded no document chunks. Ensure it's a text-based PDF.")

    except FileNotFoundError:
        print(f"\nTEST SKIPPED: '{sample_pdf_path}' not found. Place a sample text-based PDF for testing.")
    except Exception as e:
        print(f"\nAn unexpected error occurred during the test for '{sample_pdf_path}': {e}")

    print("\n--- DocumentIndexer (No OCR) tests complete ---")
