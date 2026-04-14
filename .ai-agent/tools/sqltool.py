
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
Execute SQL queries on the FHIR patient database.

Tables available:

patient
Columns:
id, patient_id, given_name, family_name, gender, birth_date

patient_identifier
Columns:
id, patient_id, system, value

patient_telecom
Columns:
id, patient_id, system, value, use

patient_address
Columns:
id, patient_id, line, city, state, postal_code, country

Relationships:

patient.id = patient_identifier.patient_id
patient.id = patient_telecom.patient_id
patient.id = patient_address.patient_id
"""
    kind = ToolKind.READ
    schema = PostgresQueryParams  

    def __init__(self, config: Config):
        super().__init__(config)
        print("Initializing PostgresQueryTool")

        # Create DuckDB connection
        self.engine = PostgresConnectionManager.get_engine()
                
    async def execute(self, invocation: ToolInvocation) -> ToolResult:

        query = invocation.params.get("query")

        if not query:
            return ToolResult.error_result("Missing SQL query")

        # safety check
        is_valid, error = SQLQueryValidator.validate(query)
        if not is_valid:
            return ToolResult.error_result(error)

        try:

            with self.engine.connect() as conn:

                result = conn.execute(text(query))

                rows = result.fetchall()

                columns = result.keys()

                records = [dict(zip(columns, row)) for row in rows]

            return ToolResult.success_result(
                # output=str(records),
                output=json.dumps(records),
                metadata={"rows_returned": len(records)}
            )

        except Exception as e:

            return ToolResult.error_result(
                error=str(e),
                output="SQL execution failed"
            )
