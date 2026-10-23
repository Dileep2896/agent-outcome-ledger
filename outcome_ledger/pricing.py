"""Illustrative USD / million-token rates; replace with your negotiated price table."""

PRICES = {"reasoner-mini": (1.0, 4.0), "reasoner-pro": (3.0, 12.0)}


def token_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    if model not in PRICES:
        raise ValueError(f"Unknown model: {model}")
    if min(input_tokens, output_tokens) < 0:
        raise ValueError("Token counts cannot be negative")
    input_rate, output_rate = PRICES[model]
    return round((input_tokens * input_rate + output_tokens * output_rate) / 1_000_000, 8)
