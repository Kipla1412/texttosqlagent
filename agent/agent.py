from __future__ import annotations
from typing import AsyncGenerator, Awaitable, Callable
from agent.events import AgentEvent, AgentEventType
from agent.session import Session
from client.response import StreamEventType, TokenUsage, ToolCall, ToolResultMessage, parse_tool_call_arguments
from config.config import Config
from prompts.system import create_loop_breaker_prompt
from tools.base import ToolConfirmation
import json
import time
from datetime import datetime
import asyncio

class Agent:
    def __init__(
        self,
        config: Config,
        confirmation_callback: Callable[[ToolConfirmation], bool] | None = None,
    ):
        self.config = config
        self.session: Session | None = Session(self.config)
        self.session.approval_manager.confirmation_callback = confirmation_callback

    async def run(self, message: str):
        
        await self.session.hook_system.trigger_before_agent(message)
        yield AgentEvent.agent_start(message)
        self.session.context_manager.add_user_message(message)

        final_response: str | None = None

        async for event in self._agentic_loop():
            yield event

            if event.type == AgentEventType.TEXT_COMPLETE:
                final_response = event.data.get("content")

        await self.session.hook_system.trigger_after_agent(message, final_response)
        
        # Track agent interaction with MLflow
        session_duration = (
            datetime.now() - self.session.created_at
        ).total_seconds()

        # Extract tools used and token usage from the session
        tools_used = []  # You can populate this from the session context
        token_usage = None  # You can extract this from the LLM client response
        
        self.session.track_agent_interaction(
            user_message=message,
            agent_response=final_response or "",
            tools_used=tools_used,
            session_duration=session_duration,
            token_usage=token_usage,
            success=final_response is not None
        )
        
        yield AgentEvent.agent_end(final_response)

    async def _agentic_loop(self) -> AsyncGenerator[AgentEvent, None]:
        max_turns = self.config.max_turns

        for turn_num in range(max_turns):
            self.session.increment_turn()
            response_text = ""

            # check for context overflow
            if self.session.context_manager.needs_compression():
                summary, usage = await self.session.chat_compactor.compress(
                    self.session.context_manager
                )

                if summary:
                    self.session.context_manager.replace_with_summary(summary)
                    self.session.context_manager.set_latest_usage(usage)
                    self.session.context_manager.add_usage(usage)

            tool_schemas = self.session.tool_registry.get_schemas()

            tool_calls: list[ToolCall] = []
            usage: TokenUsage | None = None

            async for event in self.session.client.chat_completion(
                self.session.context_manager.get_messages(),
                tools=tool_schemas if tool_schemas else None,
            ):
                if event.type == StreamEventType.TEXT_DELTA:
                    if event.text_delta:
                        content = event.text_delta.content
                        response_text += content
                        yield AgentEvent.text_delta(content)
                elif event.type == StreamEventType.TOOL_CALL_COMPLETE:
                    if event.tool_call:
                        tool_calls.append(event.tool_call)
                elif event.type == StreamEventType.ERROR:
                    yield AgentEvent.agent_error(
                        event.error or "Unknown error occurred.",
                    )
                elif event.type == StreamEventType.MESSAGE_COMPLETE:
                    usage = event.usage

            self.session.context_manager.add_assistant_message(
                response_text or "",
                (
                    [
                        {
                            "id": tc.call_id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments),
                            },
                        }
                        for tc in tool_calls
                    ]
                    if tool_calls
                    else None
                ),
            )
            if response_text:
                yield AgentEvent.text_complete(response_text)
                self.session.loop_detector.record_action(
                    "response",
                    text=response_text,
                )

            if not tool_calls:
                if usage:
                    self.session.context_manager.set_latest_usage(usage)
                    self.session.context_manager.add_usage(usage)

                self.session.context_manager.prune_tool_outputs()
                return

            tool_call_results: list[ToolResultMessage] = []

            for tool_call in tool_calls:
                yield AgentEvent.tool_call_start(
                    tool_call.call_id,
                    tool_call.name,
                    tool_call.arguments,
                )

                self.session.loop_detector.record_action(
                    "tool_call",
                    tool_name=tool_call.name,
                    args=tool_call.arguments,
                )
                # parsed_args = parse_tool_call_arguments(tool_call.arguments)
                
                print(f"DEBUG: Tool {tool_call.name} called with args: {tool_call.arguments}")
                
                # start_time = time.time()
                result = await self.session.tool_registry.invoke(
                    tool_call.name,
                    tool_call.arguments,
                    self.config.cwd,
                    self.session.hook_system,
                    self.session.approval_manager,
                )
                

                yield AgentEvent.tool_call_complete(
                    tool_call.call_id,
                    tool_call.name,
                    result,
                )

                tool_call_results.append(
                    ToolResultMessage(
                        tool_call_id=tool_call.call_id,
                        content=result.to_model_output(),
                        is_error=not result.success,
                    )
                )

            for tool_result in tool_call_results:
                self.session.context_manager.add_tool_result(
                    tool_result.tool_call_id,
                    tool_result.content,
                )

            loop_detection_error = self.session.loop_detector.check_for_loop()
            if loop_detection_error:
                loop_prompt = create_loop_breaker_prompt(loop_detection_error)
                self.session.context_manager.add_user_message(loop_prompt)

            if usage:
                self.session.context_manager.set_latest_usage(usage)
                self.session.context_manager.add_usage(usage)

            self.session.context_manager.prune_tool_outputs()
        yield AgentEvent.agent_error(f"Maximum turns ({max_turns}) reached")

    # async def run_audio(self, audio, rate):

    #     import io
    #     import soundfile as sf
    #     import numpy as np

    #     # 1. STT
    #     stt_engine = self.config.stt_engine

    #     processed = stt_engine.processor.process(audio, rate)
    #     audio_bytes = stt_engine.processor.to_bytes(processed)

    #     try:
           
    #         user_text = await asyncio.to_thread(
    #             stt_engine.provider.transcribe,
    #             audio_bytes
    #         )
    #     except Exception as e:
    #         yield AgentEvent.agent_error(f"STT Error: {str(e)}")
    #         return

    #     # handle empty speech
    #     if not user_text.strip():
    #         yield AgentEvent.agent_error("No speech detected")
    #         return

    #     # 2. Run normal agent (NO extra agent_start)
    #     async for event in self.run(user_text):
    #         yield event

    #         # 3. Convert final response → speech
    #         if event.type == AgentEventType.TEXT_COMPLETE:

    #             try:
    #                 tts = self.config.tts_engine

    #                 audio_out, sr = await asyncio.to_thread(tts.synthesize, event.data["content"])

    #                 # use helper method
    #                 yield AgentEvent.voice_output(audio_out, sr)

    #             except Exception as e:
    #                 yield AgentEvent.agent_error(f"TTS Error: {str(e)}")


    async def run_audio(self, audio, rate):
        import io
        import soundfile as sf
        import numpy as np

        # Initialize session-level buffers
        if not hasattr(self.session, '_audio_buffer'):
            self.session._audio_buffer = []
            self.session._silence_chunks = 0
        
        # Add new audio chunk to buffer
        self.session._audio_buffer.append(audio)
        
        # Calculate energy for this chunk
        audio_array = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 32768.0
        energy = np.mean(audio_array ** 2)
        energy_db = 10 * np.log10(energy + 1e-10)
        
        print(f"DEBUG: Chunk energy: {energy_db:.2f} dB, Buffer size: {len(self.session._audio_buffer)}")
        
        # Check if this is silence (below threshold)
        if energy_db < -35:  # More sensitive threshold
            self.session._silence_chunks += 1
            print(f"DEBUG: Silence chunks: {self.session._silence_chunks}")
        else:
            self.session._silence_chunks = 0
        
        # Process if we have speech followed by silence (user finished speaking)
        if len(self.session._audio_buffer) > 5 and self.session._silence_chunks >= 3:  # More responsive
            print("DEBUG: User finished speaking, processing...")
            
            # Combine all buffered audio
            total_audio = b''.join(self.session._audio_buffer)
            
            # Reset buffers
            self.session._audio_buffer = []
            self.session._silence_chunks = 0
            
            # Only process if we have enough audio (at least 0.5 seconds)
            min_bytes = int(16000 * 0.5 * 2)
            if len(total_audio) < min_bytes:
                print("DEBUG: Too short, ignoring")
                return
        else:
            # Keep collecting audio
            return

        # 1. STT Setup
        stt_engine = self.config.stt_engine
        
        try:
            # Convert raw bytes to Numpy Array
            raw_audio_array = (
                np.frombuffer(total_audio, dtype=np.int16)
                .astype(np.float32) / 32768.0
            )

            samplerate = 16000
            # Now the processor can handle it because it's an array with .ndim
            processed = stt_engine.processor.process(raw_audio_array, samplerate)
            audio_bytes = stt_engine.processor.to_bytes(processed)

            # 2. Transcribe (using to_thread because it's a blocking network call)
            user_text = await asyncio.to_thread(
                stt_engine.provider.transcribe,
                audio_bytes
            )
            
            # DEBUG: Log what STT returned
            print(f"DEBUG: STT returned: '{user_text}' (length: {len(user_text) if user_text else 0})")
            
        except Exception as e:
            print(f"DEBUG: STT Exception: {str(e)}")
            yield AgentEvent.agent_error(f"STT/Processing Error: {str(e)}")
            return

        # Handle empty speech
        if not user_text or not user_text.strip():
            print("DEBUG: No speech detected or empty transcription")
            yield AgentEvent.agent_error("No speech detected - please speak clearly")
            return

        # Filter out very short transcriptions (likely noise)
        clean_text = user_text.strip()

        if len(clean_text) < 3:
            print("DEBUG: Transcription too short, likely noise")
            return

        # Send user question to frontend
        yield AgentEvent.user_question(user_text.strip())

        # 3. Run normal agent loop
        async for event in self.run(user_text):
            yield event

            # 4. Convert final response → speech
            if event.type == AgentEventType.TEXT_COMPLETE:
                try:
                    tts = self.config.tts_engine
                    
                    # Wrap synthesize in to_thread so it doesn't block the async loop
                    audio_out, sr = await asyncio.to_thread(
                        tts.synthesize, 
                        event.data["content"]
                    )
                    audio_bytes = tts.processor.array_to_wav_bytes(audio_out, sr)
                    yield AgentEvent.voice_output(audio_bytes, sr)

                except Exception as e:
                    yield AgentEvent.agent_error(f"TTS Error: {str(e)}")
                    
    async def __aenter__(self) -> Agent:
        await self.session.initialize()
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_val,
        exc_tb,  
    ) -> None:
        if self.session and self.session.client and self.session.mcp_manager:
            await self.session.client.close()
            await self.session.mcp_manager.shutdown()
            # Cleanup MLflow run
            self.session.cleanup()
            self.session = None
