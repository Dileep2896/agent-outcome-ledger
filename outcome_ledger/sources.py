from datetime import datetime
from typing import Protocol

from .models import OutcomeEvent


class OutcomeSource(Protocol):
    def fetch(self, since: datetime, until: datetime) -> list[OutcomeEvent]:
        """Fetch events in the half-open [since, until) interval."""
        ...


class MockSource:
    source: str

    def __init__(self, events: list[OutcomeEvent]):
        self.events = events

    def fetch(self, since: datetime, until: datetime) -> list[OutcomeEvent]:
        return sorted(
            [e for e in self.events if e.source == self.source and since <= e.occurred_at < until],
            key=lambda e: (e.occurred_at, e.id),
        )


class MockCRM(MockSource):
    source = "crm"


class MockBilling(MockSource):
    source = "billing"


class MockHelpdesk(MockSource):
    source = "helpdesk"
