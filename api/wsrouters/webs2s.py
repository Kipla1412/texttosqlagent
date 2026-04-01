from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import base64

router = APIRouter()


@router.websocket("/ws/chatting")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()
    print("WebSocket connected")

    agent = websocket.app.state.agent

    try:
        while True:

            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                print("Client disconnected")
                break

            audio_data = None

            if "bytes" in message:
                audio_data = message["bytes"]

            elif "text" in message:
                text_content = message["text"]

                if not text_content.startswith("{"):
                    try:
                        audio_data = base64.b64decode(text_content)
                    except Exception:
                        continue

            if not audio_data:
                continue

            async for event in agent.run_audio(audio_data, rate=16000):

                if event.type == "user_question":
                    await websocket.send_json({
                        "type": "user_question",
                        "content": event.data["content"]
                    })

                elif event.type == "text_delta":
                    await websocket.send_json({
                        "type": "text",
                        "content": event.data["content"]
                    })

                elif event.type == "voice_output":
                    await websocket.send_bytes(event.data["audio"])

                elif event.type == "stop_audio":
                    await websocket.send_json({
                        "type": "stop_audio"
                    })

                elif event.type == "agent_error":

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
        print("WebSocket disconnected")

    except Exception as e:
        print(f"Runtime error: {e}")

        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })