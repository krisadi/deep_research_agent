"""
Word Document Export Utility
Exports research results to .docx format with proper formatting and preserved links
"""

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import re
from datetime import datetime


def create_research_report_docx(query, results, is_raw_data=False):
    """
    Create a Word document from research results
    
    Args:
        query: The research query
        results: The research results (HTML formatted)
        is_raw_data: Whether this is raw data mode or AI synthesis mode
    
    Returns:
        Document: The Word document object
    """
    doc = Document()
    
    # Add title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run(f"Research Report: {query}")
    title_run.bold = True
    title_run.font.size = Pt(24)
    
    # Add timestamp
    timestamp = doc.add_paragraph()
    timestamp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    timestamp_run = timestamp.add_run(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    timestamp_run.font.size = Pt(11)
    
    # Add mode indicator
    mode_para = doc.add_paragraph()
    if is_raw_data:
        mode_para.add_run("Mode: Raw Data Analysis (LLM not available)")
    else:
        mode_para.add_run("Mode: AI-Synthesized Analysis")
    
    doc.add_paragraph()  # Spacing
    
    # Parse the HTML results and convert to Word document
    parse_html_to_docx(doc, results)
    
    return doc


def parse_html_to_docx(doc, html_content):
    """
    Parse HTML content and convert to Word document elements
    """
    # Remove the outer div wrapper
    html_content = re.sub(r'<div[^>]*>', '', html_content)
    html_content = re.sub(r'</div>', '', html_content)
    
    # Split content by HTML tags
    lines = html_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Handle different HTML elements
        if line.startswith('<h1'):
            # Extract text from h1
            text = re.search(r'<h1[^>]*>(.*?)</h1>', line)
            if text:
                para = doc.add_paragraph()
                run = para.add_run(text.group(1))
                run.bold = True
                run.font.size = Pt(18)
                
        elif line.startswith('<h2'):
            # Extract text from h2
            text = re.search(r'<h2[^>]*>(.*?)</h2>', line)
            if text:
                para = doc.add_paragraph()
                run = para.add_run(text.group(1))
                run.bold = True
                run.font.size = Pt(14)
                
        elif line.startswith('<h3'):
            # Extract text from h3
            text = re.search(r'<h3[^>]*>(.*?)</h3>', line)
            if text:
                para = doc.add_paragraph()
                run = para.add_run(text.group(1))
                run.bold = True
                run.font.size = Pt(12)
                
        elif line.startswith('<h4'):
            # Extract text from h4
            text = re.search(r'<h4[^>]*>(.*?)</h4>', line)
            if text:
                para = doc.add_paragraph()
                run = para.add_run(text.group(1))
                run.bold = True
                
        elif line.startswith('<div') and 'background:' in line:
            # Handle styled divs (info boxes, etc.)
            text = re.search(r'<div[^>]*>(.*?)</div>', line, re.DOTALL)
            if text:
                para = doc.add_paragraph()
                para.add_run(text.group(1).strip())
                
        elif line.startswith('<hr'):
            # Add a horizontal line
            doc.add_paragraph().add_run('_' * 50)
            
        elif line.startswith('<strong>'):
            # Handle bold text
            text = re.search(r'<strong>(.*?)</strong>', line)
            if text:
                para = doc.add_paragraph()
                run = para.add_run(text.group(1))
                run.bold = True
                
        elif line.startswith('•'):
            # Handle bullet points
            para = doc.add_paragraph()
            para.add_run(line)
            
        elif line.startswith('--- START OF'):
            # Handle source content markers
            para = doc.add_paragraph()
            run = para.add_run(line)
            run.italic = True
            
        elif line.startswith('--- END OF'):
            # Handle source content markers
            para = doc.add_paragraph()
            run = para.add_run(line)
            run.italic = True
            
        elif line.startswith('Title:') or line.startswith('URL:') or line.startswith('Abstract:') or line.startswith('Snippet:'):
            # Handle metadata fields
            para = doc.add_paragraph()
            para.add_run(line)
            
        elif 'http' in line and ('URL:' in line or line.startswith('http')):
            # Handle URLs - extract URL and make it clickable
            url_match = re.search(r'https?://[^\s]+', line)
            if url_match:
                url = url_match.group(0)
                para = doc.add_paragraph()
                
                # If it's a URL field, format it nicely
                if line.startswith('URL:'):
                    para.add_run('URL: ')
                    run = para.add_run(url)
                    run.font.color.rgb = None  # Blue color
                    run.font.underline = True
                else:
                    run = para.add_run(url)
                    run.font.color.rgb = None  # Blue color
                    run.font.underline = True
            else:
                para = doc.add_paragraph()
                para.add_run(line)
                
        else:
            # Regular text content
            if line and not line.startswith('<'):
                para = doc.add_paragraph()
                para.add_run(line)


def save_docx_to_bytes(doc):
    """
    Save document to bytes for Streamlit download
    """
    import io
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def generate_docx_filename(query):
    """
    Generate a filename for the Word document
    """
    # Clean the query for filename
    clean_query = re.sub(r'[^\w\s-]', '', query)
    clean_query = re.sub(r'[-\s]+', '-', clean_query)
    clean_query = clean_query[:50]  # Limit length
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"Research_Report_{clean_query}_{timestamp}.docx" 