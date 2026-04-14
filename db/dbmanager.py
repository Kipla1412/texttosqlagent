from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy import text
from config.config import Config
import logging

logger = logging.getLogger(__name__)

config = Config()

class PostgresConnectionManager:

    _engine: Engine | None = None

    @classmethod
    def get_engine(cls) -> Engine:
        """
        Returns a singleton SQLAlchemy engine instance.
        Uses connection pooling and health checks.
        """

        if cls._engine is None:

            database_url = config.database_url
            # print("DATABASE_URL:", database_url)

            if not database_url:
                raise RuntimeError(
                    "DATABASE_URL environment variable is not set"
                )

            try:
                cls._engine = create_engine(
                    database_url,

                    # connection pool settings
                    pool_size=5,
                    max_overflow=10,
                    pool_timeout=30,
                    pool_recycle=1800,

                    # automatically check stale connections
                    pool_pre_ping=True,

                    # disable verbose SQL logs in production
                    echo=False,
                )

                # test connection
                with cls._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                logger.info("PostgreSQL engine initialized")

            except Exception as e:
                logger.error(f"Failed to initialize database engine: {e}")
                raise

        return cls._engine