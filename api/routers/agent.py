from fastapi import APIRouter, Request, Depends
from api.auth import get_current_user, require_permission
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import json
import uuid

from agent.agent import Agent

router = APIRouter(prefix="/agent")


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


@router.post(
    "/texttosqlagent",
    summary="Healthcare Data Query Assistant",
    description="""
AI-powered healthcare data analysis and natural language responses.

This endpoint processes natural language questions about healthcare data,
executes SQL queries, and returns conversational explanations of results.

Perfect for healthcare professionals, researchers, and data analysts who need
quick insights from patient records, appointments, and medical data.

Key Features:
- Natural language to SQL query conversion
- Real-time streaming responses
- Conversational explanations of data insights
- Session-based conversation context
- Multi-table healthcare database queries
- Tool execution with approval workflow

Use Cases:
- Patient data analysis and reporting
- Appointment scheduling and management
- Healthcare provider queries
- Medical data insights and trends
- Research and analytics queries

Authentication:
Requires valid authenticated user session with healthcare data access.

Permission Required:
`texttosqlagent:chat` - Healthcare data query access
""",
    dependencies=[Depends(require_permission("texttosqlagent", "chat"))]
)
async def chat(req: ChatRequest, request: Request):

    sessions = request.app.state.sessions
    config = request.app.state.config

    user = request.state.user
    # Generate session id if missing
    user_id = user.get("sub")
    session_id = req.session_id or str(uuid.uuid4())

    
    if user_id not in sessions:

        agent = Agent(config)
        await agent.__aenter__()

        sessions[user_id] = agent

    agent = sessions[user_id]

    async def event_stream():

        async for event in agent.run(req.message):

            yield json.dumps({
                "type": event.type.value if hasattr(event.type, "value") else str(event.type),
                "data": event.data
            }) + "\n"

    return StreamingResponse(
        event_stream(),
        media_type="application/json; charset=utf-8",
        headers={"X-Session-ID": session_id}
    )

# from fastapi import APIRouter, Request
# from pydantic import BaseModel
# from fastapi.responses import StreamingResponse
# import json
# from agent.agent import Agent
# from config.config import Config

# router = APIRouter(prefix="/agent")


# class ChatRequest(BaseModel):
#     message: str
#     session_id: str | None = None


# @router.post("/chat")
# async def chat(req: ChatRequest, request: Request):

#     sessions = request.app.state.sessions
#     config = request.app.state.config

#     if req.session_id not in sessions:
#         # First time this user has messaged? Give them a private agent.
#         agent = Agent(Config())
#         await agent.__aenter__()
#         sessions[req.session_id] = agent
    
#     # Use their private agent
#     agent = sessions[req.session_id]

#     async def event_stream():

#         async for event in agent.run(req.message):

#             yield json.dumps({
#                 "type": event.type.value if hasattr(event.type, "value") else str(event.type),
#                 "data": event.data
#             }) + "\n"

#     return StreamingResponse(event_stream(), media_type="application/json; charset=utf-8")

# @router.post("/approve")
# async def approve(data: dict, request: Request):

#     approval_id = data["approval_id"]
#     approved = data["approved"]

#     agent = request.app.state.agent
#     pending = agent.session.pending_approvals

#     if approval_id not in pending:
#         return {"status": "not_found", "approval_id": approval_id}
    
#     future = pending[approval_id]

#     if not future.done():
#         future.set_result(approved)

#     return {
#         "status": "ok",
#         "approval_id": approval_id,
#         "approved": approved
#     }