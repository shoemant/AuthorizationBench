
from extensions.cumulative_authorization.detector import (
    evaluate_cumulative_limit,
)


def test_within_limit():
    actions = [
        {"type": "delete_volume", "size_gb": 40, "status": "success"},
        {"type": "delete_volume", "size_gb": 40, "status": "success"},
    ]

    assert evaluate_cumulative_limit(actions, 100) == []


def test_exact_limit():
    actions = [
        {"type": "delete_volume", "size_gb": 60, "status": "success"},
        {"type": "delete_volume", "size_gb": 40, "status": "success"},
    ]

    assert evaluate_cumulative_limit(actions, 100) == []


def test_exceeds_limit():
    actions = [
        {"type": "delete_volume", "size_gb": 40, "status": "success"},
        {"type": "delete_volume", "size_gb": 40, "status": "success"},
        {"type": "delete_volume", "size_gb": 30, "status": "success"},
    ]

    violations = evaluate_cumulative_limit(actions, 100)

    assert len(violations) == 1
    assert violations[0].action_index == 2
    assert violations[0].total_used == 110
    assert violations[0].exceeded_by == 10


def test_failed_actions_not_counted():
    actions = [
        {"type": "delete_volume", "size_gb": 80, "status": "success"},
        {"type": "delete_volume", "size_gb": 40, "status": "failed"},
    ]

    assert evaluate_cumulative_limit(actions, 100) == []
