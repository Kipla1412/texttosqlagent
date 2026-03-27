import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from agent.agent import Agent
from config.config import Config
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
cfg = Config()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, "*" allows everything
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/chatting")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Initialize your agent for this specific session
    async with Agent(cfg) as agent:
        try:
            while True:
                # 1. Receive Audio Bytes from Browser
                message = await websocket.receive()

                if message["type"] == "websocket.disconnect":
                    print("Client disconnected")
                    break

                audio_data = None

                if "bytes" in message:
                    audio_data = message["bytes"]
                
                elif "text" in message:
                    try:
                        import base64
                        # We only decode if it looks like base64
                        audio_data = base64.b64decode(message["text"])
                    except Exception:
                        print("DEBUG: Received text but it wasn't valid Base64")
                        continue

                if not audio_data:
                    continue
                
                # 2. Run your Speech-to-Speech logic
                # We use your run_audio method which yields events
                async for event in agent.run_audio(audio_data, rate=16000):
                    
                    # 3. Stream events back to the frontend immediately
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
                        # Send raw PCM/WAV bytes back to be played
                        await websocket.send_bytes(event.data["audio"])
                        
                    # Change this part in your websocket_endpoint:
                    elif event.type == "agent_error":
                        # Use .get() with a fallback to avoid KeyError
                        error_msg = event.data.get("message") or event.data.get("error") or "Unknown Agent Error"
                        await websocket.send_json({
                            "type": "error", 
                            "message": error_msg
                        })

        except WebSocketDisconnect:
            print("Client disconnected")