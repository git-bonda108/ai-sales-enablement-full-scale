#!/usr/bin/env python3
import docx
import re

def extract_all_text_from_docx(docx_path):
    """Extract all text from a Word document"""
    doc = docx.Document(docx_path)
    
    full_text = ""
    for paragraph in doc.paragraphs:
        full_text += paragraph.text + "\n"
    
    return full_text

if __name__ == "__main__":
    try:
        full_text = extract_all_text_from_docx("streamlit-complete.docx")
        
        print("Full document content:")
        print("=" * 80)
        print(full_text)
        print("=" * 80)
            
    except Exception as e:
        print(f"Error extracting text: {e}") 