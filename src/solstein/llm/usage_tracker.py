_USAGE_RATES: dict[str, dict[str, tuple[float, float]]] = {
    "openai": {
        "gpt-4o-mini": (0.00015, 0.0006),
    },
    "groq": {
        "llama-3.3-70b-versatile": (0.00059, 0.00079),
    },
    "ollama": {},
}


class UsageTracker:
    def __init__(self) -> None:
        self.total_requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0
        self.costs_by_provider: dict[str, float] = {}

    def record_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        normalized_provider = provider.lower()
        normalized_model = model.lower()

        if normalized_provider == "ollama":
            cost = 0.0
        else:
            input_rate, output_rate = _USAGE_RATES.get(normalized_provider, {}).get(normalized_model, (0.0, 0.0))
            cost = (input_tokens / 1000) * input_rate + (output_tokens / 1000) * output_rate

        self.total_requests += 1
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_usd += cost
        self.costs_by_provider[normalized_provider] = self.costs_by_provider.get(normalized_provider, 0.0) + cost
        return cost

    def get_summary(self) -> dict[str, object]:
        return {
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost_usd": self.total_cost_usd,
            "costs_by_provider": dict(self.costs_by_provider),
        }


_usage_tracker: UsageTracker | None = None


def get_usage_tracker() -> UsageTracker:
    global _usage_tracker
    if _usage_tracker is None:
        _usage_tracker = UsageTracker()
    return _usage_tracker
