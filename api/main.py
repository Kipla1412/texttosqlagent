"""
FastAPI application module
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import logging
 
from agent.agent import Agent
from config.config import Config
from api.routers.agent import router as agent_router
from api.wsrouters.webs2s import router as websocket_router
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting Alees AI Agent Runtime")

    # Load configuration
    config = Config()

    # Create agent runtime
    agent = Agent(config)
   
    try:
        # 3. Initialize the global session/client
        await agent.session.initialize()
        
        # We link the session here so that any route using 'get_agent' 
        for tool in agent.session.tool_registry.get_tools():
            if hasattr(tool, 'session'):
                tool.session = agent.session
        
        # 4. Store inside FastAPI app state for global access
        app.state.config = config
        app.state.agent = agent
        app.state.pending_approvals = agent.session.pending_approvals
        logger.info("Agent initialized and Tools linked successfully")
        logger.info(f"Approval policy: {config.approval}")
        
    except Exception as e:
        logger.error(f"Critical Failure during Agent Startup: {e}")
        raise e

    yield

    logger.info("Shutting down agent runtime")

    # Optional cleanup
    if agent.session and agent.session.client:
        await agent.session.client.close()


# Create FastAPI application
def create_app():

    app = FastAPI(
        title="AI Agent API",
        version="1.0",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    app.include_router(agent_router, prefix="/api")
    app.include_router(websocket_router)
    
    # Mount static files for approval dashboard
    app.mount("/static", StaticFiles(directory="static"), name="static")

    return app


# Global app instance
app = create_app()


# Helper function to get agent
def get_agent(request: Request) -> Agent:
    return request.app.state.agent