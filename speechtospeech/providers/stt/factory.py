from .huggingface import HuggingFaceSTTProvider
from .openaiprovider import OpenAISTTProvider


def create_stt_provider(provider_name: str, **kwargs):

    provider_name = provider_name.lower()

    if provider_name == "huggingface":
        return HuggingFaceSTTProvider(
           
            api_key=kwargs.get("api_key"),
            model=kwargs.get("model", "openai/whisper-large-v3"),
            #endpoint_url=kwargs.get("endpoint_url"),
            debug=kwargs.get("debug", False)
        )

    elif provider_name == "openai":
        return OpenAISTTProvider(
            api_key=kwargs.get("api_key"),
            model=kwargs.get("modael", "gpt-4o-mini-transcribe")
        )

    else:
        raise ValueError(f"Unsupported provider: {provider_name}")