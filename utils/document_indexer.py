import PyPDF2
from PIL import Image
import pytesseract
import io
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document as LangchainDocument # Alias to avoid confusion
from typing import List

# Configure Tesseract path if not in system PATH (optional, depends on installation)
# Example for some environments, adjust as needed or ensure Tesseract is in PATH:
# try:
#     pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' # Common on Linux
# except Exception:
#     try: # Common on macOS if installed via Homebrew
#         pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
#     except Exception:
#          print("Tesseract command path not explicitly set, assuming it's in PATH.")


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
            add_start_index=False, # Keep it simple for now
        )
        print(f"DocumentIndexer initialized with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")

    def _extract_text_from_pdf_pypdf2(self, pdf_file_stream: io.BytesIO, pdf_name: str) -> str:
        """Extracts text directly using PyPDF2."""
        text_parts = []
        try:
            pdf_file_stream.seek(0) # Reset stream position
            reader = PyPDF2.PdfReader(pdf_file_stream)
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            print(f"PyPDF2 extracted text from {len(text_parts)} pages in '{pdf_name}'.")
            return "\n".join(text_parts)
        except Exception as e:
            print(f"Error during PyPDF2 text extraction for '{pdf_name}': {e}")
            return ""

    def _ocr_pdf_page_image(self, page_image: Image.Image, lang: str = 'eng') -> str:
        """Performs OCR on a single PIL Image object."""
        try:
            return pytesseract.image_to_string(page_image, lang=lang)
        except pytesseract.TesseractNotFoundError:
            print("TESSERACT NOT FOUND ERROR: Ensure Tesseract OCR is installed and in your system's PATH, "
                  "or configure pytesseract.pytesseract.tesseract_cmd in document_indexer.py.")
            raise # Re-raise to be caught by the caller and potentially skip OCR for this PDF
        except Exception as e:
            print(f"Error during OCR for a page image: {e}")
            return ""
            
    def _extract_text_with_ocr(self, pdf_file_stream: io.BytesIO, pdf_name: str, pypdf2_text: str) -> str:
        """
        Extracts text using OCR, typically if direct extraction yields insufficient text.
        """
        ocr_text_parts = []
        MIN_DIRECT_TEXT_LENGTH_TO_TRIGGER_OCR = 200 # characters for the whole PDF

        # Heuristic: If PyPDF2 text is very short, try OCR.
        if len(pypdf2_text) < MIN_DIRECT_TEXT_LENGTH_TO_TRIGGER_OCR:
            print(f"Directly extracted text from '{pdf_name}' is short ({len(pypdf2_text)} chars). Attempting full OCR.")
            try:
                # pdf2image is used to convert PDF pages to images for OCR
                from pdf2image import convert_from_bytes 
                
                pdf_file_stream.seek(0) # Reset stream position
                # It's important that pdf_file_stream.read() is called here, as convert_from_bytes expects bytes.
                images = convert_from_bytes(pdf_file_stream.read(), dpi=200) 
                
                if not images:
                    print(f"pdf2image could not convert '{pdf_name}' to images. Using PyPDF2 text.")
                    return pypdf2_text

                print(f"Converted '{pdf_name}' to {len(images)} images for OCR.")
                for i, image in enumerate(images):
                    print(f"OCR'ing page {i+1} of '{pdf_name}'...")
                    try:
                        page_ocr_text = self._ocr_pdf_page_image(image)
                        if page_ocr_text:
                            ocr_text_parts.append(page_ocr_text)
                    except pytesseract.TesseractNotFoundError: # Propagated from _ocr_pdf_page_image
                        print(f"OCR skipped for '{pdf_name}' due to Tesseract not found.")
                        return pypdf2_text # Fallback to PyPDF2 text immediately
                    # Other errors in _ocr_pdf_page_image return "" and are handled by `if page_ocr_text`
                
                ocr_full_text = "\n".join(ocr_text_parts)
                print(f"OCR processing completed for '{pdf_name}'. Extracted {len(ocr_full_text)} chars via OCR.")
                
                # Prefer OCR text if it's significantly longer and not empty
                if ocr_full_text.strip() and len(ocr_full_text) > len(pypdf2_text) * 1.1: 
                     print(f"Using OCR text for '{pdf_name}' as it's longer.")
                     return ocr_full_text
                else:
                     print(f"Using PyPDF2 text for '{pdf_name}' (OCR text not significantly longer or empty).")
                     return pypdf2_text

            except ImportError:
                print("PDF2IMAGE NOT FOUND: 'pdf2image' library is not installed. OCR will be skipped for this PDF. "
                      "Please install it ('pip install pdf2image') and ensure Poppler (or other dependency) is installed.")
                return pypdf2_text # Fallback to PyPDF2 text
            except Exception as e: # Catch other potential errors from pdf2image or within this block
                print(f"An unexpected error occurred during OCR preparation for '{pdf_name}': {e}")
                return pypdf2_text # Fallback
        else:
            print(f"Sufficient text ({len(pypdf2_text)} chars) extracted directly by PyPDF2 from '{pdf_name}'. Skipping OCR.")
            return pypdf2_text

    def process_pdf(self, pdf_file_stream: io.BytesIO, pdf_name: str) -> List[LangchainDocument]:
        """
        Processes a single PDF file: extracts text (direct + OCR if needed),
        chunks it, and prepares Langchain Document objects.
        Embeddings are NOT generated here; they will be handled by the vector store.
        """
        print(f"Processing PDF: {pdf_name}")
        
        # 1. Direct text extraction
        direct_text = self._extract_text_from_pdf_pypdf2(pdf_file_stream, pdf_name)
        
        # 2. OCR (conditionally)
        final_text_to_chunk = self._extract_text_with_ocr(pdf_file_stream, pdf_name, direct_text)

        if not final_text_to_chunk.strip():
            print(f"No text could be extracted from '{pdf_name}' after direct and OCR attempts.")
            return []

        # 3. Chunking the text
        print(f"Chunking text from '{pdf_name}' (total {len(final_text_to_chunk)} chars)...")
        text_chunks = self.text_splitter.split_text(final_text_to_chunk)
        
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
    print("\n--- Testing DocumentIndexer ---")
    indexer = DocumentIndexer(chunk_size=500, chunk_overlap=50)

    # This test requires:
    # 1. A PDF file named 'sample.pdf' in the same directory as this script.
    # 2. Tesseract OCR installed and accessible in PATH or configured.
    # 3. 'pdf2image' library installed (pip install pdf2image).
    # 4. Poppler binaries installed and accessible by pdf2image (common dependency).

    sample_pdf_path = "sample.pdf" 
    try:
        with open(sample_pdf_path, "rb") as f:
            pdf_bytes_io = io.BytesIO(f.read())
            print(f"\n--- Attempting to process '{sample_pdf_path}' (ensure it exists and dependencies are installed) ---")
            
            documents = indexer.process_pdf(pdf_bytes_io, sample_pdf_path)
            
            if documents:
                print(f"\nSuccessfully processed '{sample_pdf_path}' into {len(documents)} chunks.")
                if len(documents) > 0:
                    print("First chunk metadata:", documents[0].metadata)
                    print("First chunk content (first 100 chars):", documents[0].page_content[:100] + "...")
            else:
                print(f"Processing '{sample_pdf_path}' yielded no document chunks. Check PDF content and OCR setup.")

    except FileNotFoundError:
        print(f"\nTEST SKIPPED: '{sample_pdf_path}' not found. Place a sample PDF in the root directory to test.")
    except pytesseract.TesseractNotFoundError:
        print("\nTEST FAILED/SKIPPED: Tesseract OCR not found. Please install Tesseract and ensure it's in your PATH, "
              "or configure pytesseract.pytesseract.tesseract_cmd in document_indexer.py.")
    except ImportError as e:
        if e.name == 'pdf2image':
            print("\nTEST WARNING: 'pdf2image' library not found. OCR part of PDF processing will be skipped. "
                  "Install with 'pip install pdf2image' and ensure Poppler is set up for full OCR testing.")
        else:
            print(f"\nTEST FAILED/SKIPPED: Missing a Python library ({e.name}). Please install all dependencies.")
    except Exception as e: # Catch any other unexpected errors during the test
        print(f"\nAn unexpected error occurred during the test for '{sample_pdf_path}': {e}")
        print("Ensure all dependencies (Tesseract, Poppler, Python libs) are correctly installed and configured.")

    print("\n--- DocumentIndexer tests complete ---")
