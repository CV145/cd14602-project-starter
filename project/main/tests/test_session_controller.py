"""Unit tests for SessionController Facade."""

import json
import pytest

from utils.session_controller import SessionController


def test_deck_validation_missing_file(tmp_path):
    """Test validation rejects non-existent deck file."""
    # Arrange
    missing_file = tmp_path / "nonexistent.json"
    state_file = tmp_path / "state.json"

    # Act & Assert
    with pytest.raises((FileNotFoundError, ValueError)):
        SessionController.validate_and_load_deck(
            deck_path=missing_file,
            state_path=state_file,
        )

    # Edge Cases: Missing path raises FileNotFoundError or ValueError.
    # Security Vulnerabilities: None.


def test_deck_validation_non_json_file(tmp_path):
    """Test validation rejects files not ending with .json."""
    # Arrange
    text_file = tmp_path / "deck.txt"
    text_file.write_text("front,back\n", encoding="utf-8")
    state_file = tmp_path / "state.json"

    # Act & Assert
    with pytest.raises(ValueError, match=r"\.json"):
        SessionController.validate_and_load_deck(
            deck_path=text_file,
            state_path=state_file,
        )

    # Edge Cases: Extension check is case-insensitive.
    # Security Vulnerabilities: None.


def test_deck_validation_file_over_1mb(tmp_path):
    """Test validation rejects files exceeding 1 MB limit."""
    # Arrange
    large_file = tmp_path / "large_deck.json"
    # Create file > 1MB (1,048,576 bytes)
    large_file.write_bytes(b" " * (1024 * 1024 + 10))
    state_file = tmp_path / "state.json"

    # Act & Assert
    with pytest.raises(ValueError, match="1 MB"):
        SessionController.validate_and_load_deck(
            deck_path=large_file,
            state_path=state_file,
        )

    # Edge Cases: Exactly 1MB boundary edge case.
    # Security Vulnerabilities: DoS via oversized file prevented.


def test_deck_validation_empty_deck(tmp_path):
    """Test validation rejects empty deck files."""
    # Arrange
    empty_file = tmp_path / "empty_deck.json"
    empty_file.write_text("[]", encoding="utf-8")
    state_file = tmp_path / "state.json"

    # Act & Assert
    with pytest.raises(ValueError, match="empty"):
        SessionController.validate_and_load_deck(
            deck_path=empty_file,
            state_path=state_file,
        )

    # Edge Cases: Valid JSON list with zero items rejected.
    # Security Vulnerabilities: None.


def test_deck_validation_settings_card_front(tmp_path):
    """Test validation rejects cards with front named '_settings'."""
    # Arrange
    bad_deck = tmp_path / "bad_deck.json"
    bad_cards = [{"front": "_settings", "back": "Reserved"}]
    bad_deck.write_text(json.dumps(bad_cards), encoding="utf-8")
    state_file = tmp_path / "state.json"

    # Act & Assert
    with pytest.raises(ValueError, match="_settings"):
        SessionController.validate_and_load_deck(
            deck_path=bad_deck,
            state_path=state_file,
        )

    # Edge Cases: Prevents collision with deck metadata key.
    # Security Vulnerabilities: None.


def test_deck_loading_duplicate_front_warning(tmp_path):
    """Test duplicate card fronts generate warning list."""
    # Arrange
    dup_deck = tmp_path / "dup_deck.json"
    dup_cards = [
        {"front": "Dup", "back": "Ans 1"},
        {"front": "Dup", "back": "Ans 2"},
        {"front": "Unique", "back": "Ans 3"},
    ]
    dup_deck.write_text(json.dumps(dup_cards), encoding="utf-8")
    state_file = tmp_path / "state.json"

    # Act
    cards, warnings = SessionController.validate_and_load_deck(
        deck_path=dup_deck,
        state_path=state_file,
    )

    # Assert
    assert len(cards) == 3
    assert any("Dup" in w for w in warnings)

    # Edge Cases: Duplicate cards kept; warning identifies duplicated front.
    # Security Vulnerabilities: None.


def test_latest_deck_discovery(tmp_path):
    """Test latest deck lookup selects non-upload deck with max last_seen."""
    # Arrange
    state_file = tmp_path / "quiz_state.json"
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    deck_old = data_dir / "deck_old.json"
    deck_new = data_dir / "deck_new.json"
    deck_old.write_text('[{"front": "O", "back": "A"}]', encoding="utf-8")
    deck_new.write_text('[{"front": "N", "back": "B"}]', encoding="utf-8")

    state_data = {
        "_active_session": {"deck": "ignored"},
        "deck_old": {"O": {"correct": 1, "incorrect": 0, "last_seen": 100.0}},
        "deck_new": {"N": {"correct": 1, "incorrect": 0, "last_seen": 200.0}},
        "upload:custom.json": {"C": {"correct": 1, "last_seen": 300.0}},
    }
    state_file.write_text(json.dumps(state_data), encoding="utf-8")

    # Act
    resolved = SessionController.get_latest_deck_path(
        state_path=state_file,
        data_dir=data_dir,
    )

    # Assert
    assert resolved == deck_new

    # Edge Cases: Ignores _active_session, _settings, and upload: decks.
    # Security Vulnerabilities: None.


def test_latest_deck_discovery_no_history(tmp_path):
    """Test latest deck lookup returns None when state has no valid deck."""
    # Arrange
    state_file = tmp_path / "quiz_state.json"
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    state_data = {
        "_active_session": {"deck": "ignored"},
        "upload:only_upload.json": {"C": {"last_seen": 300.0}},
    }
    state_file.write_text(json.dumps(state_data), encoding="utf-8")

    # Act
    resolved = SessionController.get_latest_deck_path(
        state_path=state_file,
        data_dir=data_dir,
    )

    # Assert
    assert resolved is None

    # Edge Cases: Upload-only decks treated as having no study history.
    # Security Vulnerabilities: None.


def test_process_input_empty_input(tmp_path):
    """Test empty and whitespace input returns empty status without penalty."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text('[{"front": "F", "back": "B"}]', encoding="utf-8")
    state_file = tmp_path / "state.json"
    controller = SessionController(deck_file, "sequential", state_file)

    # Act
    res_empty = controller.process_input("")
    res_spaces = controller.process_input("   \t  ")

    # Assert
    assert res_empty.status == "empty"
    assert res_spaces.status == "empty"
    assert controller.current_attempt == 1
    assert controller.engine.session_correct == 0
    assert controller.engine.session_incorrect == 0

    # Edge Cases: Tabs, spaces, and empty strings re-prompt cleanly.
    # Security Vulnerabilities: None.


def test_process_input_exit_command(tmp_path):
    """Test exit command is detected case-insensitively with whitespace."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text('[{"front": "F", "back": "B"}]', encoding="utf-8")
    state_file = tmp_path / "state.json"
    controller = SessionController(deck_file, "sequential", state_file)

    # Act
    result = controller.process_input("  EXIT  ")

    # Assert
    assert result.status == "exit"

    # Edge Cases: Whitespace trimmed and case folded.
    # Security Vulnerabilities: None.


def test_process_input_skip_command_sequential(tmp_path):
    """Test skip command records 1 incorrect and advances card."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text(
        '[{"front": "F1", "back": "B1"}, {"front": "F2", "back": "B2"}]',
        encoding="utf-8",
    )
    state_file = tmp_path / "state.json"
    controller = SessionController(deck_file, "sequential", state_file)

    # Act
    result = controller.process_input("skip")

    # Assert
    assert result.status == "skip"
    assert result.correct_answer == "B1"
    assert controller.engine.session_incorrect == 1
    assert controller.get_current_card().front == "F2"

    # Edge Cases: Skip reveals correct answer and advances.
    # Security Vulnerabilities: None.


def test_process_input_skip_command_adaptive(tmp_path):
    """Test skip in adaptive mode records fail count 2 to 5min queue."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text('[{"front": "F1", "back": "B1"}]', encoding="utf-8")
    state_file = tmp_path / "state.json"
    controller = SessionController(deck_file, "adaptive", state_file)

    # Act
    result = controller.process_input("skip")

    # Assert
    assert result.status == "skip"
    assert controller.engine.session_incorrect == 1
    strat = controller.engine.strategy
    assert any(c.front == "F1" for c in strat.queues["5min"])

    # Edge Cases: Skip routes card to Difficult (5min queue).
    # Security Vulnerabilities: None.


def test_process_input_adaptive_two_attempt_flow_success(tmp_path):
    """Test adaptive flow: wrong first try prompts retry, second try scores."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text('[{"front": "F1", "back": "Ans"}]', encoding="utf-8")
    state_file = tmp_path / "state.json"
    controller = SessionController(deck_file, "adaptive", state_file)

    # Act
    res1 = controller.process_input("Wrong")
    assert res1.status == "retry"
    assert controller.current_attempt == 2
    assert controller.engine.session_incorrect == 0

    res2 = controller.process_input("Ans")

    # Assert
    assert res2.status == "correct"
    assert controller.engine.session_correct == 1
    strat = controller.engine.strategy
    assert any(c.front == "F1" for c in strat.queues["10min"])

    # Edge Cases: 1 fail before success routes card to 10min queue.
    # Security Vulnerabilities: None.


def test_process_input_adaptive_two_attempt_flow_failure(tmp_path):
    """Test adaptive flow: two consecutive wrong answers record 1 incorrect."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text('[{"front": "F1", "back": "Ans"}]', encoding="utf-8")
    state_file = tmp_path / "state.json"
    controller = SessionController(deck_file, "adaptive", state_file)

    # Act
    res1 = controller.process_input("Wrong1")
    assert res1.status == "retry"
    res2 = controller.process_input("Wrong2")

    # Assert
    assert res2.status == "incorrect"
    assert res2.correct_answer == "Ans"
    assert controller.engine.session_incorrect == 1
    strat = controller.engine.strategy
    assert any(c.front == "F1" for c in strat.queues["5min"])

    # Edge Cases: 2 fails routes card to 5min queue.
    # Security Vulnerabilities: None.


def test_process_input_collision_handling_exit(tmp_path):
    """Test exit command collision grades answer and waits for confirmation."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text(
        '[{"front": "Type exit to test", "back": "exit"}]',
        encoding="utf-8",
    )
    state_file = tmp_path / "state.json"
    controller = SessionController(deck_file, "sequential", state_file)

    # Act
    res_coll = controller.process_input("exit")
    assert res_coll.status == "collision"
    assert res_coll.command == "exit"

    # Decline quit confirmation (chose 'n' -> wanted to submit 'exit' answer)
    res_declined = controller.resolve_collision(confirmed=False)

    # Assert
    assert res_declined.status == "correct"
    assert controller.engine.session_correct == 1

    # Edge Cases: Collision prompts confirmation before state mutation.
    # Security Vulnerabilities: None.


def test_process_input_collision_confirmed_exit(tmp_path):
    """Test confirming exit collision executes exit command without grading."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text(
        '[{"front": "Type exit to test", "back": "exit"}]',
        encoding="utf-8",
    )
    state_file = tmp_path / "state.json"
    controller = SessionController(deck_file, "sequential", state_file)

    # Act
    controller.process_input("exit")
    res_confirmed = controller.resolve_collision(confirmed=True)

    # Assert
    assert res_confirmed.status == "exit"
    assert controller.engine.session_correct == 0

    # Edge Cases: Confirmed exit aborts grading and leaves card unrecorded.
    # Security Vulnerabilities: None.


def test_active_session_persisted_after_recorded_outcome(tmp_path):
    """Test _active_session is written to quiz_state after recorded answer."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text(
        '[{"front": "F1", "back": "A1"}, {"front": "F2", "back": "A2"}]',
        encoding="utf-8",
    )
    state_file = tmp_path / "state.json"
    controller = SessionController(deck_file, "sequential", state_file)

    # Act
    controller.process_input("A1")

    # Assert
    saved_state = json.loads(state_file.read_text(encoding="utf-8"))
    assert "_active_session" in saved_state
    sess = saved_state["_active_session"]
    assert sess["deck_key"] == "deck"
    assert sess["session_correct"] == 1
    assert sess["current_front"] == "F2"
    assert sess["cards"] is None

    # Edge Cases: Saves active progress without losing existing deck history.
    # Security Vulnerabilities: None.


def test_active_session_persistence_for_upload_deck(tmp_path):
    """Test uploaded deck saves full card list in _active_session."""
    # Arrange
    deck_file = tmp_path / "upload_sample.json"
    cards_json = '[{"front": "UpF", "back": "UpB"}]'
    deck_file.write_text(cards_json, encoding="utf-8")
    state_file = tmp_path / "state.json"
    controller = SessionController(
        f"upload:{deck_file}", "sequential", state_file
    )

    # Act
    controller.process_input("UpB")

    # Assert
    saved_state = json.loads(state_file.read_text(encoding="utf-8"))
    sess = saved_state["_active_session"]
    assert sess["deck_key"] == f"upload:{deck_file.name}"
    assert sess["cards"] == [{"front": "UpF", "back": "UpB"}]

    # Edge Cases: Serializes cards so uploaded decks resume without files.
    # Security Vulnerabilities: None.


def test_resume_sequential_session(tmp_path):
    """Test resuming sequential session at saved card and score."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text(
        '[{"front": "F1", "back": "A1"}, {"front": "F2", "back": "A2"}]',
        encoding="utf-8",
    )
    state_file = tmp_path / "state.json"
    active_sess = {
        "deck_key": "deck",
        "source": str(deck_file),
        "cards": None,
        "mode": "sequential",
        "session_correct": 5,
        "session_incorrect": 2,
        "current_front": "F2",
        "attempt": 1,
    }
    state_file.write_text(
        json.dumps({"_active_session": active_sess}), encoding="utf-8"
    )

    # Act
    controller = SessionController(deck_file, "sequential", state_file)
    resumed = controller.resume_active_session()

    # Assert
    assert resumed is True
    assert controller.get_current_card().front == "F2"
    assert controller.engine.session_correct == 5
    assert controller.engine.session_incorrect == 2

    # Edge Cases: Fast-forwards sequential index to target card front.
    # Security Vulnerabilities: None.


def test_resume_adaptive_session(tmp_path):
    """Test resuming adaptive session restores queues and timestamps."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text(
        '[{"front": "F1", "back": "A1"}, {"front": "F2", "back": "A2"}]',
        encoding="utf-8",
    )
    state_file = tmp_path / "state.json"
    active_sess = {
        "deck_key": "deck",
        "source": str(deck_file),
        "cards": None,
        "mode": "adaptive",
        "session_correct": 1,
        "session_incorrect": 0,
        "current_front": "F2",
        "attempt": 1,
        "queues": {"new": ["F2"], "5min": ["F1"], "10min": [], "15min": []},
        "fails": {"F1": 2},
        "timestamps": {"F1": 1500.0},
    }
    state_file.write_text(
        json.dumps({"_active_session": active_sess}), encoding="utf-8"
    )

    # Act
    controller = SessionController(deck_file, "adaptive", state_file)
    resumed = controller.resume_active_session()

    # Assert
    assert resumed is True
    strat = controller.engine.strategy
    assert any(c.front == "F1" for c in strat.queues["5min"])
    assert strat._fails.get("F1") == 2

    # Edge Cases: Queue membership and failure count restored.
    # Security Vulnerabilities: None.


def test_discard_active_session_on_missing_target(tmp_path):
    """Test resume discards session if target card is missing from deck."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text('[{"front": "F1", "back": "A1"}]', encoding="utf-8")
    state_file = tmp_path / "state.json"
    active_sess = {
        "deck_key": "deck",
        "source": str(deck_file),
        "cards": None,
        "mode": "sequential",
        "current_front": "MissingFront",
    }
    state_file.write_text(
        json.dumps({"_active_session": active_sess}), encoding="utf-8"
    )

    # Act
    controller = SessionController(deck_file, "sequential", state_file)
    resumed = controller.resume_active_session()

    # Assert
    assert resumed is False
    saved = json.loads(state_file.read_text(encoding="utf-8"))
    assert "_active_session" not in saved

    # Edge Cases: Purges invalid active session and returns False.
    # Security Vulnerabilities: None.


def test_custom_intervals_saved_and_loaded(tmp_path):
    """Test saving and retrieving custom queue intervals in deck settings."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text('[{"front": "F", "back": "B"}]', encoding="utf-8")
    state_file = tmp_path / "state.json"
    controller = SessionController(deck_file, "adaptive", state_file)

    # Act
    custom = {"5min": 60.0, "10min": 120.0, "15min": 180.0}
    controller.set_custom_intervals(custom)
    loaded = controller.get_custom_intervals()

    # Assert
    assert loaded == custom
    saved = json.loads(state_file.read_text(encoding="utf-8"))
    assert saved["deck"]["_settings"]["intervals"] == custom

    # Edge Cases: Preserves non-default intervals under deck settings.
    # Security Vulnerabilities: None.


def test_reset_deck_progress_preserves_settings_and_clears_active_session(
    tmp_path,
):
    """Test reset progress purges card stats while keeping settings intact."""
    # Arrange
    deck_file = tmp_path / "deck.json"
    deck_file.write_text('[{"front": "F", "back": "B"}]', encoding="utf-8")
    state_file = tmp_path / "state.json"
    state_data = {
        "_active_session": {"deck_key": "deck"},
        "deck": {
            "_settings": {"intervals": {"5min": 100.0}},
            "F": {"correct": 3, "incorrect": 1, "last_seen": 10.0},
        },
    }
    state_file.write_text(json.dumps(state_data), encoding="utf-8")
    controller = SessionController(deck_file, "sequential", state_file)

    # Act
    controller.reset_deck_progress()

    # Assert
    saved = json.loads(state_file.read_text(encoding="utf-8"))
    assert "_active_session" not in saved
    assert "F" not in saved["deck"]
    assert saved["deck"]["_settings"]["intervals"]["5min"] == 100.0

    # Edge Cases: Reset preserves interval settings while clearing card data.
    # Security Vulnerabilities: None.
