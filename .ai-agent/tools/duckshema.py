from __future__ import annotations

from pydantic import BaseModel
import duckdb

from tools.base import Tool, ToolInvocation, ToolResult, ToolKind
from config.config import Config
from .duckdbtool import DuckDBConnectionManager


class SchemaParams(BaseModel):
    table_name: str | None = None


class DuckDBSchemaInspectorTool(Tool):

    name = "duckdb_schema_inspector"
    kind = ToolKind.READ

    description = """
Inspect the DuckDB database schema.

Use this tool to discover:
- available tables
- column names
- column data types
"""

    schema = SchemaParams

    def __init__(self, config: Config):
        super().__init__(config)
        self.conn = DuckDBConnectionManager.get_connection()

    async def execute(self, invocation: ToolInvocation) -> ToolResult:

        table = invocation.params.get("table_name")

        try:

            if table:
                query = f"DESCRIBE {table}"
            else:
                query = "SHOW TABLES"

            result = self.conn.execute(query).fetchdf()

            return ToolResult.success_result(
                output=result.to_json(orient="records")
            )

        except Exception as e:

            return ToolResult.error_result(
                error=str(e)
            )