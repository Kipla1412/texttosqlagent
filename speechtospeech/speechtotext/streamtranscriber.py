import asyncio

class StreamTranscriber:

    def __init__(self, engine):
        self.engine = engine
        self.buffer = []
        self.silence_count = 0

    async def process_chunk(self, chunk, rate):

        processed = self.engine.processor.process(chunk, rate)
        audio_bytes = self.engine.processor.to_bytes(processed)

        try:
            text = await asyncio.to_thread(
                self.engine.provider.transcribe,
                audio_bytes
            )
        except Exception as e:
            print("STT error:", e)
            return None


        if text and text.strip():
            self.silence_count = 0
            self.buffer.append(text)
            print("Partial:", text)

        else:
            self.silence_count += 1

        # silence detection
        if self.silence_count > 3:
            final_text = " ".join(self.buffer)
            self.buffer = []
            self.silence_count = 0

            return final_text

        return None
