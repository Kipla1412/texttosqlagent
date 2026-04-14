from sqlalchemy import create_engine, text
from config.config import Config


class SchemaLoader:

    def __init__(self, config: Config):
        self.config = config
        self.engine = create_engine(self.config.database_url)
        self._schema_cache = None

    def get_schema(self):
        """
        Load database schema from PostgreSQL
        """

        if self._schema_cache:
            return self._schema_cache

        query = """
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name
        """

        schema = {}

        with self.engine.connect() as conn:
            result = conn.execute(text(query))

            for table, column in result:
                schema.setdefault(table, []).append(column)

        self._schema_cache = schema

        return schema

    def select_relevant_tables(self, question: str):

        schema = self.get_schema()

        question = question.lower()

        selected = {}

        for table, columns in schema.items():

            if table in question:
                selected[table] = columns
                continue

            for col in columns:
                if col in question:
                    selected[table] = columns
                    break

        if not selected:
            return schema

        return selected

    def format_schema(self, schema):

        text = "# Database Schema\n\n"

        for table, cols in schema.items():

            text += f"Table: {table}\n"

            for col in cols:
                text += f"- {col}\n"

            text += "\n"

        return text