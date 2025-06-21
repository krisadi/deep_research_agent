import PyPDF2
import io

def extract_text_from_pdf_stream(pdf_stream, filename="<stream>"):
    """
    Extracts text from a PDF file stream.
    
    Args:
        pdf_stream (file-like object): A file-like object representing the PDF.
        filename (str): The original name of the file, for logging.
        
    Returns:
        str: The extracted text from the PDF.
             Returns an error message string if extraction fails.
    """
    try:
        reader = PyPDF2.PdfReader(pdf_stream)
        text = []
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text.append(page.extract_text() or "") # Add empty string if None
        return "\n".join(text)
    except PyPDF2.errors.PdfReadError as e:
        print(f"Error reading PDF {filename}: {e}. The file might be corrupted or password-protected.")
        return f"Could not extract text from {filename}: File is corrupted or password-protected."
    except Exception as e:
        print(f"An unexpected error occurred while processing PDF {filename}: {e}")
        return f"Could not extract text from {filename}: An unexpected error occurred."

def extract_text_from_uploaded_files(uploaded_files):
    """
    Extracts text from a list of uploaded PDF files (Streamlit UploadedFile objects).

    Args:
        uploaded_files (list): A list of Streamlit UploadedFile objects.

    Returns:
        list: A list of strings, where each string is the extracted text
              from a corresponding PDF. If extraction fails for a file,
              an error message string is included for that file.
    """
    all_text_results = []
    if not uploaded_files:
        return all_text_results
    
    for uploaded_file in uploaded_files:
        try:
            # Streamlit's UploadedFile is a file-like object.
            # We can pass it directly to PyPDF2.
            # Ensure the stream is reset if it has been read before (though usually not needed for new uploads)
            uploaded_file.seek(0)
            print(f"Processing PDF: {uploaded_file.name}")
            text = extract_text_from_pdf_stream(uploaded_file, uploaded_file.name)
            all_text_results.append(text)
            print(f"Successfully extracted text from {uploaded_file.name}" if "Could not extract" not in text else f"Failed to extract text from {uploaded_file.name}")
        except Exception as e:
            # This is a fallback, specific errors should be caught in extract_text_from_pdf_stream
            print(f"Error processing uploaded file {uploaded_file.name}: {e}")
            all_text_results.append(f"Could not extract text from {uploaded_file.name}: Critical processing error.")
            
    return all_text_results
