import os
import pickle
import hashlib
import json
import numpy as np
from numpy.linalg import norm
from config.config import Config
from google import genai
import re
import time
import logging

class SchemaSemanticSearch:

    """
    Semantic search for database schema tables based on natural language queries.
    Uses sentence embeddings to find semantically similar tables.
    """
    def __init__(self, schema, config: Config, cache_path="db/schema_embeddinggs.pkl"):
        self.schema = schema
        self.cache_path = cache_path

        # self.embed_fn = self.embed

        self.client = genai.Client(api_key=config.gemini_api_key)

        self.tables = list(schema.keys())

        self.schema_hash = self._compute_schema_hash()

        if os.path.exists(self.cache_path):
            self._load()
        else:
            self._build()
            self._save()

    def embed(self, text: str):
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                res = self.client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=text
                )
                return np.array(res.embeddings[0].values)
            except Exception as e:
                if attempt == max_retries - 1:
                    logging.error(f"Failed to embed text after {max_retries} attempts: {e}")
                    raise
                
                delay = base_delay * (2 ** attempt)
                logging.warning(f"Embedding attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                time.sleep(delay)

    def embed_batch(self, texts):
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                res = self.client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=texts
                )
                return np.array([e.values for e in res.embeddings])
            except Exception as e:
                if attempt == max_retries - 1:
                    logging.error(f"Failed to embed batch after {max_retries} attempts: {e}")
                    raise
                
                delay = base_delay * (2 ** attempt)
                logging.warning(f"Batch embedding attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                time.sleep(delay)

    def _compute_schema_hash(self):
        """
        Compute a hash of the schema to detect changes.
        """
        return hashlib.md5(
            json.dumps(self.schema, sort_keys=True).encode()
        ).hexdigest()

    def _to_text(self, table, data):
        """
        Convert table schema to natural language text.
        """
        col_parts = []

        for col, meta in data["columns"].items():
            if isinstance(meta, dict):
                col_type = meta.get("type", "")
                col_description = meta.get("description", "")
                col_parts.append(f"{col} ({col_type}) {col_description}")
            else:
                col_parts.append(f"{col} {meta}")

        cols = "\n".join(col_parts)

        return f"""
        Table: {table}
        Description: {data['description']}
        Columns:
        {cols}
        """.strip()

    def _build(self):
        print("Building schema embeddings...")

        self.texts = [
            self._to_text(table, self.schema[table])
            for table in self.tables
        ]

        try:
            embeddings = self.embed_batch(self.texts)
            self.embeddings = embeddings / norm(embeddings, axis=1, keepdims=True)

            # table name embeddings
            # table_vecs = np.array([self.embed(t) for t in self.tables])
            table_vecs = self.embed_batch(self.tables)
            self.table_name_vecs = table_vecs / norm(table_vecs, axis=1, keepdims=True)
            print("Schema embeddings built successfully")
        except Exception as e:
            logging.error(f"Failed to build schema embeddings: {e}")
            print("Warning: Failed to build embeddings, semantic search will be disabled")
            # Set empty embeddings to prevent crashes
            self.embeddings = np.zeros((len(self.texts), 768))  # Default embedding size
            self.table_name_vecs = np.zeros((len(self.tables), 768))
        
    def _save(self):
        """
        Save embeddings to cache.
        """
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, "wb") as f:
            pickle.dump({
                "tables": self.tables,
                "texts": self.texts,
                "embeddings": self.embeddings,
                "table_name_vecs": self.table_name_vecs,
                "schema_hash": self.schema_hash,
            }, f)

        print("Embeddings saved")

    def _load(self):
        """
        Load embeddings from cache.
        """
        print("Loading cached embeddings...")

        with open(self.cache_path, "rb") as f:
            data = pickle.load(f)

        # check schema change
        if data.get("schema_hash") != self.schema_hash:
            print("Schema changed → rebuilding embeddings")
            self._build()
            self._save()
            return

        self.tables = data["tables"]
        self.texts = data["texts"]
        self.embeddings = data["embeddings"]
        self.table_name_vecs = data["table_name_vecs"]

    def search(self, query, k=4):
        """
        Search for semantically similar tables based on a natural language query.
        Falls back to keyword matching if semantic search fails.
        """
        try:
            query_vec = self.embed(query)
            query_vec = query_vec / norm(query_vec)

            # similarity score (main + table boost)
            scores = (
                0.7 * np.dot(self.embeddings, query_vec) +
                0.3 * np.dot(self.table_name_vecs, query_vec)
            )

            top_indices = np.argsort(scores)[-k:][::-1]

            # results = [self.tables[i] for i in top_indices]
            results = []

            for i in top_indices:
                if scores[i] > 0.35:
                    results.append(self.tables[i])

            print(f"Semantic tables for '{query}': {results}")
            for i in top_indices:
                print(f"  → {self.tables[i]} (score={scores[i]:.4f})")

                return results
        except Exception as e:
            logging.warning(f"Semantic search failed, falling back to keyword matching: {e}")
            return self._keyword_fallback_search(query, k)
    
    def _keyword_fallback_search(self, query, k=4):
        """
        Fallback keyword-based search when semantic search fails.
        """
        query = query.lower()
        matched_tables = []
        
        for table in self.tables:
            table_keywords = [table, table.replace("_", " ")]
            
            # match table name
            if any(keyword in query for keyword in table_keywords):
                matched_tables.append(table)
                continue
            
            # match columns from schema
            if table in self.schema:
                for col in self.schema[table]["columns"]:
                    col_keywords = [col.lower(), col.replace("_", " ")]
                    if any(keyword in query for keyword in col_keywords):
                        matched_tables.append(table)
                        break
        
        # Limit results to k
        results = matched_tables[:k]
        
        print(f"Keyword fallback tables for '{query}': {results}")
        for table in results:
            print(f"  → {table} (keyword match)")

        return results