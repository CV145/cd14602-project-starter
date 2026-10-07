import json
import time
from unittest.mock import patch

import pytest

from utils.quiz_engine import (
    AdaptiveStrategy,
    Card,
    QuizEngine,
    SequentialStrategy,
    StateFileError,
)


def test_quiz_engine_session_score_tracking(tmp_path):
    """Test QuizEngine tracks session correct and incorrect attempts."""
    # Arrange
    card = Card("Python?", "Language")
    strategy = SequentialStrategy([card])
    state_file = tmp_path / "quiz_state.json"
    engine = QuizEngine(
        cards=[card],
        strategy=strategy,
        deck_name="sample",
        state_path=state_file,
    )

    # Act
    first_result = engine.answer_current_card("Language")
    second_result = engine.answer_current_card("Wrong")

    # Assert
    assert first_result is True
    assert second_result is False
    assert engine.session_correct == 1
    assert engine.session_incorrect == 1

    # Edge Cases: None (Handled by Card answer normalization).
    # Security Vulnerabilities: None.


def test_quiz_engine_auto_initializes_missing_state_file(tmp_path):
    """Test QuizEngine creates empty state file if none exists."""
    # Arrange
    card = Card("Front", "Back")
    strategy = SequentialStrategy([card])
    non_existent_state = tmp_path / "nested" / "quiz_state.json"

    # Act
    engine = QuizEngine(
        cards=[card],
        strategy=strategy,
        deck_name="test_deck",
        state_path=non_existent_state,
    )

    # Assert
    assert non_existent_state.exists()
    assert engine.state == {}

    # Edge Cases: Missing parent directories are created automatically.
    # Security Vulnerabilities: None.


def test_quiz_engine_lifetime_accuracy_zero_attempts(tmp_path):
    """Test get_lifetime_accuracy returns 0.0 when no attempts recorded."""
    # Arrange
    card = Card("Front", "Back")
    strategy = SequentialStrategy([card])
    state_file = tmp_path / "quiz_state.json"
    engine = QuizEngine(
        cards=[card],
        strategy=strategy,
        deck_name="sample",
        state_path=state_file,
    )

    # Act
    accuracy = engine.get_lifetime_accuracy()

    # Assert
    assert accuracy == 0.0

    # Edge Cases: Zero total attempts safely returns 0.0 instead of dividing.
    # Security Vulnerabilities: None.


def test_quiz_engine_lifetime_accuracy_calculation(tmp_path):
    """Test calculation of lifetime accuracy percentage from attempts."""
    # Arrange
    card = Card("Front", "Back")
    strategy = SequentialStrategy([card])
    state_file = tmp_path / "quiz_state.json"
    engine = QuizEngine(
        cards=[card],
        strategy=strategy,
        deck_name="sample",
        state_path=state_file,
    )

    # Act
    engine.answer_current_card("Back")
    engine.answer_current_card("Back")
    engine.answer_current_card("Back")
    engine.answer_current_card("Wrong")
    accuracy = engine.get_lifetime_accuracy()

    # Assert
    assert accuracy == 75.0

    # Edge Cases: None.
    # Security Vulnerabilities: None.


def test_quiz_engine_raises_state_file_error_on_invalid_json(tmp_path):
    """Test StateFileError captures file path, line, and column."""
    # Arrange
    state_file = tmp_path / "corrupt_state.json"
    state_file.write_text('{\n  "bad": json\n}', encoding="utf-8")
    card = Card("Front", "Back")
    strategy = SequentialStrategy([card])

    # Act & Assert
    with pytest.raises(StateFileError) as exc_info:
        QuizEngine(
            cards=[card],
            strategy=strategy,
            deck_name="sample",
            state_path=state_file,
        )

    assert exc_info.value.path == state_file
    assert exc_info.value.line == 2
    assert exc_info.value.column == 10

    # Edge Cases: Malformed JSON with exact line and column captured.
    # Security Vulnerabilities: None.


def test_quiz_engine_grade_current_card_without_advancing(tmp_path):
    """Test grade_current_card evaluates answer without side effects."""
    # Arrange
    card1 = Card("Front 1", "Back 1")
    card2 = Card("Front 2", "Back 2")
    strategy = SequentialStrategy([card1, card2])
    state_file = tmp_path / "quiz_state.json"
    engine = QuizEngine(
        cards=[card1, card2],
        strategy=strategy,
        deck_name="sample",
        state_path=state_file,
    )

    # Act
    is_correct_true = engine.grade_current_card("Back 1")
    is_correct_false = engine.grade_current_card("Wrong")

    # Assert
    assert is_correct_true is True
    assert is_correct_false is False
    assert engine.session_correct == 0
    assert engine.session_incorrect == 0
    assert engine._current_card == card1
    assert engine.state.get("sample", {}) == {}

    # Edge Cases: Multiple grading calls do not advance current card.
    # Security Vulnerabilities: None.


def test_quiz_engine_record_result_updates_metrics_and_advances(tmp_path):
    """Test record_result updates metrics, timestamps, and advances card."""
    # Arrange
    card1 = Card("Front 1", "Back 1")
    card2 = Card("Front 2", "Back 2")
    strategy = SequentialStrategy([card1, card2])
    state_file = tmp_path / "quiz_state.json"
    engine = QuizEngine(
        cards=[card1, card2],
        strategy=strategy,
        deck_name="sample",
        state_path=state_file,
    )
    engine.grade_current_card("Back 1")

    # Act
    before_time = time.time()
    engine.record_result(is_correct=True, fails=0)
    after_time = time.time()

    # Assert
    assert engine.session_correct == 1
    assert engine.session_incorrect == 0
    assert engine._current_card == card2
    deck_stats = engine.state["sample"]["Front 1"]
    assert deck_stats["correct"] == 1
    assert deck_stats["incorrect"] == 0
    assert before_time <= deck_stats["last_seen"] <= after_time

    # Edge Cases: Card state persisted to file with valid timestamp.
    # Security Vulnerabilities: None.


def test_quiz_engine_answer_current_card_single_attempt_wrapper(tmp_path):
    """Test answer_current_card preserves one-attempt functionality."""
    # Arrange
    card1 = Card("Front 1", "Back 1")
    card2 = Card("Front 2", "Back 2")
    strategy = SequentialStrategy([card1, card2])
    state_file = tmp_path / "quiz_state.json"
    engine = QuizEngine(
        cards=[card1, card2],
        strategy=strategy,
        deck_name="sample",
        state_path=state_file,
    )

    # Act
    result = engine.answer_current_card("Back 1")

    # Assert
    assert result is True
    assert engine.session_correct == 1
    assert engine._current_card == card2
    assert engine.state["sample"]["Front 1"]["correct"] == 1

    # Edge Cases: Wrapper grades, records, and advances in one step.
    # Security Vulnerabilities: None.


def test_quiz_engine_save_state_propagates_oserror(tmp_path):
    """Test _save_state propagates OSError instead of swallowing it."""
    # Arrange
    card = Card("Front", "Back")
    strategy = SequentialStrategy([card])
    state_file = tmp_path / "quiz_state.json"
    engine = QuizEngine(
        cards=[card],
        strategy=strategy,
        deck_name="sample",
        state_path=state_file,
    )

    # Act & Assert
    with patch("builtins.open", side_effect=OSError("Disk full")):
        with pytest.raises(OSError):
            engine._save_state()

    # Edge Cases: Filesystem failures propagated to caller.
    # Security Vulnerabilities: None.


def test_adaptive_explicit_fail_counts():
    """Test record_attempt routes fail counts: 0->15m, 1->10m, 2->5m."""
    # Arrange
    c0 = Card("F0", "B0")
    c1 = Card("F1", "B1")
    c2 = Card("F2", "B2")
    strat = AdaptiveStrategy([c0, c1, c2])

    # Act
    strat.record_attempt(c0, fails=0)
    strat.record_attempt(c1, fails=1)
    strat.record_attempt(c2, fails=2)

    # Assert
    assert c0 in strat.queues["15min"]
    assert c1 in strat.queues["10min"]
    assert c2 in strat.queues["5min"]

    # Edge Cases: Explicit integer fail count parameter overrides bool.
    # Security Vulnerabilities: None.


def test_adaptive_due_time_filtering():
    """Test get_next_card filters cards by elapsed interval."""
    # Arrange
    c_due = Card("F_due", "B_due")
    c_not_due = Card("F_not_due", "B_not_due")
    now = 1000.0
    strat = AdaptiveStrategy([], time_provider=lambda: now)
    strat.queues["5min"].extend([c_due, c_not_due])
    strat.card_timestamps[c_due.front] = now - 350.0
    strat.card_timestamps[c_not_due.front] = now - 100.0

    # Act
    served_card = strat.get_next_card()
    next_served = strat.get_next_card()

    # Assert
    assert served_card == c_due
    assert next_served is None

    # Edge Cases: Non-due cards remain in queue until interval elapses.
    # Security Vulnerabilities: None.


def test_adaptive_seconds_until_next_due():
    """Test seconds_until_next_due returns remaining seconds or None."""
    # Arrange
    card = Card("F", "B")
    now = 1000.0
    strat = AdaptiveStrategy([], time_provider=lambda: now)
    strat.queues["5min"].append(card)
    strat.card_timestamps[card.front] = now - 100.0

    # Act
    rem_sec = strat.seconds_until_next_due()
    empty_strat = AdaptiveStrategy([])
    empty_rem = empty_strat.seconds_until_next_due()

    # Assert
    assert rem_sec == 200.0
    assert empty_rem is None

    # Edge Cases: Empty strategy returns None; waiting card returns delta.
    # Security Vulnerabilities: None.


def test_adaptive_serialization_roundtrip():
    """Test to_dict and from_dict roundtrip queues and timestamps."""
    # Arrange
    c1 = Card("Front 1", "Back 1")
    c2 = Card("Front 2", "Back 2")
    now = 1000.0
    strat = AdaptiveStrategy([c1, c2], time_provider=lambda: now)
    strat.record_attempt(c1, fails=0)
    strat.record_attempt(c2, fails=1)

    # Act
    data = strat.to_dict()
    new_strat = AdaptiveStrategy([c1, c2], time_provider=lambda: now)
    new_strat.from_dict(data)

    # Assert
    assert c1 in new_strat.queues["15min"]
    assert c2 in new_strat.queues["10min"]
    assert new_strat.card_timestamps == strat.card_timestamps

    # Edge Cases: Queue membership and timestamp dictionaries restored.
    # Security Vulnerabilities: None.


def test_quiz_engine_ignores_reserved_keys_in_stats(tmp_path):
    """Test get_lifetime_accuracy ignores _settings key inside deck."""
    # Arrange
    state_file = tmp_path / "quiz_state.json"
    state_content = {
        "_active_session": {"deck_key": "sample"},
        "sample": {
            "_settings": {"intervals": {"5min": 300}},
            "Card 1": {"correct": 2, "incorrect": 1, "last_seen": 100.0},
        },
    }
    state_file.write_text(json.dumps(state_content), encoding="utf-8")
    card = Card("Card 1", "Back 1")
    engine = QuizEngine(
        cards=[card],
        strategy=SequentialStrategy([card]),
        deck_name="sample",
        state_path=state_file,
    )

    # Act
    accuracy = engine.get_lifetime_accuracy()

    # Assert
    assert abs(accuracy - 66.66666666666667) < 0.01

    # Edge Cases: Ignores _settings dictionary inside deck stats.
    # Security Vulnerabilities: None.


def test_quiz_engine_get_all_decks_stats(tmp_path):
    """Test get_all_decks_stats aggregates standard and upload decks."""
    # Arrange
    state_file = tmp_path / "quiz_state.json"
    state_content = {
        "_active_session": {"deck_key": "deck1"},
        "deck1": {
            "_settings": {"intervals": {"5min": 300}},
            "Q1": {"correct": 3, "incorrect": 1, "last_seen": 100.0},
        },
        "upload:custom.json": {
            "Q2": {"correct": 1, "incorrect": 1, "last_seen": 105.0},
        },
    }
    state_file.write_text(json.dumps(state_content), encoding="utf-8")
    card = Card("Q1", "A1")
    engine = QuizEngine(
        cards=[card],
        strategy=SequentialStrategy([card]),
        deck_name="deck1",
        state_path=state_file,
    )

    # Act
    stats = engine.get_all_decks_stats()

    # Assert
    assert stats["total_correct"] == 4
    assert stats["total_attempts"] == 6
    assert abs(stats["accuracy"] - 66.66666666666667) < 0.01

    # Edge Cases: Skips top-level _active_session and deck-level _settings.
    # Security Vulnerabilities: None.


def test_quiz_engine_get_all_decks_stats_empty(tmp_path):
    """Test get_all_decks_stats handles state with no cards gracefully."""
    # Arrange
    state_file = tmp_path / "quiz_state.json"
    state_content = {"_active_session": {}}
    state_file.write_text(json.dumps(state_content), encoding="utf-8")
    card = Card("Q1", "A1")
    engine = QuizEngine(
        cards=[card],
        strategy=SequentialStrategy([card]),
        deck_name="deck1",
        state_path=state_file,
    )

    # Act
    stats = engine.get_all_decks_stats()

    # Assert
    assert stats["total_correct"] == 0
    assert stats["total_attempts"] == 0
    assert stats["accuracy"] == 0.0

    # Edge Cases: Empty history returns zero counts and 0.0% accuracy.
    # Security Vulnerabilities: None.
