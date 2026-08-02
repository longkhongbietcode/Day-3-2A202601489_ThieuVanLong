"""
Multi-provider LLM adapter.

Supported providers: Gemini, OpenAI, Anthropic, OpenRouter, and offline Mock.
The file intentionally uses ASCII text to avoid encoding issues on Windows.
"""

import os
import sys

import requests
from dotenv import load_dotenv


if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


load_dotenv()


class BaseLLMProvider:
    """Base interface for all LLM providers."""

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: GEMINI_API_KEY is not configured in .env."
        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents,
            )
            return response.text
        except Exception as exc:
            return f"[Gemini Exception]: {exc}"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: OPENAI_API_KEY is not configured in .env."
        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as exc:
            return f"[OpenAI Exception]: {exc}"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "claude-3-haiku-20240307"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_anthropic_api_key_here":
            return "[Anthropic Error]: ANTHROPIC_API_KEY is not configured in .env."
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as exc:
            return f"[Anthropic Exception]: {exc}"


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter provider."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "google/gemini-2.5-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return "[OpenRouter Error]: OPENROUTER_API_KEY is not configured in .env."
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model_name,
                "messages": messages,
            }
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            return f"[OpenRouter API Error {response.status_code}]: {response.text}"
        except Exception as exc:
            return f"[OpenRouter Exception]: {exc}"


class MockProvider(BaseLLMProvider):
    """Offline mock provider for local lab testing without API keys."""

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        text = prompt.lower()
        if "data analyst" in text:
            return (
                "Data Analyst thuong thu thap, lam sach, phan tich du lieu va tao bao cao "
                "de ho tro ra quyet dinh. Ky nang nen co gom Excel, SQL, Python co ban, "
                "thong ke va truc quan hoa du lieu."
            )
        if "ky nang mem" in text:
            return (
                "Ba ky nang mem quan trong la giao tiep ro rang, lam viec nhom va quan ly thoi gian. "
                "Sinh vien cung nen ren luyen tu duy phan hoi va kha nang trinh bay."
            )
        if "ceo" in text or "dam bao" in text:
            return (
                "Toi khong the dam bao ban thanh CEO trong 1 thang. "
                "Ban nen bat dau bang muc tieu thuc te hon nhu hoc mot ky nang nen tang va lam mot project nho."
            )
        return (
            "[Mock Provider]: Day la phan hoi baseline offline. "
            "Cau hoi ca nhan hoa nen can agent dung tool de danh gia ky nang, so thich va lo trinh."
        )


def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """Create a provider from LLM_PROVIDER or the explicit provider name."""
    name = (provider_name or os.getenv("LLM_PROVIDER") or "mock").lower().strip()

    if name == "gemini":
        return GeminiProvider()
    if name == "openai":
        return OpenAIProvider()
    if name == "anthropic":
        return AnthropicProvider()
    if name == "openrouter":
        return OpenRouterProvider()
    return MockProvider()


if __name__ == "__main__":
    print("=== TEST MULTI-PROVIDER LLM ADAPTER ===")
    provider = get_llm_provider()
    print(f"Provider: {provider.__class__.__name__}")
    print("User Query: Hello")
    print(f"Response: {provider.generate('Hello')}")
