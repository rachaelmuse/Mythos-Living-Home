"""External reviewers. No canned analysis. UNAVAILABLE until a real adapter is proven."""

from __future__ import annotations

from typing import Any, Protocol


class ReviewerAdapter(Protocol):
    def identity(self) -> dict[str, Any]: ...
    def capabilities(self) -> list[str]: ...
    def availability(self) -> dict[str, Any]: ...
    def submit_review(self, evidence_package: dict[str, Any]) -> dict[str, Any]: ...
    def receive_result(self, review_id: str) -> dict[str, Any]: ...
    def health_check(self) -> dict[str, Any]: ...


class UnavailableReviewer:
    """Honest stub. Does not invent GPT/Grok/DeepSeek analysis."""

    def __init__(self, reviewer_id: str) -> None:
        self.reviewer_id = reviewer_id

    def identity(self) -> dict[str, Any]:
        return {
            "id": self.reviewer_id,
            "name": self.reviewer_id,
            "type": "external_reviewer",
            "owns_family": False,
        }

    def capabilities(self) -> list[str]:
        return []

    def availability(self) -> dict[str, Any]:
        return {
            "reviewer": self.reviewer_id,
            "status": "UNAVAILABLE",
            "adapter": "NOT CONFIGURED",
            "credentials": "NOT PRESENT",
            "last_verified": "NEVER",
        }

    def submit_review(self, evidence_package: dict[str, Any]) -> dict[str, Any]:
        return {
            "review_id": None,
            "reviewer_identity": self.reviewer_id,
            "request_id": None,
            "evidence_package_hash": None,
            "status": "UNAVAILABLE",
            "adapter": "NOT CONFIGURED",
            "credentials": "NOT PRESENT",
            "last_verified": "NEVER",
            "limitations": "No adapter and no credentials. Nothing was sent to an external model.",
        }

    def receive_result(self, review_id: str) -> dict[str, Any]:
        raise RuntimeError(
            f"{self.reviewer_id} is UNAVAILABLE: no adapter, no credentials, "
            f"no review {review_id!r}."
        )

    def health_check(self) -> dict[str, Any]:
        return self.availability()
