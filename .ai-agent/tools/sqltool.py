
from __future__ import annotations
import re
from pydantic import BaseModel
from tools.base import Tool, ToolInvocation, ToolKind, ToolResult
from config.config import Config

from sqlalchemy import create_engine, text
from db.dbmanager import PostgresConnectionManager
from db.validator import SQLQueryValidator
import json


class PostgresQueryParams(BaseModel):
    query: str

class PostgresQueryTool(Tool):

    name = "postgres_query"
    description = """
Execute read-only SQL queries on the healthcare database.

Rules:
- Only SELECT queries are allowed
- Use proper JOINs based on relationships
- Always limit results when possible
"""
    kind = ToolKind.READ
    schema = PostgresQueryParams  

    def __init__(self, config: Config):
        super().__init__(config)
        print("Initializing PostgresQueryTool")

        # Create PostgreSQL connection
        self.engine = PostgresConnectionManager.get_engine()
    
    def _clean_query(self, query: str) -> str:
        query = re.sub(r"```.*?```", "", query, flags=re.DOTALL)
        return query.strip().rstrip(";")

    def _add_limit(self, query: str) -> str:
        query_clean = query.strip().rstrip(";")

        match = re.search(r"\blimit\s+(\d+)", query_clean, re.IGNORECASE)

        if match:
            limit_val = int(match.group(1))
            if limit_val > 100:
                return re.sub(r"\blimit\s+\d+", "LIMIT 100", query_clean, flags=re.IGNORECASE)
            return query_clean

        return query_clean + " LIMIT 50"
    
    async def execute(self, invocation: ToolInvocation) -> ToolResult:

        query = invocation.params.get("query")

        if not query:
            return ToolResult.error_result("Missing SQL query")

        query = query.replace("```sql", "").replace("```", "").strip()
       
        # safety check
        is_valid, error = SQLQueryValidator.validate(query)
        if not is_valid:
            return ToolResult.error_result(error)
        
        # add limit if not present
        safe_query = self._add_limit(query)

        try:

            with self.engine.connect() as conn:

                conn.execute(text("SET statement_timeout = 5000"))

                result = conn.execute(text(safe_query))

                rows = result.fetchall()

                columns = result.keys()

                records = [dict(zip(columns, row)) for row in rows]

            return ToolResult.success_result(
                # output=str(records),
                output=json.dumps(records if records else [{"message": "No data found"}], default=str),
                metadata={
                    "rows_returned": len(records),
                    "query": safe_query
                }
            )

        except Exception as e:
            error_message = str(e).split("\n")[0]
            return ToolResult.error_result(
                error=error_message,
                output=json.dumps({
                    "failed_query": query,
                    "error_message": error_message
                })
            )   
            
