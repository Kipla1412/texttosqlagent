from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy import text
from config.config import Config
import logging

logger = logging.getLogger(__name__)

config = Config()

class PostgresConnectionManager:

    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker | None = None

    @classmethod
    async def get_engine(cls) -> AsyncEngine:
        """
        Returns a singleton async SQLAlchemy engine instance.
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
                cls._engine = create_async_engine(
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
                async with cls._engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
                
                # Create session factory
                cls._session_factory = async_sessionmaker(
                    cls._engine,
                    expire_on_commit=False
                )
                
                logger.info("PostgreSQL async engine initialized")

            except Exception as e:
                logger.error(f"Failed to initialize database engine: {e}")
                raise

        return cls._engine

    @classmethod
    async def get_session(cls):
        """
        Returns a database session.
        """
        if cls._session_factory is None:
            await cls.get_engine()
        return cls._session_factory()

    @classmethod
    def get_sync_engine(cls):
        """
        Fallback method for sync operations.
        Converts asyncpg URL to psycopg2 for sync operations.
        """
        database_url = config.database_url
        if database_url and "postgresql+asyncpg://" in database_url:
            # Convert asyncpg URL to psycopg2 for sync operations
            sync_url = database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
            from sqlalchemy import create_engine
            return create_engine(sync_url)
        
        # Fallback to original sync engine if URL doesn't need conversion
        from sqlalchemy import create_engine
        return create_engine(database_url)