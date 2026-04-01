import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from agent.agent import Agent
from config.config import Config
from fastapi.middleware.cors import CORSMiddleware
import base64

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
    print("WebSocket connection established")
    
    # Initialize your agent for this specific session
    try:
        # Skip MCP initialization for now to avoid timeout
        agent = Agent(cfg)
        await agent.session.initialize()
        print("Agent initialized successfully (MCP disabled)")

        for tool in agent.session.tool_registry.get_tools():
            if hasattr(tool, 'session'):
                tool.session = agent.session
        
        print("Agent & Tools initialized with Session linking")
        
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
                    # Handle potential JSON commands vs Base64 audio
                    text_content = message["text"]
                    if not text_content.startswith('{'): # Ignore JSON heartbeats
                        try:
                            audio_data = base64.b64decode(text_content)
                        except Exception:
                            continue
                
                if not audio_data:
                    continue
                
                # 2. Run your Speech-to-Speech logic
                # We use your run_audio method which yields events
                async for event in agent.run_audio(audio_data, rate=16000):
                    
                    # 3. Stream events back to frontend immediately
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

                    elif event.type == "stop_audio":
                        await websocket.send_json({
                            "type": "stop_audio"
                        })
                        
                    # Change this part in your websocket_endpoint:
                    elif event.type == "agent_error":
                        # Use .get() with a fallback to avoid KeyError
                        error_msg = event.data.get("message") or event.data.get("error") or "Unknown Agent Error"
                        
                        await websocket.send_json({
                            "type": "error", 
                            "message": error_msg
                        })

        except Exception as e:
            print(f"Runtime error: {e}")
            await websocket.send_json({
                "type": "error", 
                "message": f"Runtime error: {str(e)}"
            })
                    
    except Exception as e:
        print(f"Initialization error: {e}")
        await websocket.send_json({
            "type": "error", 
            "message": f"Initialization error: {str(e)}"
        })