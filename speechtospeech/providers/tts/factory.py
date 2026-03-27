from .openai import OpenAITTSProvider
from .huggingface import HuggingFaceTTSProvider
from .groq import GroqTTSProvider


def create_tts_provider(provider_name: str, **kwargs):

    provider_name = provider_name.lower()

    if provider_name == "openai":
        return OpenAITTSProvider(
            api_key=kwargs.get("api_key"),
            model=kwargs.get("model")
        )

    elif provider_name == "huggingface":
        return HuggingFaceTTSProvider(
            api_key=kwargs.get("api_key"),
            model=kwargs.get("model")
        )

    elif provider_name == "groq":
        return GroqTTSProvider(
            api_key=kwargs.get("api_key"),
            model=kwargs.get("model"),
            endpoint_url="https://api.groq.com/openai/v1/audio/speech"
        )

    else:
        raise ValueError(f"Unsupported TTS provider: {provider_name}")