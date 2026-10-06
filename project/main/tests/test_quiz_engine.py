"""Unit tests for QuizEngine orchestration, scoring, and persistence."""

from utils.quiz_engine import Card, QuizEngine, SequentialStrategy


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
