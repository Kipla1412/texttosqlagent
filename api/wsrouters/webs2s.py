from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import base64
import json
import logging
from agent.events import AgentEventType
from agent.session import Session
from agent.agent import Agent
from api.auth import decode_token

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/chatting")
async def websocket_endpoint(websocket: WebSocket):

    # Try to get token from Authorization header first
    auth_header = websocket.headers.get("Authorization")
    token = None

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        # Fallback to query parameter
        query_params = websocket.query_params
        token = query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return

    try:
        user = decode_token(token)
        websocket.state.user = user
    except Exception:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    print("WebSocket connected")

    config = websocket.app.state.config

    # 2. CREATE PRIVATE SESSION for this caller
    # This keeps patient data isolated and safe
    connection_session = Session(config)
    await connection_session.initialize()

    agent = Agent(config)
    await agent.__aenter__()

    agent.session = connection_session
    # 3. LINK TOOLS to this specific connection
    for tool in connection_session.tool_registry.get_tools():
        if hasattr(tool, 'session'):
            tool.session = connection_session

    try:
        while True:

            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                print("Client disconnected")
                break

            audio_data = None

            if "text" in message:
                text_content = message["text"]

                if text_content.startswith("{"):
                    try:
                        data = json.loads(text_content)
                        # Handle other JSON messages here if needed in future
                    except Exception as e:
                        logger.error(f"JSON Parse Error: {e}")
                        continue

                # Handle Base64 Audio
                try:
                    audio_data = base64.b64decode(text_content)
                except: continue

            elif "bytes" in message:
                audio_data = message["bytes"]

            # elif "text" in message:
            #     text_content = message["text"]

                # if not text_content.startswith("{"):
                #     try:
                #         audio_data = base64.b64decode(text_content)
                #     except Exception:
                #         continue

            if not audio_data:
                continue

            async for event in agent.run_audio(audio_data, rate=16000, session=connection_session):

                if event.type == AgentEventType.USER_QUESTION:
                    await websocket.send_json({
                        "type": "user_question",
                        "content": event.data["content"]
                    })

                elif event.type == AgentEventType.TEXT_DELTA:
                    await websocket.send_json({
                        "type": "text",
                        "content": event.data["content"]
                    })

                elif event.type == AgentEventType.VOICE_OUTPUT:
                    await websocket.send_bytes(event.data["audio"])

                # elif event.type == AgentEventType.STOP_AUDIO:
                #     await websocket.send_json({
                #         "type": "stop_audio"
                #     })

                # elif event.type == AgentEventType.APPROVAL_REQUEST:

                #     approval_id = event.data["approval_id"]
                #     await websocket.send_json({
                #         "type": "approval_request",
                #         "approval_id": approval_id,
                #         "tool_name": event.data["tool_name"],
                #         "description": event.data["description"],
                #         "params": event.data.get("params", {})
                #     })

                elif event.type == AgentEventType.AGENT_ERROR:

                    error_msg = (
                        event.data.get("message")
                        or event.data.get("error")
                        or "Unknown Agent Error"
                    )

                    await websocket.send_json({
                        "type": "error",
                        "message": error_msg
                    })

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

    except Exception as e:
        logger.error(f"Runtime error: {e}")

        await websocket.send_json({ 
            "type": "error",
            "message": str(e)
        })
    finally:
        
        # 7. Cleanup the Private Session
        try:
            await agent.__aexit__(None, None, None)
        except Exception:
            pass

        if connection_session.client:
            await connection_session.client.close()

        logger.info("Connection session cleaned up")