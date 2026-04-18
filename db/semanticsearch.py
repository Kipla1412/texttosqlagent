import os
import pickle
import hashlib
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from numpy.linalg import norm

class SchemaSemanticSearch:

    """
    Semantic search for database schema tables based on natural language queries.
    Uses sentence embeddings to find semantically similar tables.
    """
    def __init__(self, schema, cache_path="db/schema_embeddings.pkl"):
        self.schema = schema
        self.cache_path = cache_path

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.tables = list(schema.keys())

        self.schema_hash = self._compute_schema_hash()

        if os.path.exists(self.cache_path):
            self._load()
        else:
            self._build()
            self._save()

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
        """
        Build embeddings for all tables in the schema.
        """
        print("Building schema embeddings...")

        self.texts = [
            self._to_text(table, self.schema[table])
            for table in self.tables
        ]

        embeddings = self.model.encode(self.texts)

        # normalize embeddings (cosine similarity)
        self.embeddings = embeddings / norm(embeddings, axis=1, keepdims=True)

        # table name embeddings (for boosting)
        table_vecs = self.model.encode(self.tables)
        self.table_name_vecs = table_vecs / norm(table_vecs, axis=1, keepdims=True)

    def _save(self):
        """
        Save embeddings to cache.
        """
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
        """
        query_vec = self.model.encode([query])[0]
        query_vec = query_vec / norm(query_vec)

        # similarity score (main + table boost)
        scores = (
            0.7 * np.dot(self.embeddings, query_vec) +
            0.3 * np.dot(self.table_name_vecs, query_vec)
        )

        top_indices = np.argsort(scores)[-k:][::-1]

        results = [self.tables[i] for i in top_indices]

        print(f"Semantic tables for '{query}': {results}")
        for i in top_indices:
            print(f"  → {self.tables[i]} (score={scores[i]:.4f})")

        return results