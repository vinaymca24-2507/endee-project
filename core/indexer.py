import os
import ast
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from core.database import db_client
from core.config import settings

logger = logging.getLogger(__name__)

class CodeParser:
    """Parses code files to extract meaningful chunks (Functions, Classes)."""
    
    def parse_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        if file_path.endswith(".py"):
            return self._parse_python(file_path, content)
        # Placeholder for JS/TS parsing
        return self._parse_text(file_path, content)

    def _parse_python(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        chunks = []
        try:
            tree = ast.parse(content)
            lines = content.splitlines()
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    start_line = node.lineno
                    end_line = node.end_lineno
                    # Extract the source segment
                    segment = "\n".join(lines[start_line-1:end_line])
                    
                    # Create metadata
                    chunk = {
                        "file_path": file_path,
                        "name": node.name,
                        "type": type(node).__name__,
                        "content": segment,
                        "start_line": start_line,
                        "end_line": end_line,
                        "language": "python"
                    }
                    chunks.append(chunk)
        except SyntaxError:
            logger.warning(f"Syntax error parsing {file_path}")
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            
        return chunks

    def _parse_text(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Simple fallback chunking for non-Python files."""
        # Simple sliding window or fixed size chunking could go here
        # For now, treat the whole file as one chunk if it's small
        return [{
            "file_path": file_path,
            "name": os.path.basename(file_path),
            "type": "file",
            "content": content[:2000], # Limit size
            "start_line": 1,
            "end_line": len(content.splitlines()),
            "language": "text"
        }]

class Indexer:
    def __init__(self):
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
        self.embedder = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        self.parser = CodeParser()

    def index_repository(self, repo_path: str):
        """Walks the repository, parses files, embeds chunks, and stores in Endee."""
        logger.info(f"Indexing repository at {repo_path}")
        
        all_chunks = []
        all_embeddings = []
        
        for root, _, files in os.walk(repo_path):
            if "venv" in root or ".git" in root or "__pycache__" in root:
                continue
                
            for file in files:
                if not file.endswith((".py", ".js", ".ts", ".md")):
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    file_chunks = self.parser.parse_file(file_path, content)
                    if not file_chunks:
                        continue
                        
                    # Generate embeddings for chunks
                    texts = [chunk["content"] for chunk in file_chunks]
                    embeddings = self.embedder.encode(texts).tolist()
                    
                    all_chunks.extend(file_chunks)
                    all_embeddings.extend(embeddings)
                    
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")

        # Batch insert into Endee
        if all_chunks:
            logger.info(f"Inserting {len(all_chunks)} vectors to Endee...")
            db_client.insert_vectors(all_embeddings, all_chunks)
            logger.info("Indexing complete.")
        else:
            logger.warning("No chunks found to index.")

# Singleton
indexer = Indexer()
