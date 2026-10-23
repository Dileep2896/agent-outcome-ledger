"""Explicit demo identity policy: CRM tags are aliases; dots remain significant."""

import re
from collections.abc import Callable


def helpdesk(key: str) -> str | None:
    match = re.fullmatch(r"(?:HS-|ticket:)(\d+)", key.strip(), re.IGNORECASE)
    return f"ticket:{int(match[1])}" if match else None


def billing(key: str) -> str | None:
    match = re.fullmatch(r"(?:INV-\d{4}-|invoice:)(\d+)", key.strip(), re.IGNORECASE)
    return f"invoice:{int(match[1])}" if match else None


def crm(key: str) -> str | None:
    key = key.strip().lower().removeprefix("lead:")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", key):
        return None
    local, domain = key.split("@")
    local = local.split("+")[0]
    return f"lead:{local}@{domain}" if local else None


NORMALIZERS: dict[str, Callable[[str], str | None]] = {
    "helpdesk": helpdesk,
    "billing": billing,
    "crm": crm,
}


def normalize_entity(key: str) -> str | None:
    prefix = key.split(":", 1)[0].lower()
    normalizer = {"ticket": helpdesk, "invoice": billing, "lead": crm}.get(prefix)
    return normalizer(key) if normalizer else None
