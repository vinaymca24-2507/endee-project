import requests
import logging
import uuid
import json
import zlib
try:
    import msgpack
except ImportError:
    msgpack = None

from .config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EndeeWrapper:
    """
    Check if Endee is running via HTTP.
    Uses requests to communicate with Endee REST API.
    """
    def __init__(self):
        self.host = settings.ENDEE_HOST
        self.port = settings.ENDEE_PORT
        self.collection_name = settings.ENDEE_COLLECTION_NAME
        self.base_url = f"http://{self.host}:{self.port}/api/v1"
        self._connect()

    def _connect(self):
        """Checks connection to the Endee server and ensures collection exists."""
        try:
            # Check health
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            # Endee health check might return simple string or JSON
            if resp.status_code == 200:
                logger.info(f"Connected to Endee at {self.base_url}")
            else:
                logger.warning(f"Endee health check failed: {resp.status_code}")

            # Check if collection exists
            self._ensure_collection()
            
        except Exception as e:
            logger.error(f"Failed to connect to Endee: {e}")
            # We don't raise here to allow app to start even if DB is temporarily down

    def _ensure_collection(self):
        try:
            # List indexes
            resp = requests.get(f"{self.base_url}/index/list", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                # API returns {"indexes": [...]}
                indexes = data.get("indexes", [])
                
                # Check based on name
                exists = False
                for idx in indexes:
                    if idx.get("name") == self.collection_name:
                        exists = True
                        break
                
                if not exists:
                    logger.info(f"Collection {self.collection_name} not found. Creating...")
                    self._create_collection()
                else:
                    logger.info(f"Collection {self.collection_name} exists.")
            else:
                logger.error(f"Failed to list indexes: {resp.text}")
        except Exception as e:
            logger.error(f"Error checking collection: {e}")

    def _create_collection(self):
        payload = {
            "index_name": self.collection_name,
            "dim": 384, # Default for all-MiniLM-L6-v2
            "space_type": "cosine",
            "M": 16,
            "ef_con": 200,
            "precision": "float32" # or INT8
        }
        try:
            resp = requests.post(f"{self.base_url}/index/create", json=payload, timeout=10)
            if resp.status_code == 200:
                logger.info(f"Collection {self.collection_name} created.")
            else:
                 logger.error(f"Failed to create collection: {resp.text}")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")

    def insert_vectors(self, vectors, metadata):
        """
        Inserts vectors into Endee.
        Uses MessagePack to support metadata.
        """
        if msgpack is None:
            logger.error("msgpack module not installed. Cannot insert vectors with metadata.")
            return

        payload = []
        for i, vec in enumerate(vectors):
            meta = metadata[i] if i < len(metadata) else {}
            # Ensure ID exists
            if "id" not in meta:
                meta["id"] = str(uuid.uuid4())
            doc_id = meta["id"]
            
            # Compress metadata
            # We store the entire metadata dict as a compressed JSON blob
            # content is part of metadata, so it will be retrievable
            try:
                meta_bytes = zlib.compress(json.dumps(meta).encode('utf-8'))
            except Exception as e:
                logger.error(f"Failed to compress metadata for {doc_id}: {e}")
                meta_bytes = b""

            # Endee VectorObject structure: [id, meta, filter, norm, vector]
            # id: string
            # meta: binary
            # filter: string (JSON)
            # norm: float
            # vector: list[float]
            item = [
                doc_id,
                meta_bytes,
                "{}", # Default empty filter
                0.0,  # Default norm
                vec
            ]
            payload.append(item)
            
        try:
            url = f"{self.base_url}/index/{self.collection_name}/vector/insert"
            packed_data = msgpack.packb(payload)
            resp = requests.post(
                url, 
                data=packed_data, 
                headers={"Content-Type": "application/msgpack"}, 
                timeout=30
            )
            if resp.status_code == 200:
                logger.info(f"Inserted {len(vectors)} vectors into {self.collection_name}")
            else:
                logger.error(f"Error inserting vectors: {resp.text}")
        except Exception as e:
            logger.error(f"Error inserting vectors: {e}")

    def search(self, query_vector, limit=5):
        """
        Searches Endee.
        Returns parsed results with metadata.
        """
        if msgpack is None:
            logger.error("msgpack module not installed. Cannot perform search.")
            return []

        payload = {
            "vector": query_vector,
            "k": limit,
            "include_vectors": False # We don't need vectors back, just metadata
        }
        
        try:
            url = f"{self.base_url}/index/{self.collection_name}/search"
            # Send query as JSON (easier), response will be MessagePack
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
            
            if resp.status_code == 200:
                # Unpack response
                # Response is array of VectorResult
                # VectorResult: [similarity, id, meta, filter, norm, vector]
                try:
                    results_raw = msgpack.unpackb(resp.content, raw=False)
                except Exception as e:
                    logger.error(f"Failed to unpack search response: {e}")
                    return []

                parsed_results = []
                for r in results_raw:
                    if len(r) < 3: # Basic validation
                        continue
                        
                    similarity = r[0]
                    doc_id = r[1]
                    meta_bytes = r[2]
                    
                    # Decompress metadata
                    try:
                        if meta_bytes:
                            meta = json.loads(zlib.decompress(meta_bytes).decode('utf-8'))
                        else:
                            meta = {}
                    except Exception as e:
                        logger.warning(f"Failed to decompress metadata for result {doc_id}: {e}")
                        meta = {}
                        
                    # Add score to meta for convenience or keep separate
                    # The app likely expects a list of dicts with 'score', 'metadata', etc.
                    # Or maybe it expects just the metadata dict plus score?
                    # Let's return a clean structure
                    result_item = {
                        "id": doc_id,
                        "score": similarity,
                        "metadata": meta
                    }
                    
                    # Flatten content for UI convenience
                    if "content" in meta:
                        result_item["content"] = meta["content"]
                    if "file_path" in meta:
                        result_item["file_path"] = meta["file_path"]
                    if "name" in meta:
                        result_item["name"] = meta["name"]
                    if "language" in meta:
                        result_item["language"] = meta["language"]

                    parsed_results.append(result_item)
                
                return parsed_results
            else:
                logger.error(f"Error during search: {resp.text}")
                return []
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []

# Singleton instance
db_client = EndeeWrapper()
