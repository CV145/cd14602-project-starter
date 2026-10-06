"""End-to-end integration tests for CLI quiz session workflow."""

import json
from unittest.mock import patch

import cli_frontend


def _assert_deck_stats(deck_stats: dict) -> None:
    """Verify persisted statistics for cards Q1, Q2, and Q3."""
    assert deck_stats["Q1"]["correct"] == 1
    assert deck_stats["Q1"]["incorrect"] == 0
    assert deck_stats["Q1"]["last_seen"] > 0
    assert deck_stats["Q2"]["correct"] == 0
    assert deck_stats["Q2"]["incorrect"] == 1
    assert deck_stats["Q2"]["last_seen"] > 0
    assert deck_stats["Q3"]["correct"] == 1
    assert deck_stats["Q3"]["incorrect"] == 0
    assert deck_stats["Q3"]["last_seen"] > 0

    # Edge Cases: Verifies all per-card counters.
    # Security Vulnerabilities: None.


def test_full_session(tmp_path, capsys):
    """Test full sequential session with scripted inputs and state."""
    # Arrange
    deck_path = tmp_path / "integration_deck.json"
    cards_data = [
        {"front": "Q1", "back": "A1"},
        {"front": "Q2", "back": "A2"},
        {"front": "Q3", "back": "A3"},
    ]
    deck_path.write_text(json.dumps(cards_data), encoding="utf-8")
    state_path = tmp_path / "quiz_state.json"
    args = [
        "-m", "sequential", "-f", str(deck_path), "--state", str(state_path)
    ]
    scripted_inputs = ["A1", "Wrong", "A3", "exit", "y"]

    # Act
    with patch("builtins.input", side_effect=scripted_inputs):
        exit_code = cli_frontend.main(args)
    captured = capsys.readouterr()

    # Assert
    assert exit_code == 0
    assert "Correct: 2" in captured.out
    assert "Incorrect: 1" in captured.out
    assert "66.7%" in captured.out
    saved_state = json.loads(state_path.read_text(encoding="utf-8"))
    _assert_deck_stats(saved_state["integration_deck"])

    # Edge Cases: End-to-end flow verifying disk persistence and statistics.
    # Security Vulnerabilities: None.
