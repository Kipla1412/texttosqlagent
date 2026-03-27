class TranscriptionEngine:

    def __init__(self, provider, processor, chunk=10):
        self.provider = provider
        self.processor = processor
        self.chunk = chunk

    def split(self, raw, rate):
        step = int(rate * self.chunk)
        return [(raw[i:i+step], rate) for i in range(0, len(raw), step)]

    def transcribe(self, raw, rate):

        results = []

        for chunk, r in self.split(raw, rate):

            processed = self.processor.process(chunk, r)
            audio_bytes = self.processor.to_bytes(processed)

            text = self.provider.transcribe(audio_bytes)

            if text:
                results.append(text)

        return " ".join(results)