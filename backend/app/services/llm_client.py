from dataclasses import dataclass, asdict
from app.core.config import settings

@dataclass
class LLMUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    cost_mode: str = 'estimate'

    def to_dict(self):
        return asdict(self)

class LLMClient:
    def __init__(self):
        if not settings.ai_api_key:
            raise ValueError('AI_API_KEY is not configured')
        from openai import OpenAI
        self.client = OpenAI(
            api_key=settings.ai_api_key,
            timeout=settings.ai_timeout_seconds,
            max_retries=settings.ai_max_retries,
        )

    @staticmethod
    def _usage_from_response(response) -> LLMUsage:
        usage = getattr(response, 'usage', None)
        if usage is None:
            return LLMUsage()
        def pick(name: str) -> int:
            if isinstance(usage, dict):
                return int(usage.get(name, 0) or 0)
            return int(getattr(usage, name, 0) or 0)
        input_tokens = pick('input_tokens')
        output_tokens = pick('output_tokens')
        total_tokens = pick('total_tokens') or input_tokens + output_tokens
        estimated = (
            input_tokens / 1_000_000 * settings.estimated_input_usd_per_million
            + output_tokens / 1_000_000 * settings.estimated_output_usd_per_million
        )
        return LLMUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=round(estimated, 6),
        )

    def generate_with_meta(self, instructions: str, payload: str) -> tuple[str, dict]:
        response = self.client.responses.create(
            model=settings.ai_model,
            instructions=instructions,
            input=payload,
        )
        return response.output_text, self._usage_from_response(response).to_dict()

    def generate(self, instructions: str, payload: str) -> str:
        text, _ = self.generate_with_meta(instructions, payload)
        return text
