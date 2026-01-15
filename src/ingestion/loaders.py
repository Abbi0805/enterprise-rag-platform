from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os
from pypdf import PdfReader
from src.types import Document

class BaseLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> List[Document]:
        pass

class TextLoader(BaseLoader):
    def load(self, file_path: str) -> List[Document]:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return [Document(
            content=content,
            metadata={"source": file_path, "type": "text"}
        )]

class PDFLoader(BaseLoader):
    def load(self, file_path: str) -> List[Document]:
        reader = PdfReader(file_path)
        documents = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                documents.append(Document(
                    content=text,
                    metadata={
                        "source": file_path, 
                        "type": "pdf", 
                        "page": i + 1
                    }
                ))
        return documents

def get_loader_for_file(file_path: str) -> BaseLoader:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return PDFLoader()
    elif ext in ['.txt', '.md']:
        return TextLoader()
    raise ValueError(f"No loader found for extension: {ext}")
