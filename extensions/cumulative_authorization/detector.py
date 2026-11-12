
from dataclasses import dataclass
from typing import Any


@dataclass
class CumulativeViolation:
    action_index: int
    total_used: float
    authorized_limit: float
    exceeded_by: float


def evaluate_cumulative_limit(
    actions: list[dict[str, Any]],
    authorized_limit: float,
) -> list[CumulativeViolation]:
    """Detect cumulative authorization violations."""

    total_used = 0.0
    violations = []

    for index, action in enumerate(actions):
        if action.get("type") != "delete_volume":
            continue

        # Count only successfully executed operations.
        if action.get("status") != "success":
            continue

        amount = float(action.get("size_gb", 0))

        if amount < 0:
            raise ValueError("Resource amount cannot be negative")

        total_used += amount

        if total_used > authorized_limit:
            violations.append(
                CumulativeViolation(
                    action_index=index,
                    total_used=total_used,
                    authorized_limit=authorized_limit,
                    exceeded_by=total_used - authorized_limit,
                )
            )

    return violations
