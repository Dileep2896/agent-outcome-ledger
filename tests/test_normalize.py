import pytest

from outcome_ledger.normalize import NORMALIZERS, normalize_entity


@pytest.mark.parametrize(
    ("source", "raw", "expected"),
    [
        ("helpdesk", "HS-10293", "ticket:10293"),
        ("helpdesk", "ticket:10293", "ticket:10293"),
        ("crm", "Dana.Lee+promo@Example.com", "lead:dana.lee@example.com"),
        ("crm", "lead:Dana.Lee@Example.com", "lead:dana.lee@example.com"),
        ("billing", "INV-2026-00417", "invoice:417"),
        ("billing", "invoice:00417", "invoice:417"),
        ("helpdesk", "bad-key", None),
        ("billing", "INV-417", None),
        ("crm", "not-an-email", None),
    ],
)
def test_source_keys(source, raw, expected):
    assert NORMALIZERS[source](raw) == expected


def test_agent_key_is_normalized():
    assert normalize_entity("lead:Dana+work@Example.com") == "lead:dana@example.com"


def test_different_domains_stay_distinct():
    assert NORMALIZERS["crm"]("a@one.test") != NORMALIZERS["crm"]("a@two.test")
