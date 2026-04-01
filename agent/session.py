from datetime import datetime
import json
from typing import Any
import uuid
from client.llm_client import LLMClient
from config.config import Config
from config.loader import get_data_dir
from context.compaction import ChatCompactor
from context.loop_detector import LoopDetector
from context.manager import ContextManager
from hooks.hook_system import HookSystem
from safety.approval import ApprovalManager
from tools.discovery import ToolDiscoveryManager
from tools.registry import create_default_registry
from utils.mlflow_tracker import get_mlflow_tracker
from typing import List, Dict, Any, Optional

class Session:
    def __init__(self, config: Config):

        self.config = config
        self.client = LLMClient(config=config)
        self.tool_registry = create_default_registry(config=config)
        self.context_manager: ContextManager | None = None
        self.discovery_manager = ToolDiscoveryManager(
            self.config,
            self.tool_registry,
        )
        self.chat_compactor = ChatCompactor(self.client)
        self.approval_manager = ApprovalManager(
            self.config.approval,
            self.config.cwd,
        )

        # Add global MLflow tracker
        self.mlflow_tracker = get_mlflow_tracker(config)
        self.loop_detector = LoopDetector()
        self.hook_system = HookSystem(config)
        self.session_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        self.turn_count = 0
        self.mlflow_run_id: Optional[str] = None

        self.audio_buffer: list[bytes] = []
        self.silence_chunks: int = 0
        self.agent_speaking = False

    async def initialize(self) -> None:
        
        self.discovery_manager.discover_all()
        self.context_manager = ContextManager(
            config=self.config,
            user_memory=self._load_memory(),
            tools=self.tool_registry.get_tools(),
        )
        
        # Setup MLflow run for this session
        self.mlflow_run_id = self.mlflow_tracker.start_run(self.session_id)
        # Set session ID for trace tracking
        if self.mlflow_tracker.enabled:
            self.mlflow_tracker.current_session_id = self.session_id

    def _load_memory(self) -> str | None:
        data_dir = get_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        path = data_dir / "user_memory.json"

        if not path.exists():
            return None

        try:
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
            entries = data.get("entries")
            if not entries:
                return None

            lines = ["User preferences and notes:"]
            for key, value in entries.items():
                lines.append(f"- {key}: {value}")

            return "\n".join(lines)
        except Exception:
            return None

    def increment_turn(self) -> int:
        self.turn_count += 1
        self.updated_at = datetime.now()

        return self.turn_count

    def get_stats(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "turn_count": self.turn_count,
            "message_count": self.context_manager.message_count,
            "token_usage": self.context_manager.total_usage,
            "tools_count": len(self.tool_registry.get_tools()),
            # "mlflow_stats": self.mlflow_tracker.get_session_stats()
        }


    def reset_audio_buffer(self):
        self.audio_buffer = []
        self.silence_chunks = 0
        
    async def search_knowledge_base(self, query: str, limit: int = 5) -> list[dict]:
        """
        Convenience method to search knowledge base.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            # Get embedding for query
            async with self.embedding_connector as client:
                import httpx
                response = await client.post(
                    self.config.jina_api_url,
                    json={
                        "model": self.config.jina_model,
                        "task": "retrieval.query",
                        "dimensions": self.config.jina_dimensions,
                        "input": [query]
                    }
                )
                response.raise_for_status()
                vector = response.json()["data"][0]["embedding"]

            # Search OpenSearch with vector
            with self.opensearch_connector as client:
                search_body = {
                    "size": limit,
                    "_source": ["title", "content", "score"],
                    "query": {
                        "knn": {
                            "embedding": {
                                "vector": vector,
                                "k": limit
                            }
                        }
                    }
                }
                
                response = client.search(
                    index="knowledge-base",
                    body=search_body
                )
                
                hits = response["hits"]["hits"]
                results = []
                for hit in hits:
                    source = hit["_source"]
                    results.append({
                        "title": source.get("title", ""),
                        "content": source.get("content", ""),
                        "score": hit["_score"]
                    })
                
                return results
                
        except Exception as e:
            print(f"Knowledge base search error: {e}")
            return []

    def track_agent_interaction(
        self,
        user_message: str,
        agent_response: str,
        tools_used: List[str],
        session_duration: float,
        token_usage: Optional[Dict[str, int]] = None,
        success: bool = True
    ):
        """Track agent interaction using MLflow."""
        if self.mlflow_tracker:
            self.mlflow_tracker.log_agent_interaction(
                user_message=user_message,
                agent_response=agent_response,
                tools_used=tools_used,
                session_duration=session_duration,
                token_usage=token_usage,
                success=success
            )

    def track_tool_execution(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        execution_time: float,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Track tool execution using MLflow."""
        if self.mlflow_tracker:
            self.mlflow_tracker.log_tool_execution(
                tool_name=tool_name,
                tool_args=tool_args,
                execution_time=execution_time,
                success=success,
                error_message=error_message
            )

    def track_session_summary(
        self,
        total_interactions: int,
        total_duration: float,
        total_tools_used: int,
        success_rate: float
    ):
        """Track session summary using MLflow."""
        if self.mlflow_tracker:
            self.mlflow_tracker.log_session_summary(
                session_id=self.session_id,
                total_interactions=total_interactions,
                total_duration=total_duration,
                total_tools_used=total_tools_used,
                success_rate=success_rate
            )

    def cleanup(self):
        """Cleanup session resources."""
        if self.mlflow_tracker:
            self.mlflow_tracker.end_run()
