import numpy as np


class VoiceActivityDetector:
    """
    Simple WebRTC Voice Activity Detector.
    """

    def __init__(self, aggressiveness: int = 2, sample_rate: int = 16000):
        """
        aggressiveness: 0–3 (higher = more aggressive filtering)
        sample_rate: audio sample rate
        """
        self.sample_rate = sample_rate
        # Energy threshold based on aggressiveness
        self.energy_threshold = 0.001 * (4 - aggressiveness)  # Higher aggressiveness = lower threshold
        self.min_duration = 0.01  # Minimum 10ms of speech

    def is_speech(self, audio_chunk: bytes) -> bool:
        """
        Detect if chunk contains speech using energy.

        Args:
            audio_chunk: raw PCM int16 bytes

        Returns:
            True if speech detected
        """
        try:
            # Convert bytes to numpy array
            audio = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Calculate RMS energy
            energy = np.sqrt(np.mean(audio ** 2))
            
            # Use a more reasonable threshold
            # Normal speech has energy around 0.01-0.1, silence is < 0.001
            return energy > self.energy_threshold
            
        except Exception:
            return False