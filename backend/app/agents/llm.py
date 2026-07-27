"""
Single place to instantiate the chat model so every agent uses the same
provider/model configuration.

MODEL_PROVIDER options:
  - "ollama"    free, runs locally via Ollama, no API key or cost (default for
                a zero-cost setup — requires the Ollama app running on your Mac)
  - "anthropic" paid, Claude models via the Anthropic API
  - "openai"    paid, GPT models via the OpenAI API
"""
from app.core.config import get_settings

settings = get_settings()


def get_chat_model(temperature: float = 0.0):
    if settings.model_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=settings.chat_model, temperature=temperature, api_key=settings.openai_api_key)

    if settings.model_provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=settings.chat_model, temperature=temperature, api_key=settings.anthropic_api_key)

    # Free local default: Ollama
    from langchain_ollama import ChatOllama

    return ChatOllama(model=settings.chat_model, temperature=temperature, base_url=settings.ollama_base_url)
