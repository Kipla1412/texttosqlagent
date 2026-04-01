from fastapi import APIRouter, Request
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import json

router = APIRouter(prefix="/agent")


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


@router.post("/chat")
async def chat(req: ChatRequest, request: Request):

    agent = request.app.state.agent

    async def event_stream():

        async for event in agent.run(req.message):

            yield json.dumps({
                "type": event.type.value if hasattr(event.type, "value") else str(event.type),
                "data": event.data
            }) + "\n"

    return StreamingResponse(event_stream(), media_type="application/json; charset=utf-8")