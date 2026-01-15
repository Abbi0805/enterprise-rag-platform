import os
import shutil
import tempfile
import subprocess
from typing import List, Optional
from src.types import Document
from src.ingestion.loaders import get_loader_for_file

class GitHubIngestor:
    def __init__(self, repo_url: str, branch: str = "main"):
        self.repo_url = repo_url
        self.branch = branch
        self.supported_extensions = {'.md', '.txt', '.py', '.js', '.ts', '.html', '.css', '.json'} # Expand as needed

    def ingest(self) -> List[Document]:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_name = self.repo_url.split("/")[-1].replace(".git", "")
            target_dir = os.path.join(temp_dir, repo_name)
            
            print(f"Cloning {self.repo_url}...")
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", "--branch", self.branch, self.repo_url, target_dir],
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                # Try without branch if main fails (fallback to default)
                subprocess.run(
                    ["git", "clone", "--depth", "1", self.repo_url, target_dir],
                    check=True,
                    capture_output=True
                )

            documents = []
            for root, _, files in os.walk(target_dir):
                if ".git" in root:
                    continue
                    
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in self.supported_extensions:
                        file_path = os.path.join(root, file)
                        try:
                            # Use existing loaders where possible, or fallback to text
                            try:
                                loader = get_loader_for_file(file_path)
                                docs = loader.load(file_path)
                            except ValueError:
                                # Fallback for code files not explicitly in get_loader_for_file
                                from src.ingestion.loaders import TextLoader
                                loader = TextLoader()
                                docs = loader.load(file_path)
                            
                            # Add Repo Metadata
                            for doc in docs:
                                rel_path = os.path.relpath(file_path, target_dir)
                                doc.metadata["source"] = f"{self.repo_url}/blob/{self.branch}/{rel_path}"
                                doc.metadata["repo"] = self.repo_url
                            
                            documents.extend(docs)
                        except Exception as e:
                            print(f"Failed to ingest {file}: {e}")
                            
            return documents
