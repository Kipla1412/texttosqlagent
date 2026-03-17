from __future__ import annotations

import duckdb
from pydantic import BaseModel
from tools.base import Tool, ToolInvocation, ToolKind, ToolResult
from config.config import Config

class DuckDBConnectionManager:

    _conn = None

    @classmethod
    def get_connection(cls):

        if cls._conn is None:
            cls._conn = duckdb.connect()

        return cls._conn
        
class DuckDBQueryParams(BaseModel):
    query: str
    user_id: int

class DuckDBHealthQueryTool(Tool):

    name = "duckdb_health_query"
    description = """
Execute SQL queries on the user's health datasets.

Available tables:

1. daily_summary
Columns:
Source: summary_df_*.csv
pseudo_id2, datetime, age, gender, weight_kg, resting_heart_rate,
heart_rate_variability, steps, rem_sleep_minutes, deep_sleep_minutes,
awake_minutes, light_sleep_minutes, sleep_minutes, bed_time, wake_up_time,
stress_management_score, deep_sleep_percent, rem_sleep_percent,
awake_percent, light_sleep_percent, height_cm

2. exercise_sessions
Source: exercise_df_*.csv
Columns:
pseudo_id2, date, duration, activityName, startTime, endTime,
averageHeartRate, elevationGain, distance, calories, steps,
activeZoneMinutes, speed

Use SQL to compute statistics, trends, or correlations.
"""
    kind = ToolKind.READ
    schema = DuckDBQueryParams

    def __init__(self, config: Config):
        super().__init__(config)

        # Create DuckDB connection
        self.conn = DuckDBConnectionManager.get_connection()

        # Register datasets
        self._register_tables()

    def _register_tables(self):
        """
        Register CSV datasets as DuckDB views
        """

        try:
            self.conn.execute("""
            CREATE OR REPLACE VIEW daily_summary AS
            SELECT *
            FROM read_csv_auto('data/summary_df_*.csv')
            """)

            self.conn.execute("""
            CREATE OR REPLACE VIEW exercise_sessions AS
            SELECT *
            FROM read_csv_auto('data/exercise_df_*.csv')
            """)

        except Exception as e:
            print(f"DuckDB table registration failed: {e}")

    def _inject_user_filter(self, query: str, user_id: int) -> str:
        """
        Safely inject pseudo_id2 filter into SQL query
        """

        query = query.strip().rstrip(";")

        if "pseudo_id2" in query.lower():
            return query

        # Find position of GROUP BY / ORDER BY / LIMIT
        pattern = re.search(r"\b(group by|order by|limit)\b", query, re.IGNORECASE)

        if pattern:
            idx = pattern.start()
            main = query[:idx]
            tail = query[idx:]

            if "where" in main.lower():
                main = f"{main} AND pseudo_id2 = {user_id}"
            else:
                main = f"{main} WHERE pseudo_id2 = {user_id}"

            return f"{main} {tail}"

     
        if "where" in query.lower():
            return f"{query} AND pseudo_id2 = {user_id}"
            
        return f"{query} WHERE pseudo_id2 = {user_id}"
                
    async def execute(self, invocation: ToolInvocation) -> ToolResult:

        query = invocation.params.get("query")
        user_id = invocation.params.get("user_id")

        if not query:
            return ToolResult.error_result("Missing SQL query")

        if user_id is None:
            return ToolResult.error_result("Missing user_id")

        try:
            
            safe_query = self._inject_user_filter(query, user_id)
                
            df = self.conn.execute(safe_query).fetchdf()
            # Limit large outputs for LLM safety
            df = df.head(100)

            result_json = df.to_json(orient="records")

            return ToolResult.success_result(
                output=result_json,
                metadata={
                    "rows_returned": len(df),
                    "query": safe_query
                }
            )

        except Exception as e:
            return ToolResult.error_result(
                error=str(e),
                output="SQL execution failed"
            )