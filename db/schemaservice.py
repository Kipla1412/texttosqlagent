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
from db.semanticsearch import SchemaSemanticSearch

class SchemaService:

    def __init__(self):
        self.schema = SchemaRegistry.get_schema()
        self.relationships = SchemaRegistry.get_relationships()

        self.semantic = SchemaSemanticSearch(self.schema)

    def get_schema_for_question(self, question: str) -> str:

        question = question.lower()

        semantic_tables = self.semantic.search(question)
        keyword_tables = self._keyword_match_tables(question)

        relevant_tables = list(set(semantic_tables + keyword_tables))
        print(f"Final tables used: {relevant_tables}")

        filtered = {
            table: self.schema[table]
            for table in relevant_tables
        }
    
        filtered_relationships = []

        for rel in self.relationships:
            tables_in_rel = [t.strip() for t in rel.split() if t.isidentifier()]

            if any(t in relevant_tables for t in tables_in_rel):
                filtered_relationships.append(rel)

        schema_text = self.format_schema(filtered, filtered_relationships, relevant_tables)
        print(f"DEBUG: Generated schema length: {len(schema_text)} characters")
        print(f"DEBUG: Schema contains appointment table: {'appointment' in schema_text}")
        print(f"DEBUG: Relevant tables: {relevant_tables}")
        print("DEBUG: Full schema text:")
        print(schema_text)
        return schema_text


    def format_schema(self, schema, relationships, relevant_tables=None):

        text = "# Database Schema\n\n"

        # Only show relevant tables if provided, otherwise show all
        tables_to_show = relevant_tables if relevant_tables else schema.keys()

        for table_name in tables_to_show:
            if table_name in schema:
                data = schema[table_name]
                text += f"Table: {table_name}\n"
                text += f"Description: {data['description']}\n"

                for col, col_data in data["columns"].items():
                    if isinstance(col_data, dict):
                        # New format with type and description
                        col_type = col_data.get("type", "UNKNOWN")
                        col_desc = col_data.get("description", "No description")
                        text += f"- {col} ({col_type}): {col_desc}\n"
                    else:
                        # Old format (backward compatibility)
                        text += f"- {col}: {col_data}\n"

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
        text += "- ONLY use tables present in the schema above\n"
        text += "- DO NOT reference tables not listed\n"

        # Query strategy (NEW)
        text += "\n# Query Strategy\n"
        text += "- Start from patient table\n"
        text += "- Identify required columns\n"
        text += "- Join related tables if needed\n"
        text += "- Apply filters using WHERE clause\n"
        text += "- Use LIMIT for large result sets\n"
        
        # Column information for reference
        if relevant_tables:
            text += "\n# Available Columns by Table:\n"
            for table_name in relevant_tables:
                if table_name in self.schema:
                    table_data = self.schema[table_name]
                    text += f"\n## {table_name.upper()}:\n"
                    
                    # Add column information with types
                    columns = table_data.get("columns", {})
                    for col_name, col_data in columns.items():
                        if isinstance(col_data, dict):
                            col_type = col_data.get("type", "UNKNOWN")
                            col_desc = col_data.get("description", "No description")
                            text += f"- {col_name} ({col_type}): {col_desc}\n"
                        else:
                            text += f"- {col_name}: {col_data}\n"
                    
                    text += "\n"

        text += "\n# Join Guidelines (CRITICAL)\n"
        text += "- ONLY use tables required for the question\n"
        text += "- DO NOT include unnecessary tables\n"
        text += "- Prefer minimal joins\n"
        text += "- If data is available in one table, DO NOT join others\n"
        text += "- Only join diagnosis, location, etc. if explicitly needed\n"
        
        # Example queries (CRITICAL)
        examples = SchemaRegistry.get_example_queries()

        filtered_examples = {}
        for name, query in examples.items():
            for table in schema.keys():
                if f" {table} " in query.lower():
                    filtered_examples[name] = query
                    break
        

        text += "\n# Example Queries\n"
        for name, query in filtered_examples.items():
            text += f"{name}:\n{query.strip()}\n\n"

        return text


 # def get_schema_for_question(self, question: str) -> str:

    #     schema = SchemaRegistry.get_schema()
    #     relationships = SchemaRegistry.get_relationships()

    #     question = question.lower()
    #     filtered = {}

    #     for table, data in schema.items():

    #         table_keywords = [table, table.replace("_", " ")]

    #         # match table name
    #         if any(keyword in question for keyword in table_keywords):
    #             filtered[table] = data
    #             continue

    #         # match columns
    #         for col in data["columns"]:
    #             if col.replace("_", " ") in question:
    #                 filtered[table] = data
    #                 break

    #     # fallback AFTER filtering
    #     if not filtered:
    #         filtered = schema

    #     # filter relationships
    #     filtered_tables = set(filtered.keys())

    #     filtered_relationships = [
    #         rel for rel in relationships
    #         if any(f"{table} " in rel or f" {table}" in rel for table in filtered_tables)
    #     ]

    #     return self.format_schema(filtered, filtered_relationships)

    def _keyword_match_tables(self, question: str) -> list:
        """Traditional keyword-based table matching"""
        question = question.lower()
        matched_tables = []
        
        for table, data in self.schema.items():
            table_keywords = [table, table.replace("_", " ")]
            
            # match table name
            if any(keyword in question for keyword in table_keywords):
                matched_tables.append(table)
                continue
            
            # match columns
            for col in data["columns"]:
                col_keywords = [col.lower(), col.replace("_", " ")]
                
                if any(keyword in question for keyword in col_keywords):
                    matched_tables.append(table)
                    break
        
        return matched_tables
