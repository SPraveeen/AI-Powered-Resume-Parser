import PyPDF2
from docx import Document
from typing import Optional
import io

class FileProcessor:
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Error processing DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_content: bytes) -> str:
        """Extract text from TXT file"""
        try:
            return file_content.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Error processing TXT: {str(e)}")
    
    @classmethod
    def process_file(cls, file_content: bytes, filename: str) -> str:
        """Process file based on extension"""
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            return cls.extract_text_from_pdf(file_content)
        elif file_extension == 'docx':
            return cls.extract_text_from_docx(file_content)
        elif file_extension == 'txt':
            return cls.extract_text_from_txt(file_content)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
