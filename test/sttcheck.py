# import asyncio
# import sounddevice as sd
# import numpy as np

# from config.config import Config
# from src.speechtospeech.speechtotext.streamtranscriber import StreamTranscriber


# RATE = 16000
# CHUNK_DURATION = 1  # seconds


# async def main():

#     config = Config()
#     engine = config.stt_engine

#     streamer = StreamTranscriber(engine)

#     print("🎤 Live streaming started...")

#     while True:

#         # 🎙️ record chunk
#         audio = sd.rec(
#             int(CHUNK_DURATION * RATE),
#             samplerate=RATE,
#             channels=1
#         )
#         sd.wait()

#         audio = np.squeeze(audio)

#         result = await streamer.process_chunk(audio, RATE)

#         if result:

#             if "partial" in result:
#                 print("🟡 Partial:", result["partial"])

#             if "final" in result:
#                 print("🟢 Final:", result["final"])


# asyncio.run(main())

import soundfile as sf
from config.config import Config

# load config
config = Config()

# load your STT engine
engine = config.stt_engine

# read recorded audio
audio, rate = sf.read(r"/home/kipla/aiagent/ai-coding-agent/test/output.wav")

print("Audio shape:", audio.shape)
print("Sample rate:", rate)

# process audio
processed = engine.processor.process(audio, rate)

# convert to bytes
audio_bytes = engine.processor.to_bytes(processed)

# send to STT
text = engine.provider.transcribe(audio_bytes)

print("\n🧠 Transcription:")
print(text)