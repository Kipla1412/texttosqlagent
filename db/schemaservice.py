# from sqlalchemy import create_engine, text
# from config.config import Config


# class SchemaLoader:

#     def __init__(self, config: Config):
#         self.config = config
#         self.engine = create_engine(self.config.database_url)
#         self._schema_cache = None

#     def get_schema(self):
#         """
#         Load database schema from PostgreSQL
#         """

#         if self._schema_cache:
#             return self._schema_cache

#         query = """
#         SELECT table_name, column_name
#         FROM information_schema.columns
#         WHERE table_schema = 'public'
#         ORDER BY table_name
#         """

#         schema = {}

#         with self.engine.connect() as conn:
#             result = conn.execute(text(query))

#             for table, column in result:
#                 schema.setdefault(table, []).append(column)

#         self._schema_cache = schema

#         return schema

#     def select_relevant_tables(self, question: str):

#         schema = self.get_schema()

#         question = question.lower()

#         selected = {}

#         for table, columns in schema.items():

#             if table in question:
#                 selected[table] = columns
#                 continue

#             for col in columns:
#                 if col in question:
#                     selected[table] = columns
#                     break

#         if not selected:
#             return schema

#         return selected

#     def format_schema(self, schema):

#         text = "# Database Schema\n\n"

#         for table, cols in schema.items():

#             text += f"Table: {table}\n"

#             for col in cols:
#                 text += f"- {col}\n"

#             text += "\n"

#         return text

from db.schemaregistry import SchemaRegistry


class SchemaService:

    def get_schema_for_question(self, question: str) -> str:

        schema = SchemaRegistry.get_schema()
        relationships = SchemaRegistry.get_relationships()

        question = question.lower()
        filtered = {}

        for table, data in schema.items():

            table_keywords = [table, table.replace("_", " ")]

            # match table name
            if any(keyword in question for keyword in table_keywords):
                filtered[table] = data
                continue

            # match columns
            for col in data["columns"]:
                if col.replace("_", " ") in question:
                    filtered[table] = data
                    break

        # fallback AFTER filtering
        if not filtered:
            filtered = schema

        # filter relationships
        filtered_tables = set(filtered.keys())

        filtered_relationships = [
            rel for rel in relationships
            if any(f"{table} " in rel or f" {table}" in rel for table in filtered_tables)
        ]

        return self.format_schema(filtered, filtered_relationships)


    def format_schema(self, schema, relationships):

        text = "# Database Schema\n\n"

        for table, data in schema.items():
            text += f"Table: {table}\n"
            text += f"Description: {data['description']}\n"

            for col, desc in data["columns"].items():
                text += f"- {col}: {desc}\n"

            text += "\n"

        text += "# Relationships\n"
        for rel in relationships:
            text += f"- {rel}\n"
        
        # SQL rules
        text += "\n# SQL Rules\n"
        text += "- Always use patient.id for joins (never patient.patient_id)\n"
        text += "- Use JOIN when querying multiple tables\n"
        text += "- Use table aliases (p, pt, pa, pi)\n"
        text += "- Always use explicit column names\n"
        text += "- Use LIMIT for large result sets\n"
        text += "- Prefer LEFT JOIN when data may be missing\n"

        # Query strategy (NEW)
        text += "\n# Query Strategy\n"
        text += "- Start from patient table\n"
        text += "- Identify required columns\n"
        text += "- Join related tables if needed\n"
        text += "- Apply filters using WHERE clause\n"

        text += "\n# Join Guidelines (CRITICAL)\n"
        text += "- ONLY use tables required for the question\n"
        text += "- DO NOT include unnecessary tables\n"
        text += "- Prefer minimal joins\n"
        text += "- If data is available in one table, DO NOT join others\n"
        text += "- Only join diagnosis, location, etc. if explicitly needed\n"
        
        # Example queries (CRITICAL)
        examples = SchemaRegistry.get_example_queries()

        filtered_examples = {
            name: query
            for name, query in examples.items()
            if any(table in query for table in schema.keys())
        }

        text += "\n# Example Queries\n"
        for name, query in filtered_examples.items():
            text += f"{name}:\n{query.strip()}\n\n"

        return text